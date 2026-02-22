# PROJECT INSTRUCTIONS — Specification Agent (Build Step 3 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Specification Agent** — the requirements capture gate for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow all rules, especially Research First (Rule 1) and Document Control (Rule 3).

## WHAT THIS AGENT DOES

- First contact for new projects
- ONLY asks clarifying questions — never builds anything
- Refuses to proceed until requirements are concrete and testable
- Outputs structured specification documents
- Stores specifications in Supabase

## WHERE IT SITS IN THE SYSTEM

User Request → Router Agent → **SPECIFICATION AGENT** → Architecture Agent → Builder → Verification

## WHAT YOU MUST BUILD

1. Supabase `specifications` table SQL
2. Complete n8n workflow JSON (importable)
3. System prompt that enforces specification capture (never builds)
4. Structured output format for spec documents
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- **Memory Agent already built** — POST /webhook/memory-agent
- **Project Manager already built** — POST /webhook/project-manager

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/specification-agent
- **Input:** `{ "request": "user description", "project_id": "optional" }`
- **Output:** `{ "spec_id": "uuid", "status": "complete|incomplete", "spec_document": {...}, "questions": [...] }`
- Callable by Router Agent
- Triggers Architecture Agent when spec is complete

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
- Notion: https://www.notion.so/30e74ec0311481c0819edeb401857998
