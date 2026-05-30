# AGEN Task Lineage Design v1

| Field | Value |
|---|---|
| Ref Code | AGEN-SYS-DOC-00008 |
| Version | 1.0 |
| Status | DRAFT - implementation gated |
| Parent review | `WO-APEX-AGEN-TASKS-SCHEMA-REVIEW-006` |
| Spec | `docs/spec/SPEC-AGEN-TASK-LINEAGE-v1.md` |

## Decision

Adopt the task-lineage direction, but do not apply any migration from the earlier scope draft. The accepted root-cause target is stable lineage between `agent_tasks` and `agent_architectures.tasks[*]`; the implementation owner, backfill strategy, and dependency translation must be finalized in a separate implementation packet after live read-only schema inspection.

## Problem

`agent_tasks` is the operational work queue. `agent_architectures.tasks` contains richer decomposition data: `task_id`, `inputs`, `outputs`, `dependencies`, `component`, and sizing metadata. Current Builder materials still describe matching task rows back to architecture entries by id or name heuristic. That makes every consumer re-solve the same bridge and keeps the failure mode alive.

## Preferred Direction

Use additive nullable lineage on `agent_tasks`:

| Field | Purpose |
|---|---|
| `architecture_id` | Links to the architecture revision that emitted the decomposition task. |
| `decomposition_task_id` | Stores `agent_architectures.tasks[*].task_id`; distinct from `agent_tasks.id`. |
| `inputs`, `outputs`, `component`, `estimated_hours` | Structured build context, either canonical or cached projection. |
| `dependencies` | Only acceptable if its relationship to `agent_task_dependencies` is explicitly defined. |

Legacy rows and manually created work orders keep null lineage. Downstream agents must handle null lineage gracefully.

## Ownership Options

| Option | Owner | Status |
|---|---|---|
| Architecture RPC fan-out | `create_architecture_revision` inserts/updates `agent_tasks` in the same transaction. | Viable only if Architecture prompt, workflow, and tests are updated to own task fan-out. |
| PM/Router fan-out | Architecture stays pure; PM or Router materializes task rows from latest architecture. | Viable if PM/Router becomes the single canonical task writer. |
| Read projection only | View/RPC joins `agent_tasks` to architecture jsonb. | Not preferred unless write ownership cannot be changed; it leaves indexing and bulk-read costs. |

The implementation packet must pick exactly one owner. Split ownership is not allowed.

## Dependency Rule

The existing `agent_task_dependencies` table is the canonical dependency graph when dispatching real `agent_tasks.id` rows. If a jsonb `dependencies` field is added to `agent_tasks`, it must be documented as one of:

- A non-canonical projection copied from the architecture decomposition, resolved through `(architecture_id, decomposition_task_id)`.
- A temporary staging field that is translated into `agent_task_dependencies`.
- A deprecated field that is not added.

Router must not read two unreconciled dependency models.

## Backfill Rule

Backfill is operator-gated. The implementation packet must choose one mode:

| Mode | Behavior | Risk |
|---|---|---|
| Future-only | New architecture revisions create lineage; old rows stay untouched. | Leaves legacy manual bridge for old work. |
| Annotate existing | Match and update existing task rows where deterministic. | Requires strong matching proof. |
| Emit missing tasks | Create pending tasks from non-superseded architecture rows. | Can duplicate work if old tasks already exist. |

Default safe mode is future-only unless live evidence proves deterministic matching.

## Migration Constraints

- No migration runs from this design note.
- Run Apex work gate before repository edits.
- Run read-only live Supabase schema inspection before writing SQL.
- Take backup/export evidence before migration.
- Use tested idempotent DDL; avoid `ADD CONSTRAINT IF NOT EXISTS`.
- For partial unique indexes, conflict handling must include a tested matching predicate or use a different unique strategy.
- Preserve RLS and service-role-only write boundaries.
- Preserve null lineage for legacy and manual rows.

## Implementation Packet Shape

The next Codex packet should include:

1. Live read-only schema evidence for `agent_tasks`, `agent_architectures`, `agent_task_dependencies`, Router, Builder, and Verification tables.
2. Chosen writer owner and required prompt/workflow/test updates.
3. SQL migration with rollback and idempotency proof.
4. Test cases for legacy null lineage, duplicate replay, dependency translation, RLS, and consumer reads.
5. Evidence that Builder, Verification, and Router no longer require heuristic task matching.

## Open Risks

- Live Supabase state may differ from local governed materials.
- Existing untracked scope draft remains unpromoted.
- External research was not performed here because Perplexity Pro was unavailable in this Codex context.
- Operator approval is still required before any schema migration or production workflow change.
