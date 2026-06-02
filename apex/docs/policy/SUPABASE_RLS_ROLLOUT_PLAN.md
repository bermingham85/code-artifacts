# Supabase RLS Rollout Plan

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00039 |
| Version | 1.0 |
| Status | DRAFT |
| Created | 2026-06-02 |
| Purpose | Safe plan for resolving the reported shared Supabase RLS exposure without breaking production workflows. |

## Current Advisory

Claude reported that Supabase tooling flagged 71 public tables with RLS disabled and broad anon/authenticated exposure. Codex could not verify that count through PostgREST metadata. Treat it as critical pending SQL-side confirmation.

## Hard Rule

Do not auto-run `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` across the database. Enabling RLS without policies may block n8n, conv ingestion, audio/video workflows, and app clients.

## Rollout Phases

| Phase | Output |
|---|---|
| RLS-0 Confirm | SQL-side table, policy, grant, and role exposure inventory. |
| RLS-1 Classify | Table owner map: APEX/shared/creative/finance/app/system. |
| RLS-2 Dependency | Active clients/workflows per table. |
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
