r"""
watchdog_gpu.py - APEX Supervisor Watchdog (portable)
Ref:        APEX-MB-PY-00011
Version:    1.1
Author:     MB / SYS
Description:
    Monitors APEX supervisor.py daemon and n8n health from any Windows host.
    Restarts dead supervisor. Sends Telegram alerts on state transitions.
    Reads APEX_ROOT from env; defaults to QNAP share UNC path.

Env:
    APEX_ROOT          default: \\192.168.50.246\Automations\apex
    N8N_HEALTH_URL     default: http://192.168.50.246:5678/healthz
    TELEGRAM_BOT_TOKEN required for alerts
    TELEGRAM_CHAT_ID   required for alerts

Usage:
    python watchdog_gpu.py            # one cycle
    python watchdog_gpu.py --check    # check-only; exit 0=OK, 1=down

Scheduled via Windows Task Scheduler every 5 minutes.
"""
import argparse, json, logging, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

try:
    import psutil
except ImportError:
    print("Missing: pip install psutil")
    sys.exit(1)
try:
    import requests
except ImportError:
    print("Missing: pip install requests")
    sys.exit(1)

APEX_ROOT = Path(os.environ.get(
    "APEX_ROOT", r"\\192.168.50.246\Automations\apex"
))
N8N_HEALTH_URL = os.environ.get(
    "N8N_HEALTH_URL", "http://192.168.50.246:5678/healthz"
)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

SUPERVISOR_PY = APEX_ROOT / "supervisor" / "supervisor.py"
LOGS_DIR      = APEX_ROOT / "logs"
STATE_FILE    = APEX_ROOT / "watchdog_state.json"
LOG_FILE      = LOGS_DIR / "watchdog.log"
SUPERVISOR_CMD = [sys.executable, str(SUPERVISOR_PY)]

LOGS_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [WATCHDOG] %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"),
              logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("watchdog")


def find_process(match_str: str) -> bool:
    """True if any running process cmdline contains match_str. Uses psutil."""
    needle = match_str.lower()
    for proc in psutil.process_iter(["cmdline"]):
        try:
            cmd = " ".join(proc.info.get("cmdline") or []).lower()
            if needle in cmd:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def check_n8n() -> bool:
    try:
        r = requests.get(N8N_HEALTH_URL, timeout=6)
        return r.status_code == 200
    except Exception:
        return False


def send_telegram(message: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.warning("Telegram not configured; skipping alert")
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID,
                  "text": f"[APEX WATCHDOG] {message}"},
            timeout=8,
        )
        return r.status_code == 200
    except Exception as e:
        log.warning("Telegram alert failed: %s", e)
        return False


def start_supervisor():
    log.info("Restarting supervisor from %s", SUPERVISOR_PY)
    try:
        subprocess.Popen(
            SUPERVISOR_CMD, cwd=str(SUPERVISOR_PY.parent),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=(subprocess.DETACHED_PROCESS
                           | subprocess.CREATE_NEW_PROCESS_GROUP),
        )
        send_telegram("supervisor was DOWN - restart issued.")
    except Exception as e:
        log.error("supervisor restart FAILED: %s", e)
        send_telegram(f"supervisor RESTART FAILED: {e}")


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {}


def save_state(state: dict):
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except Exception as e:
        log.warning("state save failed: %s", e)


def run_check() -> dict:
    status = {
        "supervisor": "OK" if find_process("supervisor.py") else "DOWN",
        "n8n":        "OK" if check_n8n() else "DOWN",
    }
    for k, v in status.items():
        log.info("  %s: %s", k, v)
    return status


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true",
                   help="Check only; exit 0 OK, 1 DOWN")
    args = p.parse_args()
    log.info("=== APEX watchdog cycle (APEX_ROOT=%s) ===", APEX_ROOT)
    status = run_check()
    all_ok = all(v == "OK" for v in status.values())
    if args.check:
        print(json.dumps({"status": status, "all_ok": all_ok}, indent=2))
        sys.exit(0 if all_ok else 1)
    prev = load_state()
    if status["supervisor"] == "DOWN":
        start_supervisor()
        time.sleep(3)
    if status["n8n"] == "DOWN" and prev.get("n8n") != "DOWN":
        send_telegram(
            f"n8n health check FAILED at {N8N_HEALTH_URL}. "
            f"Check Docker on NAS (192.168.50.246)."
        )
    save_state({**status,
                "checked_at": datetime.now(timezone.utc).isoformat()})
    log.info("=== cycle complete: %s ===", status)


if __name__ == "__main__":
    main()
