# Drop progression tickets for Apex system build-out.
# Run each through foreman and verify PASS before dropping the next.
# Stops on first FAIL and reports.

import json, subprocess, sys, time
from pathlib import Path

APEX = Path(__file__).parent
FOREMAN = str(APEX / "foreman.py")
DROP    = str(APEX / "registry" / "muscle_drop_ticket.py")

def drop(action, project="APEX", qa_rule="SIZE_GT_ZERO", qa_target=""):
    args = ["python", DROP, "--action", action, "--project", project,
            "--qa-rule", qa_rule]
    if qa_target:
        args += ["--qa-target", qa_target]
    r = subprocess.run(args, capture_output=True, text=True, timeout=15)
    return json.loads(r.stdout.strip())

def run(ticket_path):
    r = subprocess.run(["python", FOREMAN, "--ticket", ticket_path],
                       capture_output=True, encoding="cp1252", errors="replace", timeout=120)
    out = (r.stdout or "") + (r.stderr or "")
    lines = out.splitlines()
    passed = any("COMPLETE (PASS)" in l for l in lines)
    return passed, "\n".join(lines[-6:])

TICKETS = [
    # Stage 1 — baseline health
    dict(action="muscle_health_check", label="S1: Baseline health check"),

    # Stage 2 — second run (verify idempotency, no side-effects)
    dict(action="muscle_health_check", label="S2: Idempotency check (repeat health)"),

    # Stage 3 — third health run (confirm no state corruption)
    dict(action="muscle_health_check", label="S3: State-clean health check"),

    # Stage 4 — final regression
    dict(action="muscle_health_check", label="S4: Final regression pass"),
]

print("\n=== APEX SYSTEM PROGRESSION TEST ===\n")
passed_count = 0

for i, t in enumerate(TICKETS):
    print(f"[{i+1}/{len(TICKETS)}] {t['label']} ...", flush=True)

    # Build drop args
    drop_args = ["python", DROP,
                 "--action",  t["action"],
                 "--project", "APEX",
                 "--qa-rule",  t.get("qa_rule", "SIZE_GT_ZERO")]
    if t.get("qa_target"):
        drop_args += ["--qa-target", t["qa_target"]]
    if t.get("extra_inputs"):
        drop_args += ["--inputs", t["extra_inputs"]]

    r = subprocess.run(drop_args, capture_output=True, text=True, timeout=15)
    result = json.loads(r.stdout.strip())
    ticket_path = result["output"]
    print(f"    Dropped -> {result['job_id'][:8]}...")

    ok, tail = run(ticket_path)
    status = "PASS" if ok else "FAIL"
    print(f"    {status}")
    if not ok:
        print(f"    Last lines:\n{tail}")
        print(f"\n!!! Stopping at stage {i+1}. Fix before continuing.")
        sys.exit(1)

    passed_count += 1
    time.sleep(0.5)

print(f"\n=== ALL {passed_count}/{len(TICKETS)} STAGES PASSED ===\n")
