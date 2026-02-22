# HANDOVER: Project Manager Agent — Build Step 2 of 8

**Document ID:** AGEN-HNDV-pm-v2  
**Date:** 2026-02-22  
**Status:** Ready to Build  
**Depends on:** Memory Agent (Step 1) must be built first

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|---------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/02_PROJECT_MANAGER/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/02_PROJECT_MANAGER/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec03114812491b3cadce807f5f3 | Spec and status tracking |

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

Tracks state across ALL projects and sessions. Central state authority for the entire system.

- Knows what's done, blocked, and next for every project
- Loads context at session start so work continues without re-explanation
- Updates state after any work completes
- Provides status summaries on demand

## PIPELINE POSITION

- Called at **START of every session** to load context
- Called by **ALL other agents** to update status
- Called by **user** for status queries ("what's the state of project X?")
- Can call **Memory Agent** to store/retrieve historical context

## SYSTEM PROMPT (For Claude API call)

```
You are the Project Manager Agent. You track the state of every project and task across all sessions.

RULES:
1. ALWAYS know current state of every active project
2. ALWAYS provide clear next actions when asked for status
3. ALWAYS identify blockers proactively
4. NEVER lose track of incomplete work
5. ALWAYS maintain task dependencies

PROJECT STATES: planning, specifying, architecting, building, verifying, complete, blocked, paused

TASK STATES: pending, in_progress, complete, blocked, failed

When asked for status, respond with:
1. Current state of the project
2. What was last completed
3. What's next (with specific task IDs)
4. Any blockers or dependencies
5. Estimated completion if possible

When updating state:
1. Validate the state transition is legal
2. Update the task record
3. Check if parent project state should change
4. Store a memory via Memory Agent for significant events
```

## INTEGRATION CONTRACT

**Webhook:** POST /webhook/project-manager

### Actions:

**get_status**
```json
{
  "action": "get_status",
  "project_id": "optional-uuid",
  "include_tasks": true
}
```
Returns: `{ "projects": [...], "active_tasks": [...], "blockers": [...], "next_actions": [...] }`

**start_session**
```json
{
  "action": "start_session",
  "project_id": "optional-uuid",
  "agent_name": "which agent is starting"
}
```
Returns: `{ "session_id": "uuid", "context": {...}, "pending_tasks": [...] }`

**end_session**
```json
{
  "action": "end_session",
  "session_id": "uuid",
  "summary": "what was accomplished",
  "next_steps": ["list of what's next"]
}
```

**update_task**
```json
{
  "action": "update_task",
  "task_id": "uuid",
  "status": "complete|in_progress|blocked|failed",
  "notes": "what happened"
}
```

## SUPABASE TABLES NEEDED

1. **agent_projects** — project registry with state tracking
2. **agent_tasks** — individual tasks with status, assignment, dependencies
3. **agent_task_dependencies** — which tasks block which
4. **agent_sessions** — session log for continuity

## EXISTING DATA TO INTEGRATE

- `contexts` table (33 existing rows in Supabase)
- `planning_conversations` table
- PROJECT_MEMORY_BANK.json (in code-artifacts repo)
- Memory Agent (already built) — call POST /webhook/memory-agent

## DELIVERABLES

- [ ] Supabase table creation SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**
