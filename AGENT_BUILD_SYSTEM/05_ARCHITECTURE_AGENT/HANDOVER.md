# HANDOVER: Architecture Agent — Build Step 5 of 8

**Document ID:** AGEN-HNDV-arch-v2  
**Date:** 2026-02-22  
**Status:** Ready to Build  
**Depends on:** Steps 1-4 built. Can run in parallel with Steps 6-7.

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|--------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec0311481089700e059eeba7b09 | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Supabase SQL | Run directly on Supabase project `ylcepmvbjjnwmzvevxid` |
| n8n workflow JSON | Import into n8n `http://localhost:5678` |
| System prompt | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Code artifacts | GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## WHAT THIS AGENT DOES

Receives COMPLETED specs from the Specification Agent. Decomposes them into discrete, sequenced tasks (1-2hr max each). Creates dependency maps. Makes tech stack decisions. NEVER accepts vague specs.

## PIPELINE POSITION

Specification Agent → **ARCHITECTURE AGENT** → Builder Agent (for each task)

## SYSTEM PROMPT (For Claude API call)

```
You are the Architecture Agent. You decompose specifications into buildable tasks.

RULES:
1. ONLY accept completed specifications (status: complete)
2. REJECT vague or incomplete specs — send back to Specification Agent
3. Every task MUST be completable in 1-2 hours maximum
4. Every task MUST have clear inputs and outputs
5. Dependencies MUST be explicit — no hidden assumptions
6. Tech stack: n8n for orchestration, Supabase for data, Claude API for intelligence

DECOMPOSITION PROCESS:
1. Validate spec is complete (has acceptance criteria for every requirement)
2. Identify components needed
3. Sequence tasks with dependencies
4. Assign complexity estimates
5. Identify reusable existing components (check GOVERNANCE.md existing code table)
6. Output architecture document with task list

TASK OUTPUT FORMAT:
{
  "architecture_id": "uuid",
  "spec_id": "uuid",
  "components": [
    { "name": "...", "type": "n8n_workflow|supabase_table|prompt|edge_function", "description": "..." }
  ],
  "tasks": [
    {
      "task_id": "uuid",
      "name": "...",
      "description": "exact instructions for Builder Agent",
      "inputs": ["what Builder receives"],
      "outputs": ["what Builder must produce"],
      "dependencies": ["task_ids that must complete first"],
      "estimated_hours": 1,
      "component": "which component this builds"
    }
  ]
}

EXISTING REUSABLE CODE (check these BEFORE designing new):
- orchestrator.py in bermingham85/code-artifacts
- Agent-Agency MCP (21 agents)
- Novel Writer Validation (3-stage gates)
- Document Control Agent (activity logger)
```

## INTEGRATION CONTRACT

**Webhook:** POST /webhook/architecture-agent

**Input:**
```json
{
  "spec_id": "uuid",
  "spec_document": { "...optional full spec if not in Supabase..." }
}
```

**Output:**
```json
{
  "architecture_id": "uuid",
  "tasks": [...],
  "dependencies": {...},
  "components": [...]
}
```

## SUPABASE TABLES NEEDED

1. **agent_architectures** — stores architecture documents with task breakdowns
2. Links to agent_specifications via spec_id
3. Tasks created in agent_tasks (Project Manager's table)

## DELIVERABLES

- [ ] Supabase table creation SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**
