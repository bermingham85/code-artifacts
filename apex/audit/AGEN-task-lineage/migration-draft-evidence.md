# AGEN Task Lineage Migration Draft Evidence

| Field | Value |
|---|---|
| Work order | `WO-APEX-AGEN-TASK-LINEAGE-IMPLEMENT-007` |
| Timestamp | 2026-05-30 |
| Mode | Local draft only |
| Production Supabase migration applied | No |
| Existing JESS rows changed | No |
| Default coordination project | `APEX` |
| Review verdict | Local draft improved; runtime validation still blocked |
| Live APEX task status | blocked - SQL execution route required |
| Nested draft branch | `codex/agen-task-lineage-draft` |
| Nested draft commit | `bd7f440` |

## Files

| File | Purpose |
|---|---|
| `registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/AGEN-SCRPT-task-lineage-migration-v1.sql` | Local SQL draft for future-only task lineage. |
| `registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/AGEN-TEST-task-lineage-migration-v1.md` | Test plan for disposable database validation before production. |

The draft files were committed to the nested `code-artifacts` clone on branch `codex/agen-task-lineage-draft`, latest commit `bd7f440`, because `apex/registry/clones/` is intentionally ignored by the parent Apex repo.

## Decisions

- Existing `agent_tasks` rows remain untouched.
- No heuristic backfill is included.
- `agent_task_dependencies` remains canonical for dispatch and is now populated from valid same-architecture decomposition dependency ids by the local draft.
- `agent_tasks.dependencies` is only a projection of decomposition dependencies.
- The helper blocks `JESS` materialization unless a later approved Jesse-specific packet changes that policy.
- The Architecture RPC source draft now includes `PERFORM materialize_architecture_tasks(v_new_id);` in the same transaction path.

## Remaining Gate

Codex CLI is installed, but a non-interactive external review attempt was blocked by the safety layer because it would send private workspace files to an external service. The next evidence item must be either explicit operator approval for that named-file review or a local/offline review route.

Local review findings are recorded at `audit/codex_review/AGEN-task-lineage-implement/findings.md`.

Live production apply remains blocked in this environment because only Supabase REST API keys are available. No `psql`, Supabase CLI, database URL, or SQL execution route was available during this pass.
