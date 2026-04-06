# APEX Document Register

**Last Updated:** 2026-04-05
**Maintained By:** APEX Governance System

---

## CONV-PROC Module

| ID | Type | Name | Status | Location |
|----|------|------|--------|----------|
| CONV-PROC-MICH-SPEC-00001 | SPEC | Conversation Processor Specification | DEPLOYED | `apex/conv_proc/CONV-PROC-MICH-SPEC-00001.md` |
| CONV-PROC-MICH-INGEST-00001 | SCRPT | Ingestion Edge Function | ACTIVE | Supabase EF `conv-proc-ingest` + `apex/conv_proc/edge_functions/conv-proc-ingest/` |
| CONV-PROC-MICH-EXTRACT-00001 | SCRPT | Extraction Engine Edge Function | ACTIVE | Supabase EF `conv-proc-extract` + `apex/conv_proc/edge_functions/conv-proc-extract/` |
| CONV-PROC-MICH-ROUTER-00001 | SCRPT | Routing Layer Edge Function | ACTIVE | Supabase EF `conv-proc-router` + `apex/conv_proc/edge_functions/conv-proc-router/` |
| CONV-PROC-MICH-EXPAND-00001 | SCRPT | Self-Expansion Hook Edge Function | ACTIVE | Supabase EF `conv-proc-expand` + `apex/conv_proc/edge_functions/conv-proc-expand/` |
| CONV-PROC-MICH-WKFL-00001 | WKFL | Orchestrator n8n Workflow | STUB | `apex/conv_proc/n8n_stubs/conv-proc-orchestrator.json` |
| CONV-PROC-MICH-WKFL-00002 | WKFL | Task Intake n8n Workflow | STUB | `apex/conv_proc/n8n_stubs/conv-proc-task-intake.json` |

## Agent Build System

| ID | Type | Name | Status | Location |
|----|------|------|--------|----------|
| AGEN-GOVN-001 | GOVN | Agent System Governance Rules v4.0 | APPROVED | `AGENT_BUILD_SYSTEM/GOVERNANCE.md` |
| WO-APEX-PH08-001 | WKFL | Supervisor Watchdog Build & Certify | PENDING | `apex/hub/WO-APEX-PH08-001.json` |

## Supabase Migrations

| Migration | Date | Tables |
|-----------|------|--------|
| `create_conv_proc_tables` | 2026-04-04 | `conv_raw`, `conv_processed`, `conv_routing_log` |
| `fix_conv_proc_constraints` | 2026-04-05 | `conv_routing_log`, `conv_processed` (expanded check constraints) |

## Edge Function Versions

| Function | Current Version | Last Deployed | Key Changes |
|----------|----------------|---------------|-------------|
| `conv-proc-ingest` | v5 | 2026-04-05 | SHA-256 dedup, multi-format support |
| `conv-proc-extract` | v7 | 2026-04-05 | Model: claude-sonnet-4-5-20250929, status fix (extracted not processed) |
| `conv-proc-router` | v7 | 2026-04-05 | 5s webhook timeout, direct Supabase fallback, type mapping |
| `conv-proc-expand` | v5 | 2026-04-05 | Pattern detection threshold 3+, auto skill/n8n stub generation |
