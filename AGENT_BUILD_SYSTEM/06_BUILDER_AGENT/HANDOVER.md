# HANDOVER: Builder Agent — Build Step 6 of 8

**Document ID:** AGEN-HNDV-builder-v3  
**Date:** 2026-02-22  
**Status:** Ready to Build  
**Depends on:** Steps 1-4 built. Can run in parallel with Steps 5 and 7.

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|--------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec03114810c83e5f2f60821e339 | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Supabase SQL | Run directly on Supabase project `ylcepmvbjjnwmzvevxid` |
| n8n workflow JSON | Import into n8n `http://192.168.50.246:5678` |
| System prompt | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## n8n CREDENTIALS (use EXACTLY these in workflow JSON)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

---

## AUDIT CHECKLIST (Phase 1 — do this FIRST)

| Check | SQL / Action | Expected |
|-------|-------------|----------|
| Table exists? | `SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename='agent_build_artifacts';` | May not exist yet |
| n8n workflow? | Search n8n for "Builder" workflow | May not exist yet |
| Existing code? | Search GitHub bermingham85/code-artifacts | Check for prior build artifacts |

**This agent has no existing infrastructure. Everything needs to be built fresh.**

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

## SUPABASE TABLE: `agent_build_artifacts`

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | gen_random_uuid() |
| task_id | UUID FK | References agent_tasks(id) |
| project_id | UUID FK | References agent_projects(id) |
| type | TEXT | CHECK: supabase_sql, n8n_workflow, prompt, edge_function, script |
| name | TEXT NOT NULL | Following naming convention |
| content | TEXT NOT NULL | The actual artifact content |
| deploy_instructions | TEXT | Steps to deploy |
| status | TEXT | CHECK: draft, complete, verified, rejected |
| created_at | TIMESTAMPTZ | Default now() |
| updated_at | TIMESTAMPTZ | Default now() |

## TEST CASES

**Test 1: Accept valid task**
Input: `POST /webhook/builder-agent` with `{"task_id": "uuid", "task": {"name": "Create hello world", "description": "Create a simple n8n workflow", "inputs": [], "outputs": ["n8n_workflow"]}}`
Expected: Returns complete artifact with status "complete"

**Test 2: Reject unclear task**
Input: `{"task_id": "uuid", "task": {"name": "Fix stuff", "description": ""}}`
Expected: Returns status "rejected" with reason

**Test 3: Store artifact in Supabase**
After successful build, verify artifact appears in `agent_build_artifacts` table

## DELIVERABLES

- [ ] Infrastructure audit documented
- [ ] Supabase table SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**
