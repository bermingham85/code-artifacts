# PROJECT INSTRUCTIONS — Builder Agent (Build Step 6 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Builder Agent** — the code production engine for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow **RULE 0 (Audit Before Build)** and the 5-phase sequence: Audit → Gap Analysis → Build Gaps → Test → Document.

## START WITH AUDIT (RULE 0)

**Before writing ANY code, SQL, or workflow:**

1. Check Supabase for existing table `agent_build_artifacts`
2. Check n8n for existing "Builder Agent" workflow
3. Report findings to the user
4. **WAIT for confirmation before building anything**

## WHAT THIS AGENT DOES

- Receives ONE task at a time from the Architecture Agent
- Produces COMPLETE, RUNNABLE code — no TODOs, no placeholders, no stubs
- Has zero discretion — builds exactly what the task specifies
- Registers all artifacts with Document Control
- Hands completed code to Verification Agent

## WHERE IT SITS IN THE SYSTEM

Architecture Agent → **BUILDER AGENT** → Verification Agent

## WHAT YOU MUST DELIVER

1. Supabase table `agent_build_artifacts` (verify or create)
2. Complete n8n workflow JSON (importable)
3. System prompt that enforces complete code production (no shortcuts)
4. Code generation pipeline with quality gates
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- **Already built:** Memory, PM, Spec, Router, Architecture Agents

### n8n Credentials (use EXACTLY these)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/builder-agent
- **Input:** `{ "task_id": "uuid", "task": {...} }`
- **Output:** `{ "build_id": "uuid", "artifacts": [...], "status": "complete|failed" }`
- Receives tasks from Architecture Agent
- Sends completed builds to Verification Agent

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
- Notion: https://www.notion.so/30e74ec03114810c83e5f2f60821e339
