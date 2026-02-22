# PROJECT INSTRUCTIONS — Memory Agent (Build Step 1 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are completing the **Memory Agent** — the foundational context storage layer for a 7-agent autonomous system. Infrastructure already partially exists. Your job is to AUDIT what's there, identify gaps, and complete the build.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. It contains the non-negotiable rules for this build. Before writing any code:

1. Read GOVERNANCE.md completely — especially **Rule 0 (Audit First)** and **Rule 1 (Research First)**
2. **DO NOT execute any CREATE TABLE or CREATE FUNCTION SQL** until you have audited what already exists
3. **DO NOT delete or overwrite any existing data** — it represents weeks of work

## STEP 1: AUDIT EXISTING INFRASTRUCTURE (DO THIS FIRST)

Before building anything, audit what already exists using MCP tools:

### Supabase Audit
Use the Supabase MCP to run these READ-ONLY queries:
```sql
-- Check existing tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'agent_%';

-- Check agent_memories structure and data
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'agent_memories';
SELECT COUNT(*), type, category FROM agent_memories GROUP BY type, category;

-- Check existing functions
SELECT routine_name FROM information_schema.routines WHERE routine_schema = 'public' AND routine_name LIKE '%memor%' OR routine_name LIKE '%search%';

-- Check existing indexes
SELECT indexname FROM pg_indexes WHERE tablename = 'agent_memories';
```

### n8n Audit
Check for existing Memory Agent workflow at http://localhost:5678

### Report findings before proceeding
Tell me what exists, what's missing, and what needs fixing. Do NOT create anything yet.

## STEP 2: GAP ANALYSIS

Compare what exists against the spec in HANDOVER.md. Identify:
- What's already built and working
- What's built but needs fixing
- What's missing entirely
- What data exists that must be preserved

Present the gap analysis and wait for approval before proceeding.

## STEP 3: BUILD ONLY WHAT'S MISSING

After audit and approval:
- Add missing columns/indexes (ALTER TABLE, not CREATE TABLE)
- Add missing functions (CREATE OR REPLACE, not DROP + CREATE)
- Complete n8n workflow if incomplete
- Write tests against existing infrastructure

## WHAT THIS AGENT DOES

- Stores and retrieves context across conversations
- Persists decisions, preferences, patterns
- Enables ANY agent to access historical context
- Full-text search across all stored memories
- Links memories to projects and agents

## WHERE IT SITS IN THE SYSTEM

- Called by ALL other agents to store/retrieve context
- Called at session start to load relevant memories
- Central knowledge authority for the entire system
- **This is built FIRST because all other agents depend on it**

## INFRASTRUCTURE

- n8n: http://localhost:5678 (Docker Desktop) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- GitHub: bermingham85/code-artifacts

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/memory-agent
- **Input:** `{ "action": "store|retrieve|search|list", ... }`
- **Output:** `{ "memories": [...], "relevance": [...] }`
- Must support full-text search
- Must link to projects and agents

## DELIVERABLES CHECKLIST

- [ ] Infrastructure audit complete (Step 1)
- [ ] Gap analysis presented and approved (Step 2)
- [ ] Any missing Supabase schema added (not recreated)
- [ ] n8n workflow complete and tested
- [ ] System prompt for Claude API categorization
- [ ] Test cases run against existing infrastructure
- [ ] Integration documentation
- [ ] Document Control registration payload

**Complete this as a working module. Preserve all existing data. No partial solutions. No TODOs.**

## REFERENCE

- Agent-specific details: See `HANDOVER.md` (uploaded as knowledge document)
- Rules and naming: See `GOVERNANCE.md` (uploaded as knowledge document)
- Notion page: https://www.notion.so/30e74ec031148197be2cf0885b30326b
