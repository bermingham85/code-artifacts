# PROJECT INSTRUCTIONS — Final Integration (Build Step 8 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are performing the **Final Integration** — connecting all 7 independently-built agents into a functioning system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow **RULE 0 (Audit Before Build)** and the 5-phase sequence: Audit → Gap Analysis → Build Gaps → Test → Document.

## START WITH AUDIT (RULE 0)

**Before writing ANY code, SQL, or workflow:**

1. Check Supabase — list ALL `agent_*` tables, verify they exist with data
2. Check n8n — list ALL agent workflows, verify they are active
3. Test each agent webhook endpoint individually
4. Report findings to the user
5. **WAIT for confirmation before building anything**

## WHAT THIS STEP DOES

- Connects all 7 agent workflows into a unified system
- Creates the Master Orchestrator n8n workflow
- Runs combined Supabase migration (filling any gaps)
- Tests all 3 end-to-end flows
- Produces deployment runbook

## WHAT YOU MUST DELIVER

1. Master Orchestrator n8n workflow (connects Router to all agents)
2. Combined Supabase migration SQL (only missing tables/columns)
3. End-to-end test plan covering all flows
4. Deployment runbook (step-by-step)
5. Health check script for all endpoints

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- **ALL 7 agents should already be built**

### n8n Credentials (use EXACTLY these)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

## END-TO-END FLOWS TO TEST

**Flow 1: New Project** — User → Router → Spec → Arch → Build → Verify
**Flow 2: Status Query** — User → Router → PM (+ Memory for context)
**Flow 3: Verification Failure** — Verify fails → Builder retries → Verify again (max 3 loops)

## DELIVERABLES CHECKLIST

- [ ] Infrastructure audit (all 7 agents verified)
- [ ] Gap analysis (what's missing from each agent)
- [ ] Master Orchestrator n8n workflow JSON
- [ ] Combined migration SQL (gaps only)
- [ ] End-to-end test results
- [ ] Deployment runbook
- [ ] Health check script
- [ ] Document Control registration payload

**Build ONLY what's missing. No partial solutions. No TODOs.**

## REFERENCE

- Integration details: See `HANDOVER.md` (knowledge document)
- Rules and naming: See `GOVERNANCE.md` (knowledge document)
- Notion: https://www.notion.so/30e74ec03114814e8e37f428fc7ec655
