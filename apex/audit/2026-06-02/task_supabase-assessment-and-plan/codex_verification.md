# Codex Verification - Supabase Shared Boundary

| Field | Value |
|---|---|
| Ref | APEX-MB-AUD-00001 |
| Date | 2026-06-02 |
| Mode | Read-only Supabase REST/OpenAPI verification |
| Supabase project ref | `ylcepmvbjjnwmzvevxid` |
| Secrets printed | No |
| Rows dumped | No |

## Verified From This Context

| Fact | Result |
|---|---|
| Public definitions visible through PostgREST/OpenAPI | 109 |
| `agent_projects` rows | 11 |
| `agent_tasks` rows | 283 |
| `agent_tasks.last_review_at` exists | yes |
| `agent_tasks.last_review_at` non-null rows | 283 |
| `conv_processed` rows | 41 |
| `conv_raw` rows | 42 |

## Live Projects

| Code | Name | Status |
|---|---|---|
| `AGEN` | Agent Build System | active |
| `APEX` | Apex Autonomous Delivery | active |
| `BERM` | Bermech Ltd / Airbnb | active |
| `BPIG` | The Balding Pig | active |
| `FINX` | Financial Automation | active |
| `GNRL` | General | active |
| `GOVN` | Governance | active |
| `INFR` | Infrastructure | active |
| `JESS` | Jesse Music / Novel Factory | active |
| `MILK` | Milka Musical | active |
| `TALE` | Taleweaver | active |

## Claude-Reported Items Not Fully Verifiable Here

Claude reported that Supabase tooling flagged 71 public tables with RLS disabled and broad anon/authenticated exposure. This managed Codex context can verify table/project/column facts through PostgREST metadata, but it cannot inspect `pg_class`, `pg_policy`, role grants, or Supabase security-advisor output without a SQL execution route.

Treat the RLS advisory as critical until disproven by SQL-side verification. Do not auto-enable RLS without policies because that can break n8n workflows, conv ingestion, audio/video pipelines, and shared automation services.

## Boundary Correction

The database is not APEX-only. It is a shared Supabase instance hosting at least 11 projects. APEX work may use shared coordination infrastructure only when scoped and documented. Non-APEX content tables are protected unless an explicit work order names that project.
