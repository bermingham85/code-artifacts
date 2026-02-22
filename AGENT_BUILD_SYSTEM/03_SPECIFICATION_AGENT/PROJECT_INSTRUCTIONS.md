# PROJECT INSTRUCTIONS — Specification Agent (Build Step 3 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Specification Agent** — the requirements clarity enforcer for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow **RULE 0 (Audit Before Build)** and the 5-phase sequence: Audit → Gap Analysis → Build Gaps → Test → Document.

## START WITH AUDIT (RULE 0)

**Before writing ANY code, SQL, or workflow:**

1. Check Supabase for existing table `agent_specifications`
2. Check n8n for existing "Specification Agent" workflow
3. Report findings to the user
4. **WAIT for confirmation before building anything**

## WHAT THIS AGENT DOES

- Forces clarity before anything gets built
- Captures complete requirements with acceptance criteria
- Prevents vague specs from entering the pipeline
- Asks clarifying questions until requirements are unambiguous
- Produces structured spec documents

## WHERE IT SITS IN THE SYSTEM

User Request → Router → **SPECIFICATION AGENT** → Architecture Agent

## WHAT YOU MUST DELIVER

1. Supabase table `agent_specifications` (verify or create)
2. Complete n8n workflow JSON (importable)
3. System prompt for requirements extraction and clarification
4. Spec template with required fields
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- **Already built:** Memory Agent, Project Manager

### n8n Credentials (use EXACTLY these)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/specification-agent
- **Input:** `{ "request": "user message", "project_id": "optional" }`
- **Output:** `{ "spec_id": "uuid", "status": "complete|needs_clarification", "questions": [...] }`

## DELIVERABLES CHECKLIST

- [ ] Infrastructure audit documented
- [ ] Gap analysis completed
- [ ] Supabase table SQL (if needed)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build ONLY what's missing. Preserve everything that works. No partial solutions. No TODOs.**

## REFERENCE

- Agent-specific details: See `HANDOVER.md` (knowledge document)
- Rules and naming: See `GOVERNANCE.md` (knowledge document)
- Notion: https://www.notion.so/30e74ec0311481c0819edeb401857998
