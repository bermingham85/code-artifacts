# PROJECT INSTRUCTIONS — Architecture Agent (Build Step 5 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Architecture Agent** — the task decomposition engine for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow all rules, especially Research First (Rule 1) and Document Control (Rule 3).

## WHAT THIS AGENT DOES

- Receives COMPLETED specifications from the Specification Agent
- Decomposes specs into discrete, sequenced tasks (1-2 hours max each)
- Knows the tech stack and makes technology decisions
- Creates dependency maps between tasks
- NEVER accepts vague specs — rejects back to Specification Agent
- NEVER builds anything — only designs task plans

## WHERE IT SITS IN THE SYSTEM

Specification Agent → **ARCHITECTURE AGENT** → Builder Agent (for each task)

## WHAT YOU MUST BUILD

1. Supabase tables: `architectures`, `architecture_tasks`, `task_dependencies`
2. Complete n8n workflow JSON (importable)
3. System prompt for task decomposition and tech stack decisions
4. Structured output format for architecture documents
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- **Already built:** Memory Agent, Project Manager, Specification Agent, Router Agent

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/architecture-agent
- **Input:** `{ "spec_id": "uuid" }` or `{ "spec_document": {...} }`
- **Output:** `{ "architecture_id": "uuid", "tasks": [...], "dependencies": {...} }`
- Triggered by Specification Agent (when spec is approved)
- Feeds tasks to Builder Agent one at a time

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
- Notion: https://www.notion.so/30e74ec0311481089700e059eeba7b09
