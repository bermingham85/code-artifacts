# AGEN Task Lineage Migration Draft Review

| Field | Value |
|---|---|
| Review type | Local deterministic review after Codex CLI external review was blocked |
| Timestamp | 2026-05-30 |
| Verdict | REVISE before production |
| Production migration approved | No |
| Draft branch | `codex/agen-task-lineage-draft` |
| Draft commit | `92d8189` |

## Findings

### HIGH - RPC fan-out is not implemented yet

File: `registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/AGEN-SCRPT-task-lineage-migration-v1.sql`

The draft creates `materialize_architecture_tasks(UUID)` and documents the required `PERFORM materialize_architecture_tasks(v_new_id);` call, but it does not replace or patch `create_architecture_revision`. That means Architecture RPC fan-out is not actually implemented by this SQL yet. This is acceptable only as a draft marker, not as a production migration.

Required fix: replace `create_architecture_revision` with the materialization call inside the same transaction, then rerun disposable-database tests TL-009 and TL-010.

### HIGH - Dependency translation is not canonical yet

File: `registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/AGEN-SCRPT-task-lineage-migration-v1.sql`

The draft projects decomposition dependencies into `agent_tasks.dependencies`, but does not translate them into `agent_task_dependencies`. The policy says `agent_task_dependencies` remains canonical for dispatch, so Router cannot rely on this migration alone for dependency gating.

Required fix: either add deterministic translation from decomposition ids to materialized `agent_tasks.id` rows and populate `agent_task_dependencies`, or explicitly defer Router dependency gating until a second reviewed migration.

### MEDIUM - Codex CLI review not completed in this context

File: `audit/AGEN-task-lineage/migration-draft-evidence.md`

The installed Codex CLI was detected, but a non-interactive external review attempt was blocked by the safety layer because it would send private workspace files to an external service. This requires explicit operator approval before retrying that exact path.

Required fix: operator must explicitly approve sending the named migration/spec files to Codex CLI, or use a local/offline review route.

## Passed Local Checks

- Work order JSON parses.
- The unsafe `ADD CONSTRAINT IF NOT EXISTS` pattern is absent.
- Existing rows are not backfilled by the draft.
- `JESS` protection exists in policy and helper logic.
- `agent_tasks` status and priority values used by the helper match the Project Manager migration constraints.

## Next Decision

Do not apply this migration to production. The next safe implementation step is to patch the actual Architecture RPC and add canonical `agent_task_dependencies` translation in a disposable/local draft.
