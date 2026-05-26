# TEST RECORD - muscle_work_gate

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00029 |
| **Version** | 1.0 |
| **Status** | APPROVED |

## Test Cases

| Case | Command | Expected | Result |
|---|---|---|---|
| Read gate | `python registry/muscle_work_gate.py --repo . --intent read --no-audit` | JSON report with repository fields | PASS |
| Fallback write gate | `python registry/muscle_work_gate.py --repo . --mode fallback --intent write --allow-dirty --no-audit` | JSON report marks fallback route as provisional | PASS |
| Normal stale/dirty gate | `python registry/muscle_work_gate.py --repo . --intent write --no-audit` | BLOCK without proven latest check or dirty acknowledgement | PASS |
| Promotion without fetch | `python registry/muscle_work_gate.py --repo . --intent promote --no-audit` | BLOCK because remote freshness is not proven | PASS |

**Approved:** YES - 2026-05-26
