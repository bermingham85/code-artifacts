# CONV-PROC Build Log

**Build Date:** 2026-04-04
**Builder:** Claude Code (APEX Autonomous Build)

---

## Phase 1 — Audit & Anchor
- [x] Supabase tables `conv_raw`, `conv_processed`, `conv_routing_log` verified (migration `20260404061932`)
- [x] GitHub repo `bermingham85/code-artifacts` cloned and inspected
- [x] GOVERNANCE.md loaded (v4.0, AGEN-GOVN-001)
- [x] NAS path `/share/Automations/apex/` not accessible from Windows host — all artifacts built locally in repo
- [x] Naming convention confirmed: CONV-PROC-MICH-{TYPE}-{SEQ5}

## Phase 2 — Ingestion Layer
- [x] Built `conv-proc-ingest` edge function
- [x] Supports: Claude JSON exports, markdown transcripts, plain text
- [x] SHA-256 deduplication
- [x] Deployed to Supabase: `61ba5469-9655-4a12-a459-a4476dd3676c` (ACTIVE)

## Phase 3 — Extraction Engine
- [x] Built `conv-proc-extract` edge function
- [x] Uses Claude Sonnet 4.6 via Anthropic API
- [x] Extracts: tasks, skills, memory_updates, n8n_ideas, supabase_changes
- [x] Deployed to Supabase: `c099a0e5-2e40-4d50-bef1-db561e6d41df` (ACTIVE)

## Phase 4 — Routing Layer
- [x] Built `conv-proc-router` edge function
- [x] Routes to n8n webhooks: apex-task-intake, apex-skill-register, apex-memory-update, apex-n8n-idea
- [x] Supabase changes queued for human review (safety)
- [x] Telegram notifications on batch completion
- [x] Deployed to Supabase: `e8330364-c45e-458e-abf4-629d107b446f` (ACTIVE)

## Phase 5 — Self-Expansion Hook
- [x] Built `conv-proc-expand` edge function
- [x] Pattern detection across conversations (threshold: 3+ occurrences)
- [x] Auto-generates skill and n8n workflow stub records
- [x] Deployed to Supabase: `9cb27cc9-f619-47e5-b150-2ddefb2fec98` (ACTIVE)

## Phase 6 — Governance & Registration
- [x] All 4 edge functions deployed and ACTIVE
- [x] DOCUMENT_REGISTER.md created at `docs/DOCUMENT_REGISTER.md`
- [x] Spec written: CONV-PROC-MICH-SPEC-00001.md
- [x] n8n orchestrator workflow stub created
- [x] n8n task intake workflow stub created
- [x] Build log written

## Phase 7 — Hardening & Automation (2026-04-05)
- [x] Migration `fix_conv_proc_constraints`: expanded conv_routing_log route_type (added auto_skill, auto_n8n_stub, memory_updates) and status (added auto_generated, queued_for_review); expanded conv_processed status (added partially_routed)
- [x] Router v3: direct Supabase fallback — when n8n webhooks unreachable, tasks insert directly to `agent_tasks`, memories to `agent_memories`, skills/ideas stored in routing log
- [x] Router: correct project_id `eaf643c4-073f-40b2-a23e-7a76d043d9cd` (Infrastructure) for direct task inserts
- [x] Router: type-mapping functions for agent_memories constraints (mapMemoryType, mapMemoryCategory)
- [x] All 4 edge functions redeployed as v2 (ingest, extract, expand) / v3 (router)
- [x] Scheduled task `conv-proc-orchestrator` created — runs every 6 hours via Claude Code scheduled tasks
- [x] Pipeline is now fully self-contained: n8n is optional, Supabase fallback handles all routing

## Decisions Made
1. **Supabase changes routed to review queue, not auto-applied** — DDL from conversation extraction is too risky to auto-apply
2. **NAS artifacts deferred** — NAS not accessible from this host; all artifacts in GitHub repo for sync later
3. **n8n workflows as JSON stubs** — n8n API not accessible from edge functions; stubs ready for manual import at 192.168.50.246:5678
4. **JWT auth enabled on all edge functions** — Governance requires authenticated access
5. **ANTHROPIC_API_KEY must be set** — Required as Supabase project secret for extraction to work
6. **Direct Supabase fallback over n8n dependency** — Router tries n8n first but falls back to direct DB inserts, making pipeline resilient to n8n downtime
7. **Scheduled task replaces n8n orchestrator** — Claude Code scheduled task (every 6h) replaces the n8n orchestrator workflow for triggering the pipeline
