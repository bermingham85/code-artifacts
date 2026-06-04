# Apex Active Queue

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00036 |
| Version | 1.0 |
| Status | ACTIVE |
| Updated | 2026-06-04T15:11:41Z |
| Purpose | Low-token current-state page so Claude, Codex, and future contexts stop rediscovering completed work. |

## Read First Rule

After `docs/APEX_CONTEXT_INDEX.md`, read this file before opening any work order, transcript, audit folder, or untracked artifact.

Do not paste chat history between agents as the source of truth. Pull the branch and use committed files.

## Current Branch State

| Item | State |
|---|---|
| Branch | `apex/estate-seed-00004` |
| Latest required head | `d5a3678` or later |
| Claude continuation | Completed by commits `89daf2f`, `80197a5`, `7e456f7`; packet marked complete in `hub/WO-APEX-CLAUDE-CONTINUE-005.json`. |
| AGEN task schema review | Reviewed with verdict `REVISE` in `hub/WO-APEX-AGEN-TASKS-SCHEMA-REVIEW-006.json`. |
| AGEN task lineage spec | Created in `docs/spec/SPEC-AGEN-TASK-LINEAGE-v1.md`. |
| AGEN task lineage design | Created in `docs/policy/AGEN_TASK_LINEAGE_DESIGN_v1.md`. |
| Supabase APEX project boundary | Live project `APEX / Apex Autonomous Delivery` created with id `243bed23-67d6-4f69-b382-e771c57abed7`; `JESS` protected/read-only by policy. |
| Supabase shared-instance correction | Verified 11 `agent_projects`; the instance is shared and must not be treated as APEX-only. See `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md`. |
| Supabase shared project guard enforcement | Completed by P1 guard delta: `supabase_project_guard.py` now requires the boundary-doc marker, blocks protected project codes by default, and requires `--allow-shared` for shared infra codes. |
| Workspace noise triage | Completed P4 classification in `docs/APEX_WORKSPACE_MENU.md` v1.1 and `audit/2026-06-04/task_workspace-noise-triage/classification.md`; unrelated loose artifacts remain unstaged. |
| B-3 task review migration | Claude reported it applied before stop directive; Codex verified `agent_tasks.last_review_at` exists and 283/283 rows are populated. Treat as completed but audit-sensitive. |
| RLS security advisory | Claude reported Supabase flagged 71 public tables with RLS disabled. Codex could not verify via PostgREST; treat as critical pending SQL-side confirmation. Do not auto-enable RLS without policies. |
| conv_extract June 2 | Claude reported 5 new rows extracted, 0 failed; Codex verified current counts only: 41 `conv_processed`, 42 `conv_raw`. |
| AGEN task lineage migration draft | Local draft improved; nested draft branch `codex/agen-task-lineage-draft` commit `bd7f440`; no production migration applied. |
| SP-A.0 split | Still open only because SP-A.2 doctrine ratification is pending; do not redo SP-A.0 work. |

## Do Not Reprocess

- Do not re-run Claude continuation batches from `WO-APEX-CLAUDE-CONTINUE-005`.
- Do not promote `docs/spec/SCOPE-AGEN-AGENT-TASKS-SCHEMA-FIX-v1.md`; it is superseded by the compact spec and design note.
- Do not commit raw `audit/claude_codex_loop/*` attempts unless directly linked by a work order or certificate.
- Do not read, print, move, or stage secret-bearing files, especially `active_projects/bermcoin/.env`.
- Do not write new Apex automation rows into `JESS`; use `APEX` unless an approved work order explicitly names another project.
- Do not treat `agent_*`, `conv_*`, `ai_audit`, or `public.config` as APEX-only. They are shared coordination infrastructure until mapped otherwise.
- Do not auto-enable RLS across public tables. RLS requires owner mapping, policies, rollback, and workflow smoke tests.

## Active Next Actions

| Priority | Work | Owner | Gate |
|---|---|---|---|
| P0 | Supabase RLS exposure rollout: `docs/policy/SUPABASE_RLS_ROLLOUT_PLAN.md`. | Operator + SQL-capable agent | Critical advisory; needs SQL-side confirmation and staged policy rollout. |
| P2 | AGEN task-lineage implementation: `hub/WO-APEX-AGEN-TASK-LINEAGE-IMPLEMENT-007.json`. | Codex/operator SQL route | Local migration draft now includes Architecture RPC source wiring and canonical `agent_task_dependencies` translation. Re-check shared-boundary/RLS risk before any production DDL. |
| P3 | SP-A.2 doctrine ratification: run the doctrine silent-twice loop against `docs/doctrine/APEX_DOCTRINE_v1.0.md`. | Claude+Codex bridge | Codex adversarial/ship-gate tooling required. |

## Next Agent Command

Use this sequence instead of asking the user what to do next:

```powershell
git pull origin apex/estate-seed-00004
python registry\muscle_work_gate.py --repo . --intent write --fetch --allow-dirty
Get-Content docs\APEX_ACTIVE_QUEUE.md
```

Then pick the first active next action that is not blocked in the current environment.

## Current Blockers

| Blocker | Effect | Safe fallback |
|---|---|---|
| Production migration approval not yet granted | Cannot apply task-lineage SQL to live Supabase. | Draft SQL, rollback, tests, and Codex review packet only. |
| Shared Supabase instance hosts 11 projects | Cross-project writes/backfills can affect non-APEX work. | Require project/table owner mapping before writes. |
| Reported 71-table RLS exposure | Potential anon/authenticated data exposure across shared database. | Confirm with SQL-side inventory; design policies before enabling RLS. |
| Codex CLI external review blocked by tenant policy | Cannot claim independent external CLI review in this managed context. | Use local deterministic review findings, or run Codex CLI directly from an operator terminal outside this managed agent context. |
| No SQL execution route in this context | Cannot run DDL, disposable DB tests, or live migration from REST API keys alone. | Use Supabase SQL editor/CLI/psql with database connection after backup evidence. |
| No Perplexity Pro connector in this Codex context | Cannot satisfy external-research-first route here. | Record limitation; use local governed materials only. |
| SP-A.2 needs actual Codex adversarial/ship-gate loop | Cannot honestly mark doctrine `1.0-LOCKED` from local file edits alone. | Keep doctrine `1.0-PROVISIONAL` binding and leave SP-A.0 split open. |

## Handoff Sentence

Tell any Claude/Codex context: "Pull `apex/estate-seed-00004`, read `docs/APEX_CONTEXT_INDEX.md`, then `docs/APEX_ACTIVE_QUEUE.md`; do not use chat text as authority."
