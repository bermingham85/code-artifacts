"""
supervisor.py — Apex Watchdog Supervisor
Ref:        APEX-MB-PY-00009
Version:    1.0
Author:     MB / SYS
Description: Watchdog process that monitors both Apex and ClaudeClaw health every 60 seconds.
             Checks: foreman heartbeat, ClaudeClaw HTTP health, dead letter count,
             disk space, n8n reachability. Attempts ClaudeClaw restart on failure.
             Logs to apex/logs/supervisor.log.

Usage:
    python supervisor\supervisor.py           # Run continuously
    python supervisor\supervisor.py --check   # Single check, exit
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


APEX_ROOT       = Path(__file__).parent.parent
LOGS_DIR        = APEX_ROOT / "logs"
LOG_FILE        = LOGS_DIR / "supervisor.log"
HUB_DIR         = APEX_ROOT / "hub"
HEARTBEAT_FILE  = HUB_DIR / ".heartbeat"
DEAD_LETTER_DIR = HUB_DIR / "dead_letter"

CLAUDECLAW_DIR      = Path(r"C:\Users\bermi\Projects\claudeclaw")
CLAUDECLAW_HEALTH   = "http://localhost:3000/health"
N8N_URL             = "http://192.168.50.246:5678"
TELEGRAM_BOT_TOKEN  = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID    = os.environ.get("ALLOWED_CHAT_IDS", "").split(",")[0].strip()

HEARTBEAT_MAX_AGE_S = 120
DEAD_LETTER_LIMIT   = 10
DISK_FREE_MIN_GB    = 5
CHECK_INTERVAL_S    = 60


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOGS_DIR.mkdir(parents=True, exist_ok=True)

def _log(level: str, msg: str):
    line = f"{_now_iso()} [{level}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Telegram alert
# ---------------------------------------------------------------------------
def _send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        _log("WARN", "Telegram not configured — cannot send alert")
        return
    try:
        payload = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": f"[Apex Supervisor] {message}"}).encode()
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
        _log("INFO", f"Telegram alert sent: {message[:100]}")
    except Exception as e:
        _log("WARN", f"Telegram alert failed: {e}")


def _write_diagnostic(message: str, severity: str = "WARN"):
    """Drop a supervisor DiagnosticTicket into hub/ for n8n routing."""
    import uuid
    ticket = {
        "meta": {
            "ticket_id":     str(uuid.uuid4()),
            "ref_code":      "APEX-SYS-WF-00000",
            "parent_job_id": "supervisor",
            "created_at":    _now_iso(),
            "severity":      severity,
            "receiver":      "originator",
        },
        "failure": {
            "stage":      "SUPERVISOR",
            "error_type": "SupervisorAlert",
            "message":    message,
            "traceback":  "",
        },
        "resolution": {
            "suggested_action": "Check supervisor.log and relevant component",
            "auto_retry":       False,
            "retry_count":      0,
            "resolved":         False,
            "resolved_at":      None,
        },
    }
    ticket_path = HUB_DIR / f"DIAG-supervisor-{ticket['meta']['ticket_id'][:8]}.json"
    HUB_DIR.mkdir(parents=True, exist_ok=True)
    ticket_path.write_text(json.dumps(ticket, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_foreman_heartbeat() -> dict:
    """Check .heartbeat file age."""
    if not HEARTBEAT_FILE.exists():
        msg = "Foreman heartbeat missing — foreman may not have run yet"
        _log("WARN", msg)
        _write_diagnostic(msg, severity="WARN")
        return {"status": "WARN", "reason": msg}

    age = int(time.time() - HEARTBEAT_FILE.stat().st_mtime)
    if age > HEARTBEAT_MAX_AGE_S:
        msg = f"Foreman heartbeat stale: {age}s old (threshold {HEARTBEAT_MAX_AGE_S}s)"
        _log("WARN", msg)
        _write_diagnostic(msg, severity="WARN")
        return {"status": "WARN", "age_seconds": age}

    return {"status": "OK", "age_seconds": age}


def check_claudeclaw_health() -> dict:
    """GET /health from ClaudeClaw. Attempt restart if unreachable."""
    try:
        req = urllib.request.Request(CLAUDECLAW_HEALTH, method="GET")
        urllib.request.urlopen(req, timeout=5)
        return {"status": "OK"}
    except Exception as e:
        msg = f"ClaudeClaw health check failed: {e}"
        _log("WARN", msg)
        # Attempt restart
        if CLAUDECLAW_DIR.exists():
            _log("INFO", "Attempting ClaudeClaw restart...")
            try:
                subprocess.Popen(
                    ["npm", "start"],
                    cwd=str(CLAUDECLAW_DIR),
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                _log("INFO", "ClaudeClaw restart triggered")
                return {"status": "RESTARTED", "reason": msg}
            except Exception as restart_err:
                _log("ERROR", f"ClaudeClaw restart failed: {restart_err}")
                return {"status": "ERROR", "reason": msg, "restart_error": str(restart_err)}
        return {"status": "UNREACHABLE", "reason": msg}


def check_dead_letter() -> dict:
    """Count dead letter queue files."""
    if not DEAD_LETTER_DIR.exists():
        return {"status": "OK", "count": 0}
    count = len(list(DEAD_LETTER_DIR.glob("*.json")))
    if count >= DEAD_LETTER_LIMIT:
        msg = f"Dead letter queue has {count} items (limit {DEAD_LETTER_LIMIT}) — manual review needed"
        _log("WARN", msg)
        _send_telegram(msg)
        return {"status": "WARN", "count": count}
    return {"status": "OK", "count": count}


def check_disk_space() -> dict:
    """Check C: drive free space."""
    import shutil
    try:
        total, used, free = shutil.disk_usage("C:\\")
        free_gb = round(free / 1024**3, 2)
        if free_gb < DISK_FREE_MIN_GB:
            msg = f"Low disk space: {free_gb}GB free on C: (threshold {DISK_FREE_MIN_GB}GB)"
            _log("WARN", msg)
            _send_telegram(msg)
            return {"status": "WARN", "free_gb": free_gb}
        return {"status": "OK", "free_gb": free_gb}
    except Exception as e:
        return {"status": "ERROR", "reason": str(e)}


def check_n8n() -> dict:
    """HTTP GET to n8n to verify reachability."""
    try:
        req = urllib.request.Request(N8N_URL, method="GET")
        urllib.request.urlopen(req, timeout=5)
        return {"status": "OK"}
    except Exception as e:
        msg = f"n8n unreachable at {N8N_URL}: {e}"
        _log("WARN", msg)
        return {"status": "UNREACHABLE", "reason": msg}


# ---------------------------------------------------------------------------
# Full check cycle
# ---------------------------------------------------------------------------

def run_checks() -> dict:
    results = {
        "timestamp":          _now_iso(),
        "foreman_heartbeat":  check_foreman_heartbeat(),
        "claudeclaw_health":  check_claudeclaw_health(),
        "dead_letter":        check_dead_letter(),
        "disk_space":         check_disk_space(),
        "n8n":                check_n8n(),
    }

    statuses = [v.get("status", "OK") for v in results.values() if isinstance(v, dict)]
    overall = "ERROR" if "ERROR" in statuses else ("WARN" if any(
        s in statuses for s in ["WARN", "UNREACHABLE", "RESTARTED"]) else "OK")
    results["overall"] = overall

    _log("INFO", f"Health check complete: {overall}")
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Apex Supervisor Watchdog")
    parser.add_argument("--check", action="store_true", help="Single health check then exit")
    args = parser.parse_args()

    if args.check:
        results = run_checks()
        print(json.dumps(results, indent=2))
        sys.exit(0)

    _log("INFO", "Supervisor started — checking every 60s (Ctrl+C to stop)")
    try:
        while True:
            run_checks()
            time.sleep(CHECK_INTERVAL_S)
    except KeyboardInterrupt:
        _log("INFO", "Supervisor stopped")


if __name__ == "__main__":
    main()
