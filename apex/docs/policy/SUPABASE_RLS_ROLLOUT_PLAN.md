# Supabase RLS Rollout Plan

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00039 |
| Version | 1.1 |
| Status | DRAFT |
| Created | 2026-06-02 |
| Purpose | Safe plan for resolving the reported shared Supabase RLS exposure without breaking production workflows. |

## Current Advisory

Claude reported that Supabase tooling flagged 71 public tables with RLS disabled and broad anon/authenticated exposure. A SQL-side inventory captured through Claude's Supabase MCP route on 2026-06-02 confirmed the advisory: 101 public tables, 30 RLS-enabled, 71 RLS-disabled, and anon/authenticated write grants on the 71 RLS-disabled tables.

Evidence: `audit/2026-06-02/task_rls-0-postgrest-inventory/inventory.md` (APEX-MB-AUD-00002).

## Hard Rule

Do not auto-run `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` across the database. Enabling RLS without policies may block n8n, conv ingestion, audio/video workflows, and app clients.

## Rollout Phases

| Phase | Output |
|---|---|
| RLS-0 Confirm | SQL-side table, policy, grant, and role exposure inventory. |
| RLS-1 Classify | Table owner map: APEX/shared/creative/finance/app/system. Next packet: `hub/WO-APEX-SUPABASE-RLS-OWNER-MAP-008.json`. |
| RLS-2 Dependency | Active clients/workflows per table. Next packet: `hub/WO-APEX-SUPABASE-RLS-OWNER-MAP-008.json`. |
| RLS-3 Policy Draft | Least-privilege policy set per table group. |
| RLS-4 Staging Test | Disposable or staging execution with workflow smoke tests. |
| RLS-5 Production Batch | Small approved batches with rollback and evidence. |

## Minimum Evidence Before Production

- SQL inventory of RLS enabled/disabled state.
- Grants for anon, authenticated, and service_role.
- Existing policies per table.
- Table owner and dependent workflow.
- Backup/export path.
- Rollback SQL.
- Smoke test commands or workflow execution ids.

## Initial Table Groups

| Group | Handling |
|---|---|
| `conv_*` | Shared ingestion pipeline; do not alter until conv workflows are mapped. |
| `agent_*` | Shared coordination tables; policy design must respect project boundaries. |
| Financial/shegoo/bermcoin tables | Treat as separate application domain; do not alter under APEX task. |
| Creative/audio/video tables | Treat as separate content domain; do not alter under APEX task. |
| Config/state tables | Key-prefix ownership required before changes. |

## Current Status

RLS-0 is evidence-complete. RLS-1/RLS-2 remain open and must complete before any policy or production RLS change. Do not enable RLS, revoke grants, or alter policies until owner mapping, dependency mapping, rollback SQL, and workflow smoke tests are prepared.
