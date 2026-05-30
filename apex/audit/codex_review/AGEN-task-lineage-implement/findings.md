# AGEN Task Lineage Migration Draft Review

| Field | Value |
|---|---|
| Review type | Local deterministic review after Codex CLI external review was blocked |
| Timestamp | 2026-05-30 |
| Verdict | LOCAL DRAFT IMPROVED - runtime validation still required |
| Production migration approved | No |
| Draft branch | `codex/agen-task-lineage-draft` |
| Draft commit | `bd7f440` |

## Findings

### RESOLVED IN DRAFT - RPC fan-out source is now wired

File: `registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/AGEN-SCRPT-task-lineage-migration-v1.sql`

Earlier draft created `materialize_architecture_tasks(UUID)` and only documented the required `PERFORM materialize_architecture_tasks(v_new_id);` call. Nested commit `bd7f440` updates the Architecture migration source to call the helper after `root_architecture_id` is set and before the final return.

Remaining validation: run disposable-database tests TL-009 and TL-010 before production apply.

### RESOLVED IN DRAFT - Dependency translation is now canonicalized

File: `registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/AGEN-SCRPT-task-lineage-migration-v1.sql`

Earlier draft projected decomposition dependencies into `agent_tasks.dependencies` but did not translate them into `agent_task_dependencies`. Nested commit `bd7f440` validates dependency ids against same-architecture decomposition tasks and recreates canonical `agent_task_dependencies` rows for materialized architecture tasks.

Remaining validation: run disposable-database tests TL-008, TL-009, and TL-010 before production apply.

### BLOCKED - Codex CLI external review not completed in this context

File: `audit/AGEN-task-lineage/migration-draft-evidence.md`

The installed Codex CLI was detected, but a non-interactive external review attempt was blocked by the safety layer because it would send private workspace files to an external service. A second attempt after broad operator approval was also rejected by the tenant policy.

Required fix: use a local/offline review route or run Codex CLI directly from an operator terminal outside this managed agent context.

### BLOCKED - Live SQL apply route unavailable here

File: `audit/AGEN-task-lineage/migration-draft-evidence.md`

This context has Supabase REST API keys only. No `psql`, Supabase CLI, database URL, or SQL execution route is available, so the migration cannot be applied or disposable-tested from here.

Required fix: provide a SQL execution route or run the pushed draft branch through the Supabase SQL editor/CLI after backup/export evidence exists.

## Passed Local Checks

- Work order JSON parses.
- The unsafe `ADD CONSTRAINT IF NOT EXISTS` pattern is absent.
- Existing rows are not backfilled by the draft.
- `JESS` protection exists in policy and helper logic.
- `agent_tasks` status and priority values used by the helper match the Project Manager migration constraints.
- Architecture RPC source includes the materializer call in the draft branch.
- Dependency ids are validated and translated into `agent_task_dependencies` in the draft branch.

## Next Decision

Do not apply this migration to production from this context. The next safe implementation step is disposable-database execution of branch `codex/agen-task-lineage-draft` commit `bd7f440`, then backup/export evidence and operator-approved production apply.
