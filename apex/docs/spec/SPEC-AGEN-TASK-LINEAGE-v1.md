# SPEC-AGEN-TASK-LINEAGE-v1

| Field | Value |
|---|---|
| Ref Code | AGEN-SYS-DOC-00007 |
| Version | 1.0 |
| Status | DRAFT - pending operator approval and live schema inspection |
| Purpose | Give every buildable `agent_tasks` row a stable link to the architecture decomposition entry that produced it. |

## Contract

`agent_tasks` MUST expose deterministic lineage to `agent_architectures.tasks[*]` without requiring prompt/name matching.

## Inputs

- `agent_architectures.id`, `project_id`, `spec_id`, and `tasks[*]`.
- Each decomposition task's `task_id`, `name`, `description`, `inputs`, `outputs`, `dependencies`, `component`, and `estimated_hours`.
- Existing `agent_tasks` rows, including legacy rows with no architecture lineage.

## Outputs

- Nullable lineage from `agent_tasks` to the source architecture revision and decomposition task id.
- Structured task fields available directly or through one documented canonical projection.
- One documented dependency model for Router, Builder, Verification, and future agents.

## Binary Definition Of Done

- Builder, Verification, and Router can resolve task `inputs`, `outputs`, `component`, and `dependencies` without heuristic title/name matching.
- Legacy and non-Architecture-authored tasks remain valid with null lineage.
- Live schema inspection, backup, rollback, idempotency, RLS, and migration tests are attached before any production migration.
