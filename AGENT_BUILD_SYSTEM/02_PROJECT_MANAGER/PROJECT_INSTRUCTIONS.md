# PROJECT INSTRUCTIONS — Project Manager Agent (Build Step 2 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Project Manager Agent** — the state tracking authority for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow all rules, especially Research First (Rule 1) and Document Control (Rule 3).

## WHAT THIS AGENT DOES

- Tracks state across ALL projects and sessions
- Knows what's done, blocked, and next for every project
- Loads context at session start so work continues without re-explanation
- Updates state after any work completes
- Provides status summaries on demand

## WHERE IT SITS IN THE SYSTEM

- Called at START of every session to load context
- Called by ALL other agents to update status
- Called by user for status queries
- Central state authority for the entire system

## WHAT YOU MUST BUILD

1. Supabase tables: agent_projects, agent_tasks, agent_task_dependencies, agent_sessions
2. Complete n8n workflow JSON (importable)
3. Multiple actions: get_status, start_session, end_session, update_task
4. System prompt for status summarization
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- **Memory Agent already built** — can call POST /webhook/memory-agent

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/project-manager
- **Input:** `{ "action": "get_status|start_session|end_session|update_task", ... }`
- **Output:** `{ "status": {...}, "next_actions": [...], "blockers": [...] }`

## DELIVERABLES CHECKLIST

- [ ] Supabase table SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**

## REFERENCE

- Agent-specific details: See `HANDOVER.md` (knowledge document)
- Rules and naming: See `GOVERNANCE.md` (knowledge document)
- Notion: https://www.notion.so/30e74ec03114812491b3cadce807f5f3
