# RLS-0 Inventory — SQL-confirmed (extension to Codex's PostgREST verification)

| Field | Value |
|---|---|
| Ref | APEX-MB-AUD-00002 |
| Companion to | `audit/2026-06-02/task_supabase-assessment-and-plan/codex_verification.md` (APEX-MB-AUD-00001) |
| Mode | Read-only SQL via Supabase MCP (route Codex's managed context did not have) |
| Date | 2026-06-02 |
| Supabase project | `ylcepmvbjjnwmzvevxid` |
| Authority | `docs/policy/SUPABASE_RLS_ROLLOUT_PLAN.md` (RLS-0 Confirm phase) |
| Status | ACTIVE — SQL evidence captured here promotes the advisory from "pending SQL-side confirmation" to **CONFIRMED** |

## Top-line verified counts

| Metric | Value | Source |
|---|---|---|
| Total `public` tables | **101** | `pg_class` where `relkind='r'`, `nspname='public'` |
| RLS-enabled tables | 30 | `pg_class.relrowsecurity = true` |
| RLS-disabled tables | **71** | `pg_class.relrowsecurity = false` |
| RLS-enabled with at-least-one policy | 20 | `pg_policies` distinct tablename |
| **RLS-enabled but POLICY-LESS** | **10** | `rls_on \ policy_table` set difference |
| `anon` grants on all-priv (DELETE/INSERT/UPDATE/SELECT/REFERENCES/TRIGGER/TRUNCATE) | 108-109 tables | `information_schema.role_table_grants` |
| `authenticated` grants — same | 108-109 tables | same |
| `service_role` grants — same | 109 tables | same |
| **`anon` can DELETE/INSERT/UPDATE on RLS-disabled tables** | **71** | join of grants × rls-off set |
| `authenticated` — same | 71 | same |

**The advisory is correct.** Any actor possessing the public anon JWT can read, insert,
update, or delete every row in 71 public tables. The RLS-enabled 30 are protected by RLS
(20 with policies; 10 policy-less = service-role-only by design).

## RLS-enabled-but-policy-less (10 — intentional service-role-only)

| Table | Likely owner |
|---|---|
| `affiliate_conversions` | BERM/shegoo (currency app affiliate flow) |
| `bank_transactions` | FINX (financial automation; comment says "immutable raw transaction lines") |
| `churn_log` | BERM/shegoo |
| `currencies` | FINX |
| `entities` | FINX (comment: "legal/tax-reporting entities") |
| `financial_accounts` | FINX |
| `financial_documents` | FINX (comment names entity owners explicitly) |
| `parser_quarantine` | FINX (comment refs APEX-MB-DOC-00024) |
| `parser_runs` | FINX (comment refs parser lifecycle) |
| `parties` | FINX |

These are the financial + currency-app tables that already have RLS on without
policies — they're write-blocked except via `service_role`. Treat as locked.

## 71 RLS-disabled tables grouped by inferred project (per `SUPABASE_SHARED_PROJECT_BOUNDARY`)

### Shared APEX/multi-project coordination (15)

`agent_projects`, `agent_tasks`, `agent_task_dependencies`, `agent_sessions`,
`agent_memories`, `agent_logs`, `prompt_registry`, `task_queue`, `session_handovers`,
`migration_logs`, `audit_log`, `canon_audit_log`, `conv_n8n_ideas`, `conv_skills`,
`contexts`.

Note: the rest of `conv_*` (`conv_raw`, `conv_processed`, `conv_routing_log`, `conv_tasks`,
`conv_memories`) and `ai_audit` are already RLS-enabled with policies. The 2 conv outliers
above are inconsistent with the rest of the conv group — flag for owner audit.

### JESS content + world + character + audio + video pipeline (42)

- **World/series:** `series`, `series_worlds`, `worlds`, `locations`, `location_variants`, `story_arcs`, `scene_outlines`, `ideas`, `planning_conversations`
- **Chapters:** `chapters`, `chapter_content`, `scenes`, `content_blocks`, `script_outputs`
- **Characters:** `characters`, `character_voices`, `character_assets`, `character_lora_runs`, `character_gates`, `voiceover_productions`, `songs`, `canon_facts`
- **Prose review:** `passage_feedback`, `prose_evaluations`, `prose_violations`, `style_profiles`, `learning_insights`, `copyright_checks`, `content_quality_checks`, `prompt_versions`
- **Audio:** `music_productions`, `scene_cue_sheets`, `audio_markers`, `audio_mixes`, `sfx_productions`, `audio_production_rules`
- **Video:** `video_assets`, `qc_results`, `expansion_clips`, `assembly_queue`
- **Asset/import:** `drive_import_log`, `production_assets`

### JESS backups (12)

`voiceover_productions_backup`, `script_outputs_backup`, `content_blocks_backup`,
`scenes_backup`, `chapters_backup`, `location_variants_backup`, `locations_backup`,
`character_voices_backup`, `characters_backup`, `songs_backup`, `series_backup`,
`_content_blocks_backup`.

### FINX-adjacent personal (2)

`personal_projects`, `personal_assets`.

(`personal_projects`/`personal_assets` are NOT in the policy-less group, so they don't have RLS even enabled.)

## Confirmed-vs-still-needed for RLS-1 Classify

The boundary doc requires "Identify the owning project by `project_id`, project code, config
key prefix, workflow id, or documented table owner." For the 15 shared-coordination tables,
ownership is by `project_id` column — those tables can host rows from any of the 11 projects.
A non-APEX project may write to `agent_tasks`/`agent_memories`/etc.; APEX must NOT silently
overwrite or backfill across `project_id` boundaries.

For the 42 JESS content tables, name + table comment strongly suggests JESS (and child series:
Beanstalk, Oz, Milka, Balding Pig). Cross-check needed before any RLS+policy work:

- Sample row inspection (read-only) on 2-3 tables to confirm the JESS attribution.
- Comments on `books`, `series_worlds`, `personal_assets`, etc. (already partial) suggest the
  intended ownership but not necessarily the writer.

## What this inventory does NOT do

- Does not enable RLS anywhere.
- Does not write any policy.
- Does not touch grants.
- Does not modify any data.
- Does not promote this doc to LOCKED — `SUPABASE_RLS_ROLLOUT_PLAN.md` stays DRAFT until
  RLS-1 (Classify) and RLS-2 (Dependency) are complete.

## Recommended next gate (RLS-1)

Owner mapping per table needs a workflow + client inventory. The right next step is to
identify which clients hold the anon JWT and which tables each touches, so policies can be
designed without breaking pipelines. That's a Codex job per `APEX_ACTIVE_QUEUE` P1.

## Reproducible queries

```sql
-- RLS state counts
SELECT COUNT(*) FILTER (WHERE c.relrowsecurity) AS rls_on,
       COUNT(*) FILTER (WHERE NOT c.relrowsecurity) AS rls_off,
       COUNT(*) AS total
FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid
WHERE n.nspname='public' AND c.relkind='r';

-- 71 RLS-disabled table list
SELECT c.relname FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid
WHERE n.nspname='public' AND c.relkind='r' AND NOT c.relrowsecurity
ORDER BY c.relname;

-- RLS-on but policy-less
WITH rls_on AS (
  SELECT c.relname AS t FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid
  WHERE n.nspname='public' AND c.relkind='r' AND c.relrowsecurity
),
with_pol AS (SELECT DISTINCT tablename AS t FROM pg_policies WHERE schemaname='public')
SELECT rls_on.t FROM rls_on LEFT JOIN with_pol USING (t) WHERE with_pol.t IS NULL;

-- anon exposure on RLS-off tables
WITH rls_off AS (
  SELECT c.relname AS t FROM pg_class c JOIN pg_namespace n ON c.relnamespace=n.oid
  WHERE n.nspname='public' AND c.relkind='r' AND NOT c.relrowsecurity
)
SELECT g.grantee, COUNT(DISTINCT g.table_name)
FROM information_schema.role_table_grants g JOIN rls_off ON rls_off.t=g.table_name
WHERE g.table_schema='public' AND g.grantee IN ('anon','authenticated')
  AND g.privilege_type IN ('SELECT','INSERT','UPDATE','DELETE')
GROUP BY g.grantee;
```
