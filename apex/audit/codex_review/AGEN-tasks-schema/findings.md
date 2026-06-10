# TASK RESULT: WO-APEX-AGEN-TASKS-SCHEMA-REVIEW-006

- Task ID: WO-APEX-AGEN-TASKS-SCHEMA-REVIEW-006
- Status: pass
- Verdict: REVISE
- Result file: audit/codex_review/AGEN-tasks-schema/findings.md
- Reviewed item: docs/spec/SCOPE-AGEN-AGENT-TASKS-SCHEMA-FIX-v1.md
- Reviewed at: 2026-05-30T05:03:03Z

## Summary

The diagnosed schema gap is real and persistent in the local AGEN materials. `agent_tasks` remains a flat work-ticket table, while rich decomposition fields live in `agent_architectures.tasks` jsonb. Builder documentation still describes heuristic matching between a task row and an architecture task entry.

The draft should not be promoted as-is. The best next action is a revision packet: split the current document into a short PT9-compliant SPEC plus a separate design/policy note, then create a later implementation packet for migration work after operator approval and live schema inspection.

## Findings

| Severity | Finding | Evidence | Doctrine / contract impact | Required action |
|---|---|---|---|---|
| High | Draft exceeds the PT9 spec-complexity ceiling. It includes a full option matrix, SQL skeleton, backfill design, and operational commentary. | The file is about 297 lines and contains implementation SQL. | PT9 requires small per-phase specs focused on identity, inputs, outputs, and binary DoD. | Split into `SPEC-AGEN-TASK-LINEAGE-v1.md` <=30 lines and move design/migration notes to policy or research docs. |
| High | The recommended fan-out location changes the Architecture Agent contract. | Local Architecture prompt says the Architecture Agent writes `agent_architectures`, not canonical `agent_tasks`; Builder later bridges the gap. | R15/R16 contract stability: agent responsibilities must remain explicit and reviewable. | Either update Architecture prompt/workflow/spec to make fan-out an explicit responsibility, or move fan-out into PM/Router with a clear owner. |
| High | Dependency semantics are not reconciled with the existing `agent_task_dependencies` table. | PM migration already defines canonical task dependencies using `agent_tasks.id`; the scope proposes `agent_tasks.dependencies` jsonb using `decomposition_task_id`. | Creates two dependency models unless Router/PM semantics are explicitly mapped. | Define whether jsonb dependencies are only a projection or are translated into `agent_task_dependencies`; document Router behavior. |
| Medium | The SQL skeleton contains invalid/non-portable constraint idempotency. | `ALTER TABLE ... ADD CONSTRAINT IF NOT EXISTS` is used in the draft skeleton. | Migration reliability risk. | Use guarded `DO` blocks against `pg_constraint`, or another tested idempotent pattern. |
| Medium | Upsert/conflict semantics are incomplete for the proposed partial unique index. | The draft discusses `ON CONFLICT (architecture_id, decomposition_task_id)` while the unique index is partial. | Replay/idempotency may fail unless conflict inference exactly matches the partial predicate. | Specify and test `ON CONFLICT (architecture_id, decomposition_task_id) WHERE architecture_id IS NOT NULL AND decomposition_task_id IS NOT NULL`, or choose a different unique strategy. |
| Medium | Backfill semantics need operator choice. | The draft notes existing rows may have no lineage and proposes emitting new rows for non-superseded architecture tasks. | Could duplicate operational tasks or alter downstream queue semantics. | Decide whether backfill creates new pending tasks, annotates existing rows, or only applies to future architecture revisions. |
| Low | The named in-flight Builder task appears stale in local documentation. | Local Builder test plan marks `641341d9-cb61-4cde-9db3-55cb5e0c5bd9` complete. | Not a blocker for the schema issue, but the scope should not rely on it as current state. | Remove or update the in-flight-task claim before promotion. |
| Low | Live Supabase read-only inspection was not performed in this session. | No Supabase connector/credentials were available in this Codex context. | Review is based on local governed materials only. | Follow-on implementation packet should include read-only schema inspection evidence before migration. |

## Recommended Next Packet

Decision: REVISE.

Create a Claude revision packet with these outputs:

1. `docs/spec/SPEC-AGEN-TASK-LINEAGE-v1.md`
   - <=30 lines.
   - Identity: canonical task lineage between `agent_tasks` and `agent_architectures.tasks`.
   - Inputs: architecture revision, decomposition task entry, existing task row if any.
   - Outputs: stable lineage fields and dependency mapping.
   - Binary DoD: no prompt heuristic required for Builder/Verification/Router to find task inputs, outputs, component, and dependencies.

2. `docs/policy/AGEN_TASK_LINEAGE_DESIGN_v1.md`
   - Keep the option matrix, chosen owner, backfill policy, RLS notes, and migration rationale here.
   - State whether fan-out belongs to Architecture RPC or PM/Router.
   - Reconcile jsonb dependencies with `agent_task_dependencies`.

3. A later Codex implementation packet
   - Read-only Supabase schema inspection first.
   - No destructive migration without backup, rollback, and operator approval.
   - Migration must be idempotent and tested against local SQL review.

## Suggested Smallest Safe Direction

Option A is broadly the strongest direction, but only after revision:

- Add nullable lineage columns, especially `architecture_id` and `decomposition_task_id`.
- Add structured fields only if consumers are explicitly updated to treat them as canonical or cached projections.
- Choose one writer for fan-out and update that agent's contract.
- Translate dependencies into `agent_task_dependencies` or document jsonb dependencies as non-canonical projection.
- Keep legacy rows valid with null lineage.

## Files Changed

- Created: `audit/codex_review/AGEN-tasks-schema/findings.md`
- Updated: `hub/WO-APEX-AGEN-TASKS-SCHEMA-REVIEW-006.json`

## Commands / Evidence

- Read scope draft.
- Read work order packet.
- Reviewed local doctrine and AGEN agent materials by repository search.
- Work gate was run before review by the preceding step.

## Risks

- This is a document review only. It does not validate live Supabase state.
- External research through Perplexity Pro was not available in this Codex context.
- The untracked draft remains unpromoted pending Claude revision and operator approval.

## Rollback

- Remove this result file.
- Revert the appended status/verdict fields from `hub/WO-APEX-AGEN-TASKS-SCHEMA-REVIEW-006.json`.
- Leave `docs/spec/SCOPE-AGEN-AGENT-TASKS-SCHEMA-FIX-v1.md` untracked unless a later promotion packet explicitly says otherwise.
