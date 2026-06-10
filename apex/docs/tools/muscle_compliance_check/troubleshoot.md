# TROUBLESHOOT - muscle_compliance_check

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00028 (proposed) |
| Tool | muscle_compliance_check |
| Version | 1.0 |
| Status | DRAFT |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Script parses | `python -c "import ast; ast.parse(open('registry/muscle_compliance_check.py').read())"` | No output, exit 0 |
| Register file exists | `Test-Path docs/DOCUMENT_REGISTER.md` | True |
| Audit dir writable | `New-Item -ItemType Directory -Force audit/compliance` | Directory present |
| Tool is approved | Check `registry/TOOL_INDEX.md` and `docs/APEX_TOOL_MENU.md` | Entry under Approved Tools |
| Output JSON well-formed | `python -c "import json,glob; json.load(open(sorted(glob.glob('audit/compliance/*.json'))[-1]))"` | No exception |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| `FATAL: register not found at ...` exit 2 | Wrong `--root` or repo not yet seeded | Confirm `docs/DOCUMENT_REGISTER.md` exists at expected path; pass `--root` explicitly | Re-run produces summary |
| Exit 1, `duplicate_refs > 0` | Two register rows OR two header refs share the same code | Open `docs/DOCUMENT_REGISTER.md`; mark older as SUPERSEDED with rationale row; OR fix the Python header | Re-run, `duplicate_refs = 0` |
| Exit 1, `header_register_mismatches > 0` | File path in register doesn't match the file on disk carrying that header ref | Decide canonical location; move file or update register path | Re-run, mismatch = 0 |
| `registered_missing > 0` for paths that DO exist | Path uses legacy root not in `STALE_PREFIXES` remap | Either edit the register row to current path, OR add the legacy prefix to the `remap_path()` mapping in source (then test + commit + reapprove) | Re-run, missing count drops |
| `secrets_on_disk > 0` | A `.env` / `credentials.json` / `service_account.json` was staged accidentally | DO NOT commit. Move file out of tree (or to `.gitignore`'d location), rotate the leaked secret, then re-run | Re-run, `secrets_on_disk = 0` |
| `muscles_missing_docs > 0` after promoting new muscle | Doc trio incomplete | Create `docs/tools/<muscle>/{blueprint,guidance,test_record,troubleshoot}.md` | Re-run, muscle no longer flagged |
| `muscles_unapproved > 0` with full trio | `test_record.md` lacks the literal `Approved: YES YYYY-MM-DD` stamp | Have Codex re-run tests and add the stamp | Re-run, count drops |
| `unregistered_disk_files` list huge | Repo accumulated WIP without registration | Decide per file: register OR move to a non-governed path OR delete | Re-run, list shrinks |
| Exit 2 with stack trace | Source code error (rare; stdlib only) | Read traceback; if regression, revert to last approved version | TC-001 syntax check passes |
| `registered_external > 0` warnings | Intentional entries pointing outside repo | Usually fine — document why in register `description` column | n/a (informational) |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created during APEX_PARALLEL_MERGE_PLAYBOOK promotion batch #1 | Operational doc gap; tool existed as WIP without governance | Drafted blueprint/guidance/test_record stub/troubleshoot per playbook | Test record completion + `validate_tool_docs --quiet` to be run by Codex |
| 2026-05-25 | `apex/...` register paths reported as missing even when files existed | Resolver treated repo-local `apex/...` as `<repo>/apex/...` | Added explicit `apex/` remap to repo root | Missing count dropped from 81 to single digits |
| 2026-05-25 | Approved table rows still reported as unapproved | Approval regex only handled colon-style `**Approved:** YES` text | Added table-style `**Approved** | YES` support | `muscle_replit_builder_packet` no longer false-flags |
| 2026-05-25 | Missing-register negative test printed FATAL then crashed | Main tried to list a report directory that was never created | Guarded report summary path when report dir does not exist | Missing-register test now exits without traceback |
| 2026-05-25 | External/session/stale rows counted as local missing files | `<external>`, `N/A`, and `/shegoo` handling was incomplete | Classified them as no-path or stale-path warnings | Missing count dropped again; stale count became more accurate |
