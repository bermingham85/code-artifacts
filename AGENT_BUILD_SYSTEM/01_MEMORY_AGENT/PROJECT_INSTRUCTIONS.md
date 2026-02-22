# PROJECT INSTRUCTIONS — Memory Agent (Build Step 1 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Memory Agent** — the foundational context storage layer for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. It contains the non-negotiable rules for this build. Before writing any code:

1. Read GOVERNANCE.md completely — especially **RULE 0 (Audit Before Build)**
2. Follow the 5-phase sequence: Audit → Gap Analysis → Build Gaps → Test → Document
3. Follow RULE 3 (Document Control) — register all artifacts
4. Follow RULE 9 — use exact table names and credential references

## START WITH AUDIT (RULE 0)

**Before writing ANY code, SQL, or workflow:**

1. Check Supabase for existing tables (`agent_memories`, `agent_projects`)
2. Check n8n for existing "Memory Agent" workflow
3. Check if search functions exist (`search_memories`, `search_memories_by_tags`, `touch_memory`)
4. Report findings to the user
5. **WAIT for confirmation before building anything**

The HANDOVER.md file documents what already exists. Verify it, don't assume it.

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

## WHAT YOU MUST DELIVER

1. Supabase table `agent_memories` (verify existing or create)
2. Search function SQL (verify existing or create)
3. Complete n8n workflow JSON (verify existing or fix/replace)
4. System prompt for Claude API call (categorization)
5. Memory schema and tagging system
6. Test cases that prove it works
7. Integration spec for other agents to call it

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- GitHub: bermingham85/code-artifacts

### n8n Credentials (use EXACTLY these)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/memory-agent
- **Input:** `{ "action": "store|retrieve|search|list", ... }`
- **Output:** `{ "memories": [...], "relevance": [...] }`
- Must support full-text search
- Must link to projects and agents

## DELIVERABLES CHECKLIST

Before this conversation ends, you must produce:
- [ ] Infrastructure audit documented
- [ ] Gap analysis completed
- [ ] Supabase table SQL (if needed — may already exist)
- [ ] Search function SQL (if needed — may already exist)
- [ ] n8n workflow JSON (verified working or fixed)
- [ ] System prompt for Claude API categorization
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build ONLY what's missing. Preserve everything that works. No partial solutions. No TODOs.**

## REFERENCE

- Agent-specific details: See `HANDOVER.md` (uploaded as knowledge document)
- Rules and naming: See `GOVERNANCE.md` (uploaded as knowledge document)
- Notion page: https://www.notion.so/30e74ec031148197be2cf0885b30326b
