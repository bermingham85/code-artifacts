# PROJECT INSTRUCTIONS — Project Manager Agent (Build Step 2 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Project Manager Agent** — the state tracking authority for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow **RULE 0 (Audit Before Build)** and the 5-phase sequence: Audit → Gap Analysis → Build Gaps → Test → Document.

## START WITH AUDIT (RULE 0)

**Before writing ANY code, SQL, or workflow:**

1. Check Supabase for existing tables (`agent_projects`, `agent_tasks`, `agent_task_dependencies`, `agent_sessions`)
2. Check n8n for existing "Project Manager" workflow
3. Report findings to the user
4. **WAIT for confirmation before building anything**

The `agent_projects` table already has 10 rows. DO NOT DROP IT.

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

## WHAT YOU MUST DELIVER

1. Supabase tables: `agent_projects` (exists — verify), `agent_tasks`, `agent_task_dependencies`, `agent_sessions`
2. Complete n8n workflow JSON (importable)
3. Multiple actions: get_status, start_session, end_session, update_task
4. System prompt for status summarization
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- **Memory Agent already built** — can call POST /webhook/memory-agent

### n8n Credentials (use EXACTLY these)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/project-manager
- **Input:** `{ "action": "get_status|start_session|end_session|update_task", ... }`
- **Output:** `{ "status": {...}, "next_actions": [...], "blockers": [...] }`

## DELIVERABLES CHECKLIST

- [ ] Infrastructure audit documented
- [ ] Gap analysis completed
- [ ] Supabase table SQL (only for missing tables)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build ONLY what's missing. Preserve everything that works. No partial solutions. No TODOs.**

## REFERENCE

- Agent-specific details: See `HANDOVER.md` (knowledge document)
- Rules and naming: See `GOVERNANCE.md` (knowledge document)
- Notion: https://www.notion.so/30e74ec03114812491b3cadce807f5f3
