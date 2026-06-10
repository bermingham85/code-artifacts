# BLUEPRINT - muscle_compliance_check

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00028 (proposed; Codex to confirm via doc_controller) |
| **Tool Name** | muscle_compliance_check |
| **File** | `registry/muscle_compliance_check.py` |
| **Category** | governance |
| **Version** | 1.0 |
| **Author** | SYS / promoted by Claude (2026-05-25) |
| **Created** | (existing WIP, formalised this batch) |
| **Status** | DRAFT (pending Codex approval per APEX_PARALLEL_MERGE_PLAYBOOK) |

## Purpose

Read-only governance compliance checker for the Apex repository. Walks `docs/DOCUMENT_REGISTER.md` plus on-disk artefacts and produces a JSON detail report plus human stdout summary. Designed to be safe to run at any time — never writes outside `audit/compliance/`.

Performs the seven governance checks the Naming & Document Control Convention (`docs/NAMING_CONVENTION.md`) mandates but which are otherwise only spot-checked at PR time:

1. Ref-code format validity (`PROJECT-ORIGINATOR-TYPE-SEQUENCE`)
2. Ref-code uniqueness across register entries AND Python file headers
3. Register row ↔ Python header agreement (the file at the register's path actually has that ref in its docstring)
4. Register-path resolution: ok / remapped / external / missing / stale-path-missing / no-path
5. Disk-file vs register coverage (files present that aren't registered)
6. Three-document rule for muscles (`docs/tools/<muscle>/blueprint+guidance+test_record`) + `Approved: YES + date` stamp in test_record
7. Plaintext secret files anywhere in the tree (`.env`, `credentials.json`, `service_account.json`)

Complements `registry/validate_tool_docs.py`, which is a narrower pre-commit gate for approved-tool docs coverage. The compliance checker is the broader audit run.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--root` | path | no | Apex repo root. Default: parent of `registry/`. |
| `--report-dir` | path | no | Where to write JSON detail. Default: `<root>/audit/compliance/`. |
| `--quiet` | flag | no | Suppress human-readable stdout. JSON still written. |
| `--strict` | flag | no | Treat warnings as failures (non-zero exit). |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | text | Human-readable summary + top items per category unless `--quiet` |
| file | JSON | `<report-dir>/<UTC-timestamp>.json` with `summary`, `fails`, `warns`, `details` |
| exit code | integer | `0` clean, `1` violations, `2` errors during check |

## What counts as FAIL vs WARN

| Bucket | Examples | Default exit |
|---|---|---|
| FAIL | duplicate refs, header/register mismatch, registered-but-missing on disk, invalid ref format | exit 1 |
| WARN | stale path remap, unregistered disk file, muscle missing 3-doc trio, secret on disk | exit 0 (exit 1 if `--strict`) |

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Python 3.10+ | runtime | `dataclasses(slots)`-free; works on stock Windows Python 3.11/3.13 |
| stdlib only | — | `argparse`, `json`, `re`, `dataclasses`, `pathlib`, `datetime`. No third-party deps. |
| `docs/DOCUMENT_REGISTER.md` | input | Must exist or exit 2 with FATAL |
| Write access to `audit/compliance/` | filesystem | Created if missing |

## How It Works

1. Parses `docs/DOCUMENT_REGISTER.md` (pipe-table rows, skipping headers/separators).
2. Validates each row's ref code against `^[A-Z]{2,6}-[A-Z]{2,4}-[A-Z]{2,4}-\d{5}$`.
3. Resolves each register `path` cell through `remap_path()` which handles legacy roots (`C:\Users\bermi\Projects\apex`, `\\192.168.50.246\Automations\apex`, `/apex/`, `C:\Users\Owner\apex_governance`) and absolute paths.
4. Walks `registry/*.py` + repo-root `*.py`, extracts the `Ref:` header from each docstring, and reconciles with register paths.
5. Globs the documented set of governance-relevant disk artifacts and flags any not in the register.
6. For each `registry/muscle_*.py` checks the three-doc trio + the `Approved: YES YYYY-MM-DD` stamp.
7. Walks for plaintext secrets (`.env`, `credentials.json`, `service_account.json`).
8. Writes JSON detail; prints summary unless quiet.

## Limitations and Edge Cases

- Only the register file is parsed for canonical state. Tools approved but missing from `DOCUMENT_REGISTER.md` will appear as `unregistered disk files`.
- `STALE_PREFIXES` is a constant list of known legacy roots; new legacy locations need source edit.
- Secret detection is filename-based only (does NOT scan file contents for inline secrets). Treats false negatives as acceptable cost vs scanning cost.
- Does not understand `git` — both tracked and untracked files are walked.
- The skip set is `{"compliance", "clones"}` plus rg-like behavior on globs; not configurable from CLI.

## Calling Convention

Default (audit run with stdout summary):
```powershell
python registry/muscle_compliance_check.py
```

Quiet (CI / cron):
```powershell
python registry/muscle_compliance_check.py --quiet
```

Strict (treat warnings as failures, for pre-commit hooks):
```powershell
python registry/muscle_compliance_check.py --quiet --strict
```

Custom root (for repo-comparison runs):
```powershell
python registry/muscle_compliance_check.py --root "C:\path\to\other\apex" --report-dir "C:\tmp\compliance"
```

## Apex WorkOrder Use

This tool is the broader compliance audit. Recommended call sites:
- Manual pre-PR audit (read summary, decide whether to fix or document).
- Daily cron / scheduled job (write JSON detail to `audit/compliance/`, alert only on FAIL count > 0 OR secret-on-disk count > 0).
- After bulk register edits (catch ref-code drift introduced by manual merges).

Pairs well with `validate_tool_docs.py` which is the narrower pre-commit gate for approved-tool doc coverage only.

## Promotion Provenance

Promoted from the parallel Claude WIP run per `docs/APEX_PARALLEL_MERGE_PLAYBOOK.md` step 3, batch #1. The source file's existing header carried `Ref: APEX-SYS-PY-00001` (stub); Codex to overwrite with the real allocated `APEX-MB-PY-00028` (or next available number per doc_controller).
