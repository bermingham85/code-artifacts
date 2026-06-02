# Supabase Project Isolation Policy

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00037 |
| Version | 1.1 |
| Status | ACTIVE |
| Created | 2026-05-30 |
| Purpose | Keep Apex autonomous delivery work isolated inside a shared 11-project Supabase instance. |

## Shared Instance Correction

This Supabase instance is not APEX-only. It hosts at least 11 projects and shared coordination infrastructure. Use `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md` before any Supabase write, migration, backfill, RLS change, or config update.

## Live Project Boundary

| Code | Project | Role | Rule |
|---|---|---|---|
| `APEX` | Apex Autonomous Delivery | Current target for Apex orchestration, index/menu, governance, and autonomous delivery setup work. | New Apex records go here unless a more specific approved project is required. |
| `AGEN` | Agent Build System | Existing agent-build-system project. | Use only for agent-system records that must remain in AGEN. |
| `JESS` | Jesse Music / Novel Factory | Protected existing creative backlog. | Read-only unless the operator explicitly authorizes Jesse work. |

Current live `APEX` project id:

```text
243bed23-67d6-4f69-b382-e771c57abed7
```

## Write Rules

- Every new Apex-owned row inserted into `agent_tasks`, `agent_specifications`, `agent_architectures`, `agent_build_artifacts`, `agent_verifications`, or `agent_routing_logs` must use the `APEX` project id unless the work order explicitly names another project.
- `JESS` rows must not be updated, completed, backfilled, deleted, or used as migration test material during Apex/AGEN setup work.
- Database schema migrations can affect shared table structure, but content writes must remain scoped by `project_id`.
- Legacy rows with no new lineage remain valid. Do not guess a backfill link for old tasks.
- Any script that writes Supabase rows should first verify the target project code and refuse protected project codes.

## Guard Helper

Use the read-only guard before Supabase write scripts:

```powershell
python registry\supabase_project_guard.py --expect-code APEX
```

The guard reads project metadata only, confirms `APEX` exists, confirms protected projects such as `JESS` are visible, and never prints key values.

## Current APEX Seed Tasks

The live `APEX` project was seeded on 2026-05-30 with:

| Task | Status |
|---|---|
| APEX project isolation guard and Supabase setup | complete |
| Draft AGEN task-lineage migration with future-only rollout | blocked - local draft improved; SQL execution route required |
| Wire Apex coverpage index menu into future agent context | complete |
| Implement APEX Supabase write guard in workflows and scripts | complete |

## Operational Decision

Use `APEX` for the autonomous delivery build path going forward. Keep `JESS` as an existing live creative backlog, not a test fixture and not a default destination.
