"""
muscle_health_check.py — System Health Check Muscle
Ref:        APEX-MB-PY-00007
Version:    1.0
Author:     MB / SYS
Description: Reports disk space, Python version, pip package count, skill count from manifest,
             last index time, foreman heartbeat age, and n8n reachability.
Inputs:     --output PATH   Where to write health_report.json (default: audit/health/health_report.json)
Outputs:    Structured JSON health report. Prints {"status": "OK", "output": "<path>"}.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path


APEX_ROOT     = Path(__file__).parent.parent
MANIFEST_FILE = APEX_ROOT / "registry" / "manifest.json"
HEARTBEAT     = APEX_ROOT / "hub" / ".heartbeat"
N8N_URL       = "http://192.168.50.246:5678"
DEFAULT_OUTPUT = APEX_ROOT / "audit" / "health" / "health_report.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def muscle_health_check(output_path: str = None) -> dict:
    """
    Run a full system health check and write JSON report.
    Returns {"status": "OK", "output": output_path} or raises.
    """
    report = {"timestamp": _now_iso(), "checks": {}}

    # Disk space (C: drive)
    try:
        total, used, free = shutil.disk_usage("C:\\")
        report["checks"]["disk_space"] = {
            "status":    "OK" if free > 5 * 1024**3 else "WARN",
            "free_gb":   round(free / 1024**3, 2),
            "total_gb":  round(total / 1024**3, 2),
            "threshold_gb": 5,
        }
    except Exception as e:
        report["checks"]["disk_space"] = {"status": "ERROR", "error": str(e)}

    # Python version
    report["checks"]["python"] = {
        "status":  "OK",
        "version": platform.python_version(),
        "executable": sys.executable,
    }

    # Pip package count
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=columns"],
            capture_output=True, text=True, timeout=15
        )
        pkg_count = max(0, len(result.stdout.strip().splitlines()) - 2)
        report["checks"]["pip_packages"] = {"status": "OK", "count": pkg_count}
    except Exception as e:
        report["checks"]["pip_packages"] = {"status": "ERROR", "error": str(e)}

    # Skill count and last index from manifest
    try:
        if MANIFEST_FILE.exists():
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            report["checks"]["manifest"] = {
                "status":        "OK",
                "skill_count":   manifest.get("total_skills", 0),
                "last_indexed":  manifest.get("last_indexed", "never"),
                "duplicate_count": len(manifest.get("duplicates", [])),
            }
        else:
            report["checks"]["manifest"] = {"status": "MISSING", "note": "Run python indexer.py --scan"}
    except Exception as e:
        report["checks"]["manifest"] = {"status": "ERROR", "error": str(e)}

    # Foreman heartbeat age
    try:
        if HEARTBEAT.exists():
            age_seconds = int(time.time() - HEARTBEAT.stat().st_mtime)
            report["checks"]["foreman_heartbeat"] = {
                "status":      "OK" if age_seconds < 120 else "WARN",
                "age_seconds": age_seconds,
                "threshold_s": 120,
            }
        else:
            report["checks"]["foreman_heartbeat"] = {
                "status": "MISSING",
                "note":   "Foreman has not run yet or heartbeat was deleted",
            }
    except Exception as e:
        report["checks"]["foreman_heartbeat"] = {"status": "ERROR", "error": str(e)}

    # n8n reachability
    try:
        req = urllib.request.Request(N8N_URL, method="GET")
        urllib.request.urlopen(req, timeout=5)
        report["checks"]["n8n"] = {"status": "OK", "url": N8N_URL}
    except urllib.error.URLError as e:
        report["checks"]["n8n"] = {"status": "UNREACHABLE", "url": N8N_URL, "error": str(e)}
    except Exception as e:
        report["checks"]["n8n"] = {"status": "ERROR", "url": N8N_URL, "error": str(e)}

    # Dead letter count
    dead_letter = APEX_ROOT / "hub" / "dead_letter"
    try:
        dl_count = len(list(dead_letter.glob("*.json"))) if dead_letter.exists() else 0
        report["checks"]["dead_letter"] = {
            "status": "OK" if dl_count < 10 else "WARN",
            "count":  dl_count,
            "threshold": 10,
        }
    except Exception as e:
        report["checks"]["dead_letter"] = {"status": "ERROR", "error": str(e)}

    # Overall status
    statuses = [v.get("status", "OK") for v in report["checks"].values()]
    if "ERROR" in statuses or "FATAL" in statuses:
        report["overall"] = "ERROR"
    elif "WARN" in statuses or "UNREACHABLE" in statuses or "MISSING" in statuses:
        report["overall"] = "WARN"
    else:
        report["overall"] = "OK"

    # Write report
    out = Path(output_path) if output_path else DEFAULT_OUTPUT
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    return {"status": "OK", "output": str(out), "overall": report["overall"]}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: system health check")
    parser.add_argument("--output",      default=None, help="Output JSON path (default: audit/health/health_report.json)")
    parser.add_argument("--task-folder", default="",   help="Foreman task folder (unused)")
    args = parser.parse_args()

    try:
        result = muscle_health_check(args.output)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
