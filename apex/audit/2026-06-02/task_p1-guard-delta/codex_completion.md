# P1 Guard Delta Completion

| Field | Value |
|---|---|
| Date | 2026-06-04 |
| Operator | Codex |
| Scope | File-only Supabase shared-boundary enforcement |
| Live database writes | None |

## Result

Implemented the P1 guard delta against `registry/supabase_project_guard.py`.

## Changes

- Protected project defaults now include `AGEN`, `BERM`, `FINX`, `JESS`, `MILK`, `TALE`, and `BPIG`.
- Shared infrastructure defaults now include `INFR`, `GOVN`, and `GNRL`.
- Shared infrastructure targets require `--allow-shared`.
- Guard execution requires `APEX_BOUNDARY_DOC_READ=APEX-MB-DOC-00038-v1.0` before contacting Supabase.
- Low-token context and task packet template now point future agents to the boundary-doc marker route.

## Evidence Required

## Evidence

| Check | Result |
|---|---|
| `python -m py_compile registry\supabase_project_guard.py` | Passed |
| Missing `APEX_BOUNDARY_DOC_READ` marker | Failed closed before Supabase key lookup; JSON included `boundary_doc_marker: MISSING_OR_STALE` and `secrets_printed: false` |
| `--expect-code APEX` with marker | Passed read-only metadata guard; target resolved to `APEX / Apex Autonomous Delivery`; `secrets_printed: false` |
| `--expect-code AGEN` with marker | Refused protected project target; `ok: false`; `secrets_printed: false` |
| `--expect-code INFR` with marker and no `--allow-shared` | Refused shared-infrastructure target; `ok: false`; `secrets_printed: false` |
| `--expect-code INFR --allow-shared` with marker | Passed only after shared-infra acknowledgement; `secrets_printed: false` |
| `python -m json.tool docs\templates\apex_task_packet_template.json` | Passed |

## Rollback

Revert the scoped commit that modified:

- `registry/supabase_project_guard.py`
- `docs/APEX_CONTEXT_INDEX.md`
- `docs/APEX_ACTIVE_QUEUE.md`
- `docs/policy/SUPABASE_PROJECT_ISOLATION.md`
- `docs/templates/apex_task_packet_template.json`
- `docs/DOCUMENT_REGISTER.md`
- `audit/2026-06-02/task_p1-guard-delta/codex_completion.md`

No live Supabase rollback is required because this task made no database changes.
