# Supabase Shared Project Boundary

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00038 |
| Version | 1.0 |
| Status | ACTIVE |
| Created | 2026-06-02 |
| Purpose | Prevent APEX agents from treating the shared Supabase instance as APEX-only. |

## Rule

The Supabase instance `ylcepmvbjjnwmzvevxid` is shared. Agents must assess table ownership before writes, migrations, backfills, or RLS changes.

## Project Boundary

| Code | Project | Default APEX Treatment |
|---|---|---|
| `APEX` | Apex Autonomous Delivery | In scope for Apex coordination. |
| `INFR` | Infrastructure | Shared infrastructure; write only with explicit work order. |
| `GOVN` | Governance | Likely overlap; write only with explicit work order. |
| `GNRL` | General | Shared scratch; avoid unless explicitly scoped. |
| `AGEN` | Agent Build System | Separate project; use only for agent-build-system work. |
| `BERM` | Bermech Ltd / Airbnb | Separate project; protected. |
| `FINX` | Financial Automation | Separate project; protected. |
| `JESS` | Jesse Music / Novel Factory | Separate creative backlog; protected. |
| `MILK` | Milka Musical | Separate creative backlog; protected. |
| `TALE` | Taleweaver | Separate creative backlog; protected. |
| `BPIG` | The Balding Pig | Separate content/project backlog; protected. |

## Shared Coordination Tables

The `agent_*`, `ai_audit`, `conv_*`, and selected config/state tables may support multiple projects. These are not automatically APEX-owned.

Before writing to a shared table:

1. Identify the owning project by `project_id`, project code, config key prefix, workflow id, or documented table owner.
2. Refuse writes to protected project codes unless the current work order names that project.
3. Avoid cross-project backfills unless the migration packet proves the ownership rule and rollback.
4. Record row counts and affected project ids before and after any approved write.

## RLS Advisory

Claude reported on 2026-06-02 that Supabase tooling flagged 71 public tables with RLS disabled and broad anon/authenticated exposure. This is a critical security advisory, but it must not be auto-fixed by simply enabling RLS. Enabling RLS without policies can break existing pipelines.

Required safe route:

1. SQL-side confirm exact tables, policies, grants, and active clients.
2. Group tables by owner/project and runtime dependency.
3. Design least-privilege policies per group.
4. Test in disposable/staging where possible.
5. Roll out in small batches with rollback and workflow smoke tests.

## Current Verified Facts

Codex read-only verification on 2026-06-02 confirmed:

- 109 public definitions visible through PostgREST/OpenAPI.
- 11 rows in `agent_projects`.
- `agent_tasks.last_review_at` exists.
- 283 `agent_tasks` rows exist and 283 have `last_review_at` populated.
- 41 `conv_processed` rows and 42 `conv_raw` rows exist.

Detailed evidence: `audit/2026-06-02/task_supabase-assessment-and-plan/codex_verification.md`.
