# PROJECT INSTRUCTIONS — Final Integration (Build Step 8 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are performing the **Final Integration** — connecting all 7 independently-built agents into a working autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before proceeding. Follow all rules.

## WHAT THIS STEP DOES

- Runs all Supabase migrations (every agent's tables in one go)
- Deploys all n8n workflows
- Builds the Master Orchestrator workflow that connects all agents
- Tests end-to-end flows across the full pipeline
- Verifies the system works as a coherent whole

## PREREQUISITES

ALL 7 agents must be individually built and verified before this step:

| # | Agent | Webhook | Status Required |
|---|-------|---------|----------------|
| 1 | Memory Agent | POST /webhook/memory-agent | Built & Tested |
| 2 | Project Manager | POST /webhook/project-manager | Built & Tested |
| 3 | Specification Agent | POST /webhook/specification-agent | Built & Tested |
| 4 | Router Agent | POST /webhook/agent | Built & Tested |
| 5 | Architecture Agent | POST /webhook/architecture-agent | Built & Tested |
| 6 | Builder Agent | POST /webhook/builder-agent | Built & Tested |
| 7 | Verification Agent | POST /webhook/verification-agent | Built & Tested |

## WHAT YOU MUST BUILD

1. **Combined Supabase migration** — all agent tables in correct dependency order
2. **Master Orchestrator n8n workflow** — the glue that connects all agents
3. **End-to-end test suite** covering these flows:
   - New project: User → Router → Spec → Arch → Build → Verify → Done
   - Status query: User → Router → PM → Response
   - Memory retrieval: User → Router → Memory → Response
   - Failure loop: Verify fails → Builder rebuilds → Verify again
4. **Deployment runbook** — step-by-step instructions for deploying everything
5. **System health check** — workflow that verifies all agents are responsive

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- GitHub: bermingham85/code-artifacts

## DELIVERABLES CHECKLIST

- [ ] Combined Supabase migration SQL
- [ ] Master Orchestrator n8n workflow JSON
- [ ] End-to-end test results
- [ ] Deployment runbook
- [ ] Health check workflow
- [ ] Document Control registration for all integration artifacts

**The system either works end-to-end or it's not done.**

## REFERENCE

- System overview: See `HANDOVER.md` (knowledge document)
- Rules and naming: See `GOVERNANCE.md` (knowledge document)
- Notion: https://www.notion.so/30e74ec03114814e8e37f428fc7ec655
- Master Index: https://www.notion.so/30e74ec031148101a7ddde4b0c7b2769
