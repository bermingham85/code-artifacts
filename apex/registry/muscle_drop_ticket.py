"""
muscle_drop_ticket.py — Work Order Drop Muscle
Ref:        APEX-MB-PY-00008
Version:    1.0
Author:     MB / SYS
Description: Creates a new WorkOrder and drops it atomically into hub/ from CLI args.
             Generates UUID, timestamps, writes atomically using tmp + rename.
Inputs:     --action MUSCLE_NAME    Skill name to execute
            --project PROJECT       Project code (APEX/CLAW/BERM etc)
            --inputs PATH,PATH      Comma-separated input paths (optional)
            --qa-rule RULE          QA rule: FILE_EXISTS | SIZE_GT_ZERO | CONTAINS_STRING (default: FILE_EXISTS)
            --qa-target PATH        QA check target path
            --priority NORMAL       NORMAL | HIGH | LOW (default: NORMAL)
            --max-retries N         Max retries (default: 3)
            --timeout N             Timeout seconds (default: 300)
Outputs:    WorkOrder JSON in hub/. Prints {"status": "OK", "job_id": "...", "output": "..."}.
"""

import argparse
import json
import os
import shutil
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


APEX_ROOT  = Path(__file__).parent.parent
HUB_DIR    = APEX_ROOT / "hub"
TMP_DIR    = HUB_DIR / ".tmp"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def muscle_drop_ticket(action: str, project: str, inputs: list[str] = None,
                       qa_rule: str = "FILE_EXISTS", qa_target: str = "",
                       priority: str = "NORMAL", max_retries: int = 3,
                       timeout_seconds: int = 300) -> dict:
    """
    Build and atomically drop a new WorkOrder into hub/.
    Returns {"status": "OK", "job_id": job_id, "output": hub_path}.
    """
    job_id = str(uuid.uuid4())
    wo = {
        "meta": {
            "job_id":          job_id,
            "ref_code":        "APEX-SYS-WF-00000",
            "created_at":      _now_iso(),
            "sender":          "human_originator",
            "receiver":        "foreman",
            "project":         project,
            "chain_next":      None,
            "idempotency_key": None,
            "retry_count":     0,
            "max_retries":     max_retries,
            "priority":        priority,
        },
        "sop": {
            "action":          action,
            "inputs":          inputs or [],
            "parameters":      {},
            "requirements":    [],
            "timeout_seconds": timeout_seconds,
        },
        "task_folder": str(APEX_ROOT / "active_projects" / "tasks" / f"task_{job_id}"),
        "qa_gate": {
            "rule":   qa_rule,
            "checks": [
                {
                    "rule":             qa_rule,
                    "target":           qa_target or "",
                    "min_size_bytes":   0,
                    "expected_string":  None,
                }
            ],
        },
        "status": {
            "state":            "PENDING",
            "started_at":       None,
            "completed_at":     None,
            "duration_seconds": None,
            "diagnostic":       None,
            "traceback":        None,
            "qa_result":        None,
            "exit_code":        None,
        },
    }

    HUB_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)

    filename  = f"WO-{job_id}.json"
    tmp_path  = TMP_DIR / filename
    final_path = HUB_DIR / filename

    tmp_path.write_text(json.dumps(wo, indent=2), encoding="utf-8")
    try:
        os.rename(str(tmp_path), str(final_path))
    except OSError:
        shutil.move(str(tmp_path), str(final_path))

    return {"status": "OK", "job_id": job_id, "output": str(final_path)}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: drop a Work Order ticket into hub/")
    parser.add_argument("--action",      required=True,              help="Muscle name to execute")
    parser.add_argument("--project",     required=True,              help="Project code")
    parser.add_argument("--inputs",      default="",                 help="Comma-separated input paths")
    parser.add_argument("--qa-rule",     default="FILE_EXISTS",
                        choices=["FILE_EXISTS", "SIZE_GT_ZERO", "CONTAINS_STRING"])
    parser.add_argument("--qa-target",   default="",                 help="QA check target path")
    parser.add_argument("--priority",    default="NORMAL",
                        choices=["NORMAL", "HIGH", "LOW"])
    parser.add_argument("--max-retries", type=int,  default=3,       help="Max retries (default: 3)")
    parser.add_argument("--timeout",     type=int,  default=300,     help="Timeout seconds (default: 300)")
    parser.add_argument("--task-folder", default="",                 help="Foreman task folder (unused)")
    args = parser.parse_args()

    inputs = [p.strip() for p in args.inputs.split(",") if p.strip()] if args.inputs else []

    try:
        result = muscle_drop_ticket(
            action=args.action,
            project=args.project,
            inputs=inputs,
            qa_rule=args.qa_rule,
            qa_target=args.qa_target,
            priority=args.priority,
            max_retries=args.max_retries,
            timeout_seconds=args.timeout,
        )
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
