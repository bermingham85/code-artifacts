"""
APEX PH-08 - Supervisor Watchdog
Monitors: supervisor.py daemon, claudeclaw node process, n8n health
Restarts dead processes and sends Telegram alerts via ClaudeClaw ticket server.

Usage:
  python watchdog.py          # one watchdog cycle (restart dead + alert)
  python watchdog.py --check  # check-only, exit 0=all OK / 1=something down

Scheduled via Windows Task Scheduler every 5 min (see run_watchdog.bat).
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
APEX_ROOT      = Path(r"C:\Users\bermi\Projects\apex")
CLAUDECLAW_DIR = Path(r"C:\Users\bermi\Projects\claudeclaw")
LOG_FILE       = APEX_ROOT / "logs" / "watchdog.log"
STATE_FILE     = APEX_ROOT / "watchdog_state.json"

SUPERVISOR_CMD = [sys.executable, str(APEX_ROOT / "supervisor" / "supervisor.py")]
CLAUDECLAW_CMD = ["node", str(CLAUDECLAW_DIR / "src" / "index.js")]

N8N_HEALTH_URL  = "http://192.168.50.246:5678/healthz"
TICKET_URL      = "http://localhost:3000/internal/ticket"

PROCESSES = {
    "supervisor": {
        "cmd":        SUPERVISOR_CMD,
        "match_str":  "supervisor.py",
        "cwd":        str(APEX_ROOT / "supervisor"),
    },
    "claudeclaw": {
        "cmd":        CLAUDECLAW_CMD,
        "match_str":  "claudeclaw",          # matches the cwd path in wmic output
        "cwd":        str(CLAUDECLAW_DIR),
    },
}

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("watchdog")


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def find_process(match_str: str) -> bool:
    """Return True if any running process command line contains match_str."""
    try:
        r = subprocess.run(
            ["wmic", "process", "get", "CommandLine", "/FORMAT:CSV"],
            capture_output=True, text=True, timeout=15,
        )
        return match_str.lower() in r.stdout.lower()
    except Exception as e:
        log.warning(f"Process scan error ({match_str}): {e}")
        return True   # assume alive on error to avoid false restarts


def check_n8n() -> bool:
    try:
        r = requests.get(N8N_HEALTH_URL, timeout=6)
        return r.status_code == 200
    except Exception:
        return False


def send_alert(message: str):
    """Send alert via ClaudeClaw /internal/ticket endpoint."""
    job_id = f"WATCHDOG-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    payload = {
        "job_id":  job_id,
        "muscle":  "originator",
        "payload": {"text": f"\u26a0\ufe0f [APEX WATCHDOG] {message}"}
    }
    try:
        r = requests.post(TICKET_URL, json=payload, timeout=6)
        if r.status_code < 300:
            log.info(f"Alert sent ({job_id}): {message}")
        else:
            log.warning(f"Alert HTTP {r.status_code}: {message}")
    except Exception as e:
        log.warning(f"Alert failed ({e}): {message}")


def start_process(name: str, config: dict):
    """Launch a managed process detached."""
    log.info(f"Restarting {name} ...")
    try:
        subprocess.Popen(
            config["cmd"],
            cwd=config.get("cwd"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        )
        log.info(f"{name} restarted.")
        send_alert(f"{name} was DOWN and has been restarted.")
    except Exception as e:
        log.error(f"Failed to restart {name}: {e}")
        send_alert(f"RESTART FAILED for {name}: {e}")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# MAIN LOGIC
# ---------------------------------------------------------------------------
def run_check() -> dict:
    status = {}
    for name, config in PROCESSES.items():
        alive = find_process(config["match_str"])
        status[name] = "OK" if alive else "DOWN"
        log.info(f"  {name}: {status[name]}")
    n8n_ok = check_n8n()
    status["n8n"] = "OK" if n8n_ok else "DOWN"
    log.info(f"  n8n: {status['n8n']}")
    return status


def main():
    parser = argparse.ArgumentParser(description="APEX Supervisor Watchdog")
    parser.add_argument("--check", action="store_true",
                        help="Check only — exit 0 all OK, 1 something down")
    args = parser.parse_args()

    log.info("=== APEX Watchdog cycle start ===")
    status = run_check()
    all_ok = all(v == "OK" for v in status.values())

    if args.check:
        print(json.dumps({"status": status, "all_ok": all_ok}, indent=2))
        sys.exit(0 if all_ok else 1)

    prev = load_state()

    # Restart dead managed processes
    for name, config in PROCESSES.items():
        if status[name] == "DOWN":
            start_process(name, config)
            time.sleep(3)

    # n8n lives in Docker on NAS — can't auto-restart, just alert on new failure
    if status["n8n"] == "DOWN" and prev.get("n8n") != "DOWN":
        send_alert("n8n health check FAILED. Check Docker on NAS (192.168.50.246).")

    save_state({**status, "checked_at": datetime.now(timezone.utc).isoformat()})
    log.info(f"=== Watchdog cycle complete: {status} ===")


if __name__ == "__main__":
    main()
