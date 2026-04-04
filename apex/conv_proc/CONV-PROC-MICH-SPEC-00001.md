# CONV-PROC Module Specification

**Document ID:** CONV-PROC-MICH-SPEC-00001
**Version:** 1.0
**Date:** 2026-04-04
**Status:** DEPLOYED
**Owner:** Michael Bermingham

---

## Overview

CONV-PROC is an autonomous conversation processing pipeline that ingests Claude conversation exports, extracts structured data via the Anthropic API, and routes outputs to the APEX ecosystem (n8n, Supabase, skills, memory).

## Architecture

```
conv_inbox/ ──► INGEST ──► conv_raw ──► EXTRACT ──► conv_processed ──► ROUTER ──► n8n webhooks
                                                                          │
                                                                          └──► EXPAND (pattern detection)
```

## Components

### 1. CONV-PROC-MICH-INGEST-00001
- **Type:** Supabase Edge Function (`conv-proc-ingest`)
- **Input:** POST with `{ files: [{ name, content }] }` or `{ name, content }` or raw text
- **Formats:** Claude JSON exports, markdown transcripts, plain text
- **Output:** Records in `conv_raw` table with status `pending`
- **Deduplication:** SHA-256 hash of content prevents duplicate ingestion

### 2. CONV-PROC-MICH-EXTRACT-00001
- **Type:** Supabase Edge Function (`conv-proc-extract`)
- **Model:** Claude Sonnet 4.6 via Anthropic API
- **Input:** Reads `conv_raw` records with status `pending`
- **Output:** `conv_processed` records with extracted:
  - `tasks[]` - actionable items with owner/project/priority
  - `skills[]` - reusable automation patterns
  - `memory_updates[]` - persistent facts
  - `n8n_ideas[]` - workflow automations
  - `supabase_changes[]` - schema/data changes (queued for review)
- **Batch size:** Configurable, default 5, max 10

### 3. CONV-PROC-MICH-ROUTER-00001
- **Type:** Supabase Edge Function (`conv-proc-router`)
- **Routes:**
  - tasks → `POST n8n/apex-task-intake`
  - skills → `POST n8n/apex-skill-register`
  - memory_updates → `POST n8n/apex-memory-update`
  - n8n_ideas → `POST n8n/apex-n8n-idea`
  - supabase_changes → `review_queue` (no auto-apply of DDL)
- **Logging:** All routing decisions recorded in `conv_routing_log`
- **Notifications:** Telegram summary after each batch

### 4. CONV-PROC-MICH-EXPAND-00001
- **Type:** Supabase Edge Function (`conv-proc-expand`)
- **Pattern detection:** Scans all processed conversations for recurring n8n ideas and skills
- **Threshold:** 3+ occurrences across conversations triggers auto-generation
- **Output:** Auto-generated skill and n8n workflow stub records in `conv_routing_log`

## Supabase Tables

| Table | Purpose |
|-------|---------|
| `conv_raw` | Raw ingested conversations with parsed structure |
| `conv_processed` | Extracted structured data from each conversation |
| `conv_routing_log` | Audit trail of all routing decisions |

## n8n Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| CONV-PROC Orchestrator | Schedule (every 6h) | Chains extract → route → expand |
| APEX Task Intake | Webhook `/apex-task-intake` | Receives tasks and inserts to `agent_tasks` |

## Environment Variables Required

- `SUPABASE_URL` (auto-set in edge functions)
- `SUPABASE_SERVICE_ROLE_KEY` (auto-set)
- `ANTHROPIC_API_KEY` (must be set in Supabase project secrets)
- `TELEGRAM_BOT_TOKEN` (for notifications)
- `TELEGRAM_CHAT_ID` (for notifications)

## Security

- All edge functions require JWT authentication (`verify_jwt: true`)
- Supabase changes are queued for human review, never auto-applied
- SHA-256 deduplication prevents duplicate processing
- Content is truncated to 100k chars before API calls

## Governance Compliance

- [x] Supabase tables audited before build
- [x] No duplicate tables created
- [x] All artifacts registered in Document Control
- [x] Naming convention followed: CONV-PROC-MICH-{TYPE}-00001
- [x] Complete solution - no TODOs or placeholders
- [x] Edge functions deployed and ACTIVE
- [x] n8n workflow stubs created for import
