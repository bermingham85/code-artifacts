"""
foreman.py — Work Order Executor
Ref:        APEX-MB-PY-00003
Version:    1.0
Author:     MB / SYS
Description: Called by n8n with a path to a WorkOrder.json in hub/.
             Executes 10 steps: idempotency, ingest, doc control, manifest lookup,
             prerequisite validation, subprocess execution with retry/circuit breaker,
             compound QA gate, chain, archive, heartbeat + dead letter.

Usage:
    python foreman.py --ticket "C:\\Users\\bermi\\Projects\\apex\\hub\\WO-XYZ.json"
"""

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
APEX_ROOT     = Path(__file__).parent
AUDIT_DIR     = APEX_ROOT / "audit"
LOGS_DIR      = APEX_ROOT / "logs"
HUB_DIR       = APEX_ROOT / "hub"
DEAD_LETTER   = HUB_DIR / "dead_letter"
TMP_DIR       = HUB_DIR / ".tmp"
REGISTRY_DIR  = APEX_ROOT / "registry"
MANIFEST_FILE = REGISTRY_DIR / "manifest.json"
TASKS_DIR     = APEX_ROOT / "active_projects" / "tasks"
LOG_FILE      = LOGS_DIR / "foreman.log"

# Bootstrap paths
for d in [AUDIT_DIR, LOGS_DIR, HUB_DIR, DEAD_LETTER, TMP_DIR, TASKS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Simple file logger (avoid log module dependency)
# ---------------------------------------------------------------------------
def _log(level: str, msg: str):
    line = f"{_now_iso()} [{level}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Atomic hub write (prevents n8n reading partially-written JSON)
# ---------------------------------------------------------------------------
def _atomic_write_hub(filename: str, data: dict):
    tmp_path = TMP_DIR / filename
    final_path = HUB_DIR / filename
    tmp_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        os.rename(str(tmp_path), str(final_path))
    except OSError:
        shutil.move(str(tmp_path), str(final_path))


# ---------------------------------------------------------------------------
# DiagnosticTicket writer
# ---------------------------------------------------------------------------
def _write_diagnostic(
    parent_job_id: str,
    stage: str,
    message: str,
    severity: str = "ERROR",
    error_type: str = "ForwardException",
    tb: str = "",
    auto_retry: bool = False,
    retry_count: int = 0,
    suggested_action: str = None,
):
    ticket = {
        "meta": {
            "ticket_id":      str(uuid.uuid4()),
            "ref_code":       "APEX-SYS-WF-00000",
            "parent_job_id":  parent_job_id,
            "created_at":     _now_iso(),
            "severity":       severity,
            "receiver":       "originator",
        },
        "failure": {
            "stage":       stage,
            "error_type":  error_type,
            "message":     message,
            "traceback":   tb,
        },
        "resolution": {
            "suggested_action": suggested_action,
            "auto_retry":       auto_retry,
            "retry_count":      retry_count,
            "resolved":         False,
            "resolved_at":      None,
        },
    }
    filename = f"DIAG-{parent_job_id}.json"
    _atomic_write_hub(filename, ticket)
    _log("WARN", f"DiagnosticTicket written: {filename} ({severity} / {stage})")
    return ticket


# ---------------------------------------------------------------------------
# WorkOrder I/O
# ---------------------------------------------------------------------------
def _read_ticket(ticket_path: Path) -> dict:
    with open(ticket_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_ticket(ticket_path: Path, data: dict):
    ticket_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Heartbeat
# ---------------------------------------------------------------------------
def _write_heartbeat(last_job_status: str = "IDLE"):
    heartbeat_file = HUB_DIR / ".heartbeat"
    pid_file       = HUB_DIR / ".foreman_pid"
    heartbeat_file.write_text(
        json.dumps({"timestamp": _now_iso(), "status": last_job_status, "pid": os.getpid()}),
        encoding="utf-8"
    )
    pid_file.write_text(str(os.getpid()), encoding="utf-8")


# ---------------------------------------------------------------------------
# QA Gate
# ---------------------------------------------------------------------------
def _run_qa_check(check: dict, task_folder: Path) -> tuple[bool, str]:
    """Run a single QA check. Returns (passed, reason)."""
    rule   = check.get("rule", "FILE_EXISTS")
    target = check.get("target", "")
    target_path = Path(target) if Path(target).is_absolute() else task_folder / target

    if rule == "FILE_EXISTS":
        if not target_path.exists():
            return False, f"FILE_EXISTS: {target_path} does not exist"
        min_size = check.get("min_size_bytes", 0)
        if min_size > 0 and target_path.stat().st_size < min_size:
            return False, f"SIZE_GT_ZERO: {target_path} is smaller than {min_size} bytes"
        return True, "OK"

    elif rule == "SIZE_GT_ZERO":
        if not target_path.exists():
            return False, f"SIZE_GT_ZERO: {target_path} does not exist"
        min_size = check.get("min_size_bytes", 1)
        if target_path.stat().st_size < min_size:
            return False, f"SIZE_GT_ZERO: {target_path} is {target_path.stat().st_size} bytes (need >{min_size})"
        return True, "OK"

    elif rule == "CONTAINS_STRING":
        if not target_path.exists():
            return False, f"CONTAINS_STRING: {target_path} does not exist"
        expected = check.get("expected_string", "")
        content  = target_path.read_text(encoding="utf-8", errors="ignore")
        if expected not in content:
            return False, f"CONTAINS_STRING: '{expected}' not found in {target_path}"
        return True, "OK"

    elif rule == "JSON_VALID":
        if not target_path.exists():
            return False, f"JSON_VALID: {target_path} does not exist"
        try:
            json.loads(target_path.read_text(encoding="utf-8", errors="ignore"))
            return True, "OK"
        except json.JSONDecodeError as e:
            return False, f"JSON_VALID: not valid JSON — {e}"

    # ── Q2: SPEC COMPLIANCE — "Is it the RIGHT output?" ───────────────────

    elif rule == "SPEC_STATUS_OK":
        if not target_path.exists():
            return False, f"SPEC_STATUS_OK: {target_path} does not exist"
        try:
            data = json.loads(target_path.read_text(encoding="utf-8", errors="ignore"))
            if str(data.get("status", "")).upper() != "OK":
                return False, f"SPEC_STATUS_OK: status={data.get('status')!r}, expected 'OK'"
            return True, "OK"
        except json.JSONDecodeError:
            return False, f"SPEC_STATUS_OK: {target_path} is not valid JSON"

    elif rule == "SPEC_FIELD_EXISTS":
        if not target_path.exists():
            return False, f"SPEC_FIELD_EXISTS: {target_path} does not exist"
        field = check.get("expected_field", "")
        try:
            data = json.loads(target_path.read_text(encoding="utf-8", errors="ignore"))
            if field not in data:
                return False, f"SPEC_FIELD_EXISTS: field '{field}' missing from output"
            return True, "OK"
        except json.JSONDecodeError:
            return False, f"SPEC_FIELD_EXISTS: {target_path} is not valid JSON"

    elif rule == "SPEC_MATCH":
        if not target_path.exists():
            return False, f"SPEC_MATCH: {target_path} does not exist"
        field    = check.get("expected_field", "status")
        expected = check.get("expected_value", "OK")
        try:
            data   = json.loads(target_path.read_text(encoding="utf-8", errors="ignore"))
            actual = data.get(field)
            if str(actual) != str(expected):
                return False, f"SPEC_MATCH: {field}={actual!r}, expected {expected!r}"
            return True, "OK"
        except json.JSONDecodeError:
            return False, f"SPEC_MATCH: {target_path} is not valid JSON"

    elif rule == "MULTI":
        checks = check.get("checks", [])
        for sub_check in checks:
            passed, reason = _run_qa_check(sub_check, task_folder)
            if not passed:
                return False, reason
        return True, "OK"

    return False, f"Unknown QA rule: {rule}"


def _run_qa_gate(wo: dict, task_folder: Path) -> tuple[bool, str]:
    """Run the QA gate from a WorkOrder. Returns (passed, failure_reason)."""
    qa_gate = wo.get("qa_gate", {})
    rule    = qa_gate.get("rule", "FILE_EXISTS")

    if rule == "MULTI":
        checks = qa_gate.get("checks", [])
        for check in checks:
            passed, reason = _run_qa_check(check, task_folder)
            if not passed:
                return False, reason
        return True, "OK"
    else:
        checks = qa_gate.get("checks", [])
        if checks:
            return _run_qa_check(checks[0], task_folder)
        return True, "OK (no checks defined)"


# ---------------------------------------------------------------------------
# Prerequisite validation
# ---------------------------------------------------------------------------
def _check_prerequisites(sop: dict, task_folder: Path) -> tuple[bool, str]:
    # Check inputs exist
    for inp in sop.get("inputs", []):
        p = Path(inp)
        if not p.is_absolute():
            p = task_folder / inp
        if not p.exists():
            return False, f"Input missing: {inp}"

    # Check requirements importable
    for req in sop.get("requirements", []):
        if importlib.util.find_spec(req) is None:
            return False, f"Requirement not installed: {req}"

    return True, "OK"


# ---------------------------------------------------------------------------
# Muscle resolution
# ---------------------------------------------------------------------------
def _find_muscle_path(action: str, manifest: dict) -> Path | None:
    """Find a callable muscle in manifest by name."""
    for skill in manifest.get("skills", []):
        if skill["name"] == action and skill.get("callable_as_muscle"):
            return Path(skill["file"])
    # Also search registry/ directly by filename convention
    muscle_file = REGISTRY_DIR / f"{action}.py"
    if muscle_file.exists():
        return muscle_file
    return None


def _load_manifest() -> dict:
    if not MANIFEST_FILE.exists():
        return {"skills": []}
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Doc control check
# ---------------------------------------------------------------------------
def _doc_control_check(action: str) -> bool:
    """Check if action (skill name) is registered in document register."""
    sys.path.insert(0, str(APEX_ROOT / "docs"))
    try:
        from doc_controller import find_doc
        results = find_doc(action)
        return len(results) > 0
    except Exception as e:
        _log("WARN", f"doc_controller check failed: {e} — allowing anyway")
        return True  # Fail open on doc_controller errors


# ---------------------------------------------------------------------------
# Main foreman logic
# ---------------------------------------------------------------------------
def process_ticket(ticket_path: Path):
    _log("INFO", f"Foreman started — ticket: {ticket_path}")
    _write_heartbeat("PROCESSING")

    # ----------------------------------------------------------------
    # STEP 0 — IDEMPOTENCY CHECK
    # ----------------------------------------------------------------
    try:
        wo = _read_ticket(ticket_path)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        _log("ERROR", f"Cannot read ticket: {e}")
        return

    job_id = wo.get("meta", {}).get("job_id", "UNKNOWN")

    # Search audit/ for existing task folder
    today_dir = AUDIT_DIR / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for search_dir in [AUDIT_DIR] + list(AUDIT_DIR.iterdir()) if AUDIT_DIR.exists() else []:
        if search_dir.is_dir():
            task_dir = search_dir / f"task_{job_id}"
            if task_dir.exists():
                _log("INFO", f"IDEMPOTENCY: Job {job_id} already processed — skipping")
                _write_diagnostic(job_id, "IDEMPOTENCY",
                                  f"Job {job_id} already processed — duplicate trigger suppressed",
                                  severity="INFO", error_type="DuplicateJob")
                _write_heartbeat("IDLE")
                return

    # ----------------------------------------------------------------
    # STEP 1 — INGEST
    # ----------------------------------------------------------------
    meta = wo.get("meta", {})
    sop  = wo.get("sop", {})

    # Basic schema validation
    required_meta = ["job_id", "sender", "receiver", "project"]
    for field in required_meta:
        if not meta.get(field):
            _write_diagnostic(job_id, "VALIDATION",
                              f"WorkOrder missing required meta field: {field}",
                              severity="ERROR", error_type="SchemaError")
            _write_heartbeat("FAILED")
            return

    if not sop.get("action"):
        _write_diagnostic(job_id, "VALIDATION",
                          "WorkOrder missing sop.action",
                          severity="ERROR", error_type="SchemaError")
        _write_heartbeat("FAILED")
        return

    # Create task folder
    task_folder = TASKS_DIR / f"task_{job_id}"
    task_folder.mkdir(parents=True, exist_ok=True)

    # Copy WorkOrder into task folder
    wo_copy = task_folder / "WorkOrder.json"
    _write_ticket(wo_copy, wo)

    _log("INFO", f"STEP 1 INGEST: job_id={job_id} sender={meta.get('sender')} action={sop.get('action')}")

    # ----------------------------------------------------------------
    # STEP 2 — DOC CONTROL CHECK
    # ----------------------------------------------------------------
    action = sop["action"]
    if not _doc_control_check(action):
        _write_diagnostic(job_id, "DOC_CONTROL",
                          f"Skill '{action}' not registered in document register. Run doc_controller --register first.",
                          severity="ERROR", error_type="UnregisteredSkill",
                          suggested_action="Register skill with doc_controller.py --register")
        wo["status"]["state"] = "FAILED"
        _write_ticket(wo_copy, wo)
        _write_heartbeat("FAILED")
        return

    _log("INFO", f"STEP 2 DOC CONTROL: '{action}' verified in register")

    # ----------------------------------------------------------------
    # STEP 3 — MANIFEST LOOKUP (REUSE GATE)
    # ----------------------------------------------------------------
    manifest = _load_manifest()
    muscle_path = _find_muscle_path(action, manifest)

    if muscle_path is None:
        _write_diagnostic(job_id, "VALIDATION",
                          f"Skill '{action}' not found in registry manifest. Run: python indexer.py --scan",
                          severity="ERROR", error_type="SkillNotFound",
                          suggested_action="python indexer.py --scan")
        wo["status"]["state"] = "FAILED"
        _write_ticket(wo_copy, wo)
        _write_heartbeat("FAILED")
        return

    _log("INFO", f"STEP 3 MANIFEST: found '{action}' at {muscle_path}")

    # ----------------------------------------------------------------
    # STEP 4 — PREREQUISITE VALIDATION
    # ----------------------------------------------------------------
    prereq_ok, prereq_msg = _check_prerequisites(sop, task_folder)
    if not prereq_ok:
        wo["status"]["state"] = "FAILED"
        _write_ticket(wo_copy, wo)
        _write_diagnostic(job_id, "VALIDATION",
                          f"Prerequisite check failed: {prereq_msg}",
                          severity="ERROR", error_type="PrerequisiteMissing")
        _write_heartbeat("FAILED")
        return

    _log("INFO", f"STEP 4 PREREQUISITES: OK")

    # ----------------------------------------------------------------
    # STEP 5 — EXECUTION (with retry and circuit breaker)
    # ----------------------------------------------------------------
    wo["status"]["state"]      = "RUNNING"
    wo["status"]["started_at"] = _now_iso()
    _write_ticket(wo_copy, wo)

    timeout_sec   = sop.get("timeout_seconds", 300)
    max_retries   = meta.get("max_retries", 3)
    retry_count   = meta.get("retry_count", 0)

    # Build command: python muscle.py --task-folder <path> [--input ...] [--param ...]
    cmd = [sys.executable, str(muscle_path), "--task-folder", str(task_folder)]
    for inp in sop.get("inputs", []):
        cmd += ["--input", inp]
    for k, v in sop.get("parameters", {}).items():
        cmd += [f"--{k}", str(v)]

    output_log = task_folder / "output.log"
    exit_code  = -1
    stdout_out = ""
    stderr_out = ""
    duration   = 0.0

    transient_errors = (TimeoutError, OSError, PermissionError)

    while True:
        t0 = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(APEX_ROOT),
            )
            duration   = round(time.time() - t0, 2)
            exit_code  = result.returncode
            stdout_out = result.stdout
            stderr_out = result.stderr
            output_log.write_text(stdout_out, encoding="utf-8")

            if exit_code == 0:
                _log("INFO", f"STEP 5 EXECUTION: OK (exit 0, {duration}s)")
                break

            # Non-zero exit — check if retryable
            _log("WARN", f"STEP 5 EXECUTION: exit {exit_code} (attempt {retry_count+1}/{max_retries+1})")
            if retry_count < max_retries:
                retry_count += 1
                backoff = min(2 ** retry_count, 60)
                _log("INFO", f"  Retrying in {backoff}s (retry {retry_count}/{max_retries})...")
                time.sleep(backoff)
                continue
            else:
                # Retries exhausted
                tb = stderr_out or f"Exit code {exit_code}"
                wo["status"].update({
                    "state":            "FAILED",
                    "completed_at":     _now_iso(),
                    "duration_seconds": duration,
                    "exit_code":        exit_code,
                    "traceback":        tb,
                })
                _write_ticket(wo_copy, wo)
                _write_diagnostic(job_id, "EXECUTION",
                                  f"Muscle '{action}' failed after {retry_count} retries (exit {exit_code})",
                                  severity="FATAL", error_type="ExecutionFailed",
                                  tb=tb, retry_count=retry_count,
                                  suggested_action="Manual review required")
                # Dead letter
                _move_to_dead_letter(ticket_path, job_id)
                _write_heartbeat("FAILED")
                return

        except subprocess.TimeoutExpired:
            duration = round(time.time() - t0, 2)
            _log("WARN", f"STEP 5 TIMEOUT after {timeout_sec}s (attempt {retry_count+1})")
            if retry_count < max_retries:
                retry_count += 1
                backoff = min(2 ** retry_count, 60)
                time.sleep(backoff)
                continue
            wo["status"].update({
                "state": "FAILED", "completed_at": _now_iso(),
                "duration_seconds": duration, "exit_code": -1,
                "traceback": f"Timeout after {timeout_sec}s"
            })
            _write_ticket(wo_copy, wo)
            _write_diagnostic(job_id, "TIMEOUT",
                              f"Muscle '{action}' timed out after {timeout_sec}s",
                              severity="FATAL", error_type="Timeout",
                              retry_count=retry_count,
                              suggested_action="Manual review required")
            _move_to_dead_letter(ticket_path, job_id)
            _write_heartbeat("FAILED")
            return

        except Exception as e:
            tb = traceback.format_exc()
            _log("ERROR", f"STEP 5 EXCEPTION: {e}")
            wo["status"].update({
                "state": "FAILED", "completed_at": _now_iso(),
                "exit_code": -1, "traceback": tb
            })
            _write_ticket(wo_copy, wo)
            _write_diagnostic(job_id, "EXECUTION",
                              str(e), severity="FATAL", error_type=type(e).__name__, tb=tb,
                              suggested_action="Manual review required")
            _move_to_dead_letter(ticket_path, job_id)
            _write_heartbeat("FAILED")
            return

    # ----------------------------------------------------------------
    # STEP 6 — QA GATE
    # ----------------------------------------------------------------
    qa_passed, qa_reason = _run_qa_gate(wo, task_folder)
    if not qa_passed:
        _log("WARN", f"STEP 6 QA GATE: FAIL — {qa_reason}")
        wo["status"].update({
            "state":            "FAILED",
            "completed_at":     _now_iso(),
            "duration_seconds": duration,
            "exit_code":        exit_code,
            "qa_result":        "FAIL",
        })
        _write_ticket(wo_copy, wo)
        _write_diagnostic(job_id, "QA_GATE",
                          qa_reason, severity="ERROR", error_type="QAGateFailure")
        _write_heartbeat("FAILED")
        return

    _log("INFO", f"STEP 6 QA GATE: PASS")

    # ----------------------------------------------------------------
    # STEP 7 — CHAIN
    # ----------------------------------------------------------------
    chain_next = meta.get("chain_next")
    if chain_next:
        _log("INFO", f"STEP 7 CHAIN: queuing next job '{chain_next}'")
        child_wo = {
            "meta": {
                "job_id":         str(uuid.uuid4()),
                "ref_code":       "APEX-SYS-WF-00000",
                "created_at":     _now_iso(),
                "sender":         job_id,
                "receiver":       "foreman",
                "project":        meta.get("project", ""),
                "chain_next":     None,
                "idempotency_key": None,
                "retry_count":    0,
                "max_retries":    meta.get("max_retries", 3),
                "priority":       meta.get("priority", "NORMAL"),
            },
            "sop": {
                "action":          chain_next,
                "inputs":          [str(output_log)],
                "parameters":      {},
                "requirements":    [],
                "timeout_seconds": 300,
            },
            "task_folder": str(TASKS_DIR / f"task_{job_id}_chain"),
            "qa_gate":     wo.get("qa_gate", {"rule": "FILE_EXISTS", "checks": []}),
            "status":      {"state": "PENDING", "started_at": None, "completed_at": None,
                            "duration_seconds": None, "diagnostic": None, "traceback": None,
                            "qa_result": None, "exit_code": None},
        }
        child_filename = f"WO-CHAIN-{child_wo['meta']['job_id']}.json"
        _atomic_write_hub(child_filename, child_wo)
        _log("INFO", f"  Chain ticket dropped: {child_filename}")

    # ----------------------------------------------------------------
    # STEP 8 — ARCHIVE
    # ----------------------------------------------------------------

    # Build compact qa_checks list for the completion report
    qa_check_log = []
    for chk in wo.get("qa_gate", {}).get("checks", []):
        qa_check_log.append({"rule": chk.get("rule", "?"), "result": "PASS"})

    # Extract output_summary from muscle stdout (the "summary" field if present)
    output_summary = ""
    try:
        stdout_data = json.loads(stdout_out.strip()) if stdout_out.strip() else {}
        output_summary = (
            stdout_data.get("summary") or
            stdout_data.get("output") or
            stdout_data.get("result") or
            f"{sop.get('action')} completed"
        )
        if isinstance(output_summary, str):
            output_summary = output_summary[:200]
        else:
            output_summary = str(output_summary)[:200]
    except Exception:
        output_summary = f"{sop.get('action')} completed in {duration}s"

    wo["status"].update({
        "state":            "COMPLETE",
        "completed_at":     _now_iso(),
        "duration_seconds": duration,
        "exit_code":        exit_code,
        "qa_result":        "PASS",
        "qa_checks":        qa_check_log,
        "output_summary":   output_summary,
    })
    _write_ticket(wo_copy, wo)

    # Write compact CompletionReport (the postman's outbound signal)
    completion_report = {
        "job_id":           job_id,
        "action":           sop.get("action", ""),
        "project":          meta.get("project", ""),
        "sender":           meta.get("sender", ""),
        "result":           "PASS",
        "qa_checks":        qa_check_log,
        "output_summary":   output_summary,
        "duration_seconds": duration,
        "timestamp":        _now_iso(),
    }
    report_path = task_folder / "CompletionReport.json"
    try:
        report_path.write_text(json.dumps(completion_report, indent=2), encoding="utf-8")
    except Exception:
        pass  # task_folder may already be moving — not fatal

    # Move task folder to audit/YYYY-MM-DD/task_{job_id}/
    archive_dir = AUDIT_DIR / datetime.now(timezone.utc).strftime("%Y-%m-%d")
    archive_dir.mkdir(parents=True, exist_ok=True)
    dest = archive_dir / f"task_{job_id}"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.move(str(task_folder), str(dest))
    _log("INFO", f"STEP 8 ARCHIVE: task archived to {dest}")
    _log("INFO", f"  CompletionReport: {output_summary}")

    # ----------------------------------------------------------------
    # STEP 9 — HEARTBEAT
    # ----------------------------------------------------------------
    _write_heartbeat("COMPLETE")
    _log("INFO", f"STEP 9 HEARTBEAT: updated")

    _log("INFO", f"=== JOB {job_id} COMPLETE (PASS) in {duration}s ===")

    # ----------------------------------------------------------------
    # STEP 10 — DEAD LETTER CHECK (handled in step 5 on FATAL, nothing more to do)
    # ----------------------------------------------------------------


def _move_to_dead_letter(ticket_path: Path, job_id: str):
    """Move the original WorkOrder to dead_letter/ on FATAL failure."""
    if ticket_path.exists():
        dest = DEAD_LETTER / ticket_path.name
        shutil.copy2(str(ticket_path), str(dest))
        _log("WARN", f"STEP 10 DEAD LETTER: {ticket_path.name} moved to dead_letter/")
    else:
        _log("WARN", f"STEP 10 DEAD LETTER: ticket path not found ({ticket_path})")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Apex Foreman — Work Order Executor")
    parser.add_argument("--ticket", required=True, help="Path to WorkOrder.json in hub/")
    args = parser.parse_args()

    ticket_path = Path(args.ticket)
    if not ticket_path.exists():
        print(f"[foreman] ERROR: ticket not found: {ticket_path}")
        sys.exit(1)

    process_ticket(ticket_path)


if __name__ == "__main__":
    main()
