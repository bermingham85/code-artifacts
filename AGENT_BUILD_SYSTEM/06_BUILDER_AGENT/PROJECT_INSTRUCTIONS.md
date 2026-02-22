# PROJECT INSTRUCTIONS — Builder Agent (Build Step 6 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Builder Agent** — the code production engine for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow all rules, especially Research First (Rule 1) and Document Control (Rule 3).

## WHAT THIS AGENT DOES

- Receives ONE task at a time from the Architecture Agent
- Produces COMPLETE, RUNNABLE code — no TODOs, no placeholders, no stubs
- Has zero discretion — builds exactly what the task specifies
- Registers all artifacts with Document Control
- Hands completed code to Verification Agent

## WHERE IT SITS IN THE SYSTEM

Architecture Agent → **BUILDER AGENT** → Verification Agent

## WHAT YOU MUST BUILD

1. Supabase tables: `build_artifacts`, `build_logs`
2. Complete n8n workflow JSON (importable)
3. System prompt that enforces complete code production (no shortcuts)
4. Code generation pipeline with quality gates
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- GitHub: bermingham85/code-artifacts
- **Already built:** Memory, PM, Spec, Router, Architecture Agents

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/builder-agent
- **Input:** `{ "task_id": "uuid", "task": {...} }`
- **Output:** `{ "build_id": "uuid", "artifacts": [...], "status": "complete|failed" }`
- Receives tasks from Architecture Agent
- Sends completed builds to Verification Agent

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
- Notion: https://www.notion.so/30e74ec03114810c83e5f2f60821e339
