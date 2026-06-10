# GUIDANCE - muscle_compliance_check

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00028 (proposed) |
| **Version** | 1.0 |

## When to Use

- Before any commit that touches `docs/DOCUMENT_REGISTER.md` (catch ref-code drift).
- Before any commit that adds or moves a `registry/muscle_*.py` file.
- As a scheduled daily / weekly audit to detect silent drift (paths going stale, secrets accidentally checked in).
- After bulk doctrine merges (this is exactly how the parallel-Claude merge today caught existing WIP gaps).
- When debugging "why doesn't `validate_tool_docs.py` flag X?" — this checker covers a wider surface.

## Do Not Use

- As a write-side governance tool. It is read-only and reports only; never mutates the register or any code.
- As the only secret scanner. Filename-based; complement with a content scanner if your threat model requires it.
- As proof of code quality. It checks governance compliance, not behavior correctness.
- During a rebase or mid-merge when `DOCUMENT_REGISTER.md` is in a partially-merged state — it will report spurious failures.

## How to Call

Standard audit run:
```powershell
python registry/muscle_compliance_check.py
```

CI / cron (JSON to file, no stdout noise):
```powershell
python registry/muscle_compliance_check.py --quiet
```

Strict pre-commit (warnings = failure):
```powershell
python registry/muscle_compliance_check.py --quiet --strict
```

## Example OK Output

```
APEX Compliance Check  -  root: C:\Users\Owner\Repos\code-artifacts\apex
timestamp: 2026-05-25T13:55:00+00:00

SUMMARY
  register_entries               87
  registered_resolved            85
  registered_missing             0
  registered_stale_path          0
  registered_external            2
  duplicate_refs                 0
  header_register_mismatches     0
  invalid_ref_format             0
  unregistered_disk_files        3
  muscles_missing_docs           0
  muscles_unapproved             0
  secrets_on_disk                0

  detail JSON: audit/compliance/2026-05-25T13-55-00Z.json
```
Exit code: 0.

## Example FAIL Output (truncated)

```
SUMMARY
  duplicate_refs                 1
  registered_missing             2
  muscles_missing_docs           3
  secrets_on_disk                0

FAIL: duplicate refs (1 total, showing up to 10):
  - APEX-MB-PY-00071: muscle_apex_context_push (header), muscle_apex_context_push (register)

FAIL: registered but missing on disk (2 total, showing up to 10):
  - APEX-MB-PY-00099 retired_thing -> apex/registry/retired_thing.py
```
Exit code: 1.

## Reading the JSON Detail

Each report is a single JSON object:
```json
{
  "root": "...",
  "timestamp": "...",
  "summary": { /* counts by category */ },
  "fails": 3,
  "warns": 4,
  "details": {
    "duplicate_refs": [...],
    "header_register_mismatches": [...],
    "registered_missing": [...],
    "registered_stale_path": [...],
    "registered_external": [...],
    "invalid_ref_format": [...],
    "unregistered_disk_files": [...],
    "muscles_missing_docs": [...],
    "muscles_unapproved": [...],
    "secrets_on_disk": [...]
  }
}
```

Each `details[<category>]` is a list of structured dicts; see source for exact per-category shape.

## Scheduled Job Pattern

1. Cron / Task Scheduler triggers nightly.
2. Run `muscle_compliance_check --quiet`.
3. Read latest `audit/compliance/*.json`.
4. If `fails > 0` OR `summary.secrets_on_disk > 0` → alert to operator.
5. If `warns > 0` only → log, do not alert.
6. Retain last 30 reports; archive older.

## Common Mistakes

- Running it against a stale repo root and assuming the result reflects current state — always `cd` to the repo first or pass `--root` explicitly.
- Treating `unregistered disk files` as automatically bad — many are intentional (research notes, audit transcripts). The right response is usually "register or move", not "delete".
- Treating `registered external` as a failure — these are intentional ref entries pointing at out-of-repo locations (e.g. `apex_governance/` files). The checker flags them only so you know they aren't repo-resident.
- Running `--strict` in dev without first cleaning warnings — guarantees a fail every time.
