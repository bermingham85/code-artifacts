# AGEN Task Lineage Migration Test Plan v1

| Field | Value |
|---|---|
| Ref Code | AGEN-SYS-TST-00004 |
| Version | 1.0 |
| Status | DRAFT - not production applied |
| SQL | `AGEN-SCRPT-task-lineage-migration-v1.sql` |

## Scope

This test plan covers the local draft migration for future-only lineage between `agent_tasks` and `agent_architectures.tasks[*]`.

## Non-Negotiable Safety

- Do not use `JESS` rows as test fixtures.
- Do not backfill existing `agent_tasks`.
- Do not apply to production until backup/export evidence and operator approval exist.
- Run `python registry\supabase_project_guard.py --expect-code APEX` before any live write test.

## Tests

| ID | Test | Expected Result |
|---|---|---|
| TL-001 | Apply migration to disposable database matching live schema. | Columns, constraints, indexes, and helper function are created idempotently. |
| TL-002 | Re-apply migration to the same disposable database. | No duplicate columns, constraints, indexes, or function errors. |
| TL-003 | Existing legacy `agent_tasks` rows with no lineage. | Rows remain unchanged with `architecture_id IS NULL`. |
| TL-004 | Call `materialize_architecture_tasks` for an APEX/AGEN architecture with two valid decomposition tasks. | Two `agent_tasks` rows appear with `architecture_id`, `decomposition_task_id`, `inputs`, `outputs`, `dependencies`, `component`, and `estimated_hours`. |
| TL-005 | Re-call helper for the same architecture. | Same rows update idempotently by `(architecture_id, decomposition_task_id)`; no duplicates. |
| TL-006 | Architecture task has missing or non-UUID `task_id`. | Helper raises and no task rows are written. |
| TL-007 | Architecture belongs to protected `JESS` project. | Helper raises `protected_project_refuses_task_materialization`; no Jesse rows are written. |
| TL-008 | Decomposition dependencies are projected into `agent_tasks.dependencies` and translated into `agent_task_dependencies`. | Projection exists for context, and canonical dispatch graph rows are recreated for materialized architecture tasks. |
| TL-009 | Add required `PERFORM materialize_architecture_tasks(v_new_id);` inside `create_architecture_revision` on a disposable database. | Architecture revision, task fan-out, and dependency translation succeed in one transaction. |
| TL-010 | Force helper failure through invalid decomposition after RPC patch. | Entire RPC transaction rolls back; no partial architecture/task pair remains. |
| TL-011 | Service role grants only. | `anon` and `authenticated` cannot execute helper; `service_role` can. |
| TL-012 | Supabase project guard. | Guard returns target `APEX` and protected project `JESS` without printing secrets. |

## Production Gate

The draft is not production-ready until Codex review signs off the DDL, helper semantics, required RPC patch, rollback plan, and consumer prompt/workflow updates.
