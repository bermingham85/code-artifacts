# TEST RECORD - muscle_compliance_check

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00028 (proposed) |
| **Tested By** | Codex |
| **Test Date** | 2026-05-25 |
| **Overall Result** | PARTIAL - source defects fixed, promotion blocked by root estate findings |

## Test Environment

| Field | Value |
|---|---|
| OS | Windows |
| Workspace | `C:\Users\Owner\Repos\code-artifacts\apex` |
| Python | 3.13.12 |
| Report dir | `audit/compliance/` default; `C:\tmp\compliance_smoke\` custom-dir test |

## Codex Source Fixes Applied

| Fix | Root cause | Result |
|---|---|---|
| `apex/...` path remap | Register paths like `apex/registry/...` were resolved as `<repo>/apex/...` | Now remaps to repo root and reduced false missing-path findings |
| Approval stamp regex | Table-style stamps like `**Approved** | YES - 2026-05-23` were not recognized | Existing approved test records are now detected |
| Missing-register exit path | `--root` without a register printed FATAL then crashed while summarizing a non-existent report dir | Now exits cleanly without traceback |
| External/session/stale path handling | `<external>`, `N/A`, and `/shegoo` rows were classified as local missing files | Now treated as no-path/stale as appropriate |

## Test Cases

| Test | Result | Evidence |
|------|--------|----------|
| TC-001 Syntax validation | PASS | `python -m py_compile registry\muscle_compliance_check.py registry\claude_codex_loop.py` exited 0 |
| TC-002 Clean audit run | PASS WITH FINDINGS | `python registry\muscle_compliance_check.py` exits non-zero because it finds real estate issues; latest baseline evidence: `audit/compliance/2026-05-25T14-20-30Z.json` |
| TC-003 Quiet mode | PASS WITH FINDINGS | `python registry\muscle_compliance_check.py --quiet` produced no stdout and wrote JSON; exit non-zero due real findings |
| TC-004 Strict mode | PARTIAL | Strict mode was run before the final resolver tweak and exited non-zero as expected while findings exist; final rerun was blocked by local Codex usage/approval limit |
| TC-005 Missing register graceful exit | PASS | `--root C:\nonexistent\nowhere` reports `FATAL: register not found ...` without traceback after patch |
| TC-006 Custom report-dir | PASS WITH FINDINGS | JSON written to `C:\tmp\compliance_smoke\2026-05-25T14-19-09Z.json` |
| TC-007 Secret detection positive control | PASS | Temporary `tmp_secret_positive\.env` raised `secrets_on_disk` from 1 to 2 in `audit/compliance/2026-05-25T14-21-59Z.json`; temp file and folder were removed |
| TC-008 Idempotency | NOT COMPLETED | Multiple runs completed and wrote separate JSON files, but a clean same-code/same-counter pair after the final resolver patch was not rerun before the local usage limit |

## Current Baseline Findings

Latest baseline after resolver fixes: `audit/compliance/2026-05-25T14-20-30Z.json`.

| Counter | Value |
|---|---:|
| register_entries | 130 |
| registered_resolved | 92 |
| registered_missing | 4 |
| registered_stale_path | 26 |
| registered_external | 3 |
| duplicate_refs | 1 |
| header_register_mismatches | 8 |
| invalid_ref_format | 0 |
| unregistered_disk_files | 93 |
| muscles_missing_docs | 8 |
| muscles_unapproved | 1 |
| secrets_on_disk | 1 |

## Blocker Report

| Field | Value |
|---|---|
| Exact blocker | The checker works, but the estate is not clean enough to stamp the tool approved under the requested strict/no-secret gate |
| Why it blocks promotion | `secrets_on_disk=1`, duplicate refs, header/register mismatches, missing/stale paths, and older undocumented muscles are real root findings |
| Lowest-friction resolution | Run a separate document-control cleanup batch: move/ignore the existing `.env`, reconcile duplicate refs, fix header/register paths, and either document or archive old muscles |
| Safe fallback | Keep `muscle_compliance_check` as DRAFT and use it manually as a diagnostic report until the cleanup batch closes |
| Work that can continue | Batch 2 loop testing and Batch 3 doctrine/policy merge can continue independently |

**All tests passed:** NO
**Approved:** NO - BLOCKED 2026-05-25
