# PROJECT INSTRUCTIONS — Verification Agent (Build Step 7 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Verification Agent** — the quality gate for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow **RULE 0 (Audit Before Build)** and the 5-phase sequence: Audit → Gap Analysis → Build Gaps → Test → Document.

## START WITH AUDIT (RULE 0)

**Before writing ANY code, SQL, or workflow:**

1. Check Supabase for existing table `agent_verifications`
2. Check n8n for existing "Verification Agent" workflow
3. Report findings to the user
4. **WAIT for confirmation before building anything**

## WHAT THIS AGENT DOES

- Checks ALL build outputs against the original specification
- Pass/fail with SPECIFIC gaps listed
- NEVER fixes anything — sends failures back to Builder Agent
- Ensures no TODOs, placeholders, or partial implementations pass
- Marks tasks as complete only when ALL acceptance criteria are met

## WHERE IT SITS IN THE SYSTEM

Builder Agent → **VERIFICATION AGENT** → Pass: Mark Complete | Fail: Back to Builder

## WHAT YOU MUST DELIVER

1. Supabase table `agent_verifications` (verify or create)
2. Complete n8n workflow JSON (importable)
3. System prompt for verification and deficiency reporting
4. Test cases that prove it works
5. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- **Already built:** Memory, PM, Spec, Router, Architecture, Builder Agents

### n8n Credentials (use EXACTLY these)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/verification-agent
- **Input:** `{ "task_id": "uuid", "spec_id": "uuid", "artifacts": [...] }`
- **Output:** `{ "verification_id": "uuid", "overall_result": "pass|fail", "checks": [...], "deficiency_list": [...] }`

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
- Notion: https://www.notion.so/30e74ec0311481609a8ad94546a95b61
