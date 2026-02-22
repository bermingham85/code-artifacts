# PROJECT INSTRUCTIONS — Memory Agent (Build Step 1 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Memory Agent** — the foundational context storage layer for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. It contains the non-negotiable rules for this build. Before writing any code:

1. Read GOVERNANCE.md completely
2. Follow RULE 1 (Research First) — search for existing memory/context solutions before building
3. Follow RULE 3 (Document Control) — register all artifacts
4. Follow RULE 4 (Completion) — nothing is "done" without tests passing

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

## WHAT YOU MUST BUILD

1. Supabase table creation SQL with full-text indexes
2. Search function SQL
3. Complete n8n workflow JSON (importable)
4. System prompt for Claude API call (categorization)
5. Memory schema and tagging system
6. Test cases that prove it works
7. Integration spec for other agents to call it

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- GitHub: bermingham85/code-artifacts

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/memory-agent
- **Input:** `{ "action": "store|retrieve|search|list", ... }`
- **Output:** `{ "memories": [...], "relevance": [...] }`
- Must support full-text search
- Must link to projects and agents

## EXISTING SOURCES TO INTEGRATE

- PROJECT_MEMORY_BANK.json (in code-artifacts repo)
- MASTER_PROMPT_LIBRARY.md (10 shortcuts)
- contexts table (33 existing rows in Supabase)
- planning_conversations table

## DELIVERABLES CHECKLIST

Before this conversation ends, you must produce:
- [ ] Supabase table SQL (ready to run)
- [ ] Search function SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API categorization
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build this as a complete, working module. No partial solutions. No TODOs.**

## REFERENCE

- Agent-specific details: See `HANDOVER.md` (uploaded as knowledge document)
- Rules and naming: See `GOVERNANCE.md` (uploaded as knowledge document)
- Notion page: https://www.notion.so/30e74ec031148197be2cf0885b30326b
