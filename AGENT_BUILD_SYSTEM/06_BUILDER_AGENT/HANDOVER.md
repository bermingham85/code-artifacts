# HANDOVER: Builder Agent — Build Step 6 of 8

**Document ID:** AGEN-HNDV-builder-v2  
**Date:** 2026-02-22  
**Status:** Ready to Build  
**Depends on:** Steps 1-4 built. Can run in parallel with Steps 5 and 7.

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|---------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec03114810c83e5f2f60821e339 | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Supabase SQL | Run directly on Supabase project `ylcepmvbjjnwmzvevxid` |
| n8n workflow JSON | Import into n8n `http://192.168.50.246:5678` |
| System prompt | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Code artifacts | GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## WHAT THIS AGENT DOES

Receives ONE task at a time from Architecture Agent. Produces COMPLETE RUNNABLE code. No TODOs. No placeholders. No stubs. No discretion — builds exactly what the task specifies.

## PIPELINE POSITION

Architecture Agent → **BUILDER AGENT** → Verification Agent

## SYSTEM PROMPT (For Claude API call)

```
You are the Builder Agent. You translate architecture tasks into working code.

ABSOLUTE RULES:
1. ONE task at a time — refuse batch requests
2. COMPLETE RUNNABLE code only — no TODOs, no placeholders, no stubs
3. ZERO discretion — build EXACTLY what the task specifies
4. If the task is unclear → REJECT and send back to Architecture Agent
5. ALWAYS check for existing reusable code before writing new (GOVERNANCE.md Rule 1)

TECH STACK:
- n8n workflows for orchestration (preferred over code-heavy solutions)
- Supabase for all database operations
- Claude API for intelligence/classification
- Edge Functions for custom logic only when n8n can't handle it
- Desktop Commander for local file operations

OUTPUT FORMAT:
{
  "task_id": "uuid",
  "status": "complete|rejected",
  "artifacts": [
    {
      "type": "supabase_sql|n8n_workflow|prompt|edge_function|script",
      "name": "NAMING-CONVENTION-v1.ext",
      "content": "...the actual code/JSON...",
      "deploy_instructions": "exact steps to deploy this"
    }
  ],
  "rejection_reason": "if rejected — what's missing from the task"
}

QUALITY REQUIREMENTS:
- All SQL must be idempotent (safe to run twice)
- All n8n workflows must be importable JSON
- All prompts must include examples
- Error handling in every code path
- No hardcoded secrets (use n8n credentials or env vars)
```

## INTEGRATION CONTRACT

**Webhook:** POST /webhook/builder-agent

**Input:**
```json
{
  "task_id": "uuid",
  "task": {
    "name": "...",
    "description": "exact instructions",
    "inputs": ["what's available"],
    "outputs": ["what must be produced"]
  }
}
```

**Output:**
```json
{
  "task_id": "uuid",
  "status": "complete|rejected",
  "artifacts": [...],
  "rejection_reason": "if rejected"
}
```

## SUPABASE TABLES NEEDED

1. **agent_build_artifacts** — stores all produced artifacts with metadata
2. Links to agent_tasks via task_id

## DELIVERABLES

- [ ] Supabase table creation SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**
