# HANDOVER: Final Integration — Build Step 8 of 8

**Document ID:** AGEN-HNDV-integration-v2  
**Date:** 2026-02-22  
**Status:** Pending (awaiting all 7 agent builds)  
**Depends on:** ALL previous steps (1-7) must be complete

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|--------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/08_FINAL_INTEGRATION/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/08_FINAL_INTEGRATION/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec03114814e8e37f428fc7ec655 | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Combined Supabase migration | Run on Supabase project `ylcepmvbjjnwmzvevxid` |
| Master Orchestrator workflow | Import into n8n `http://localhost:5678` |
| Deployment runbook | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## Context

This is the final assembly step. All 7 agents have been built independently as n8n workflows with Supabase persistence. This step connects them into a single functioning system.

## Agent Registry

| Agent | Webhook Path | Supabase Tables | n8n Workflow |
|-------|-------------|-----------------|-------------|
| Memory | /webhook/memory-agent | agent_memories | TBD after build |
| Project Manager | /webhook/project-manager | agent_projects, agent_tasks, agent_task_dependencies, agent_sessions | TBD |
| Specification | /webhook/specification-agent | agent_specifications | TBD |
| Router | /webhook/agent | routing_logs | TBD |
| Architecture | /webhook/architecture-agent | agent_architectures | TBD |
| Builder | /webhook/builder-agent | agent_build_artifacts | TBD |
| Verification | /webhook/verification-agent | agent_verifications | TBD |

## Integration Flows

### Flow 1: New Project
```
User message
  → Router classifies intent as "new project"
  → Specification Agent captures requirements
  → (loop until spec is complete)
  → Architecture Agent decomposes into tasks
  → Builder Agent builds each task
  → Verification Agent checks each build
  → Project Manager updates status throughout
  → Memory Agent stores context at each step
```

### Flow 2: Status Query
```
User asks "what's the status of X?"
  → Router classifies as "status query"
  → Project Manager returns current state
  → Memory Agent provides additional context
```

### Flow 3: Verification Failure
```
Verification Agent finds gaps
  → Returns specific failures to Builder
  → Builder rebuilds against original spec + failure details
  → Verification re-checks
  → Loop until pass (max 3 attempts before escalation)
```

## Master Orchestrator Design

The Master Orchestrator is an n8n workflow that:
1. Receives the initial request at POST /webhook/agent (Router)
2. Router determines which agent handles it
3. Orchestrator makes HTTP requests to individual agent webhooks
4. Passes responses between agents as needed
5. Logs all interactions to Supabase

## Supabase Migration Order

Run tables in this order (respecting foreign key dependencies):
1. agent_memories (Memory Agent — no dependencies)
2. agent_projects (PM — no dependencies)
3. agent_sessions (PM — references agent_projects)
4. agent_tasks (PM — references agent_projects)
5. agent_task_dependencies (PM — references agent_tasks)
6. agent_specifications (Spec — references agent_projects)
7. routing_logs (Router — no dependencies)
8. agent_architectures (Arch — references agent_specifications)
9. agent_build_artifacts (Builder — references agent_tasks)
10. agent_verifications (Verify — references agent_build_artifacts, agent_specifications)

## Health Check Endpoints

After deployment, verify each agent responds:
```
POST /webhook/memory-agent        → { "action": "search", "query": "test" }
POST /webhook/project-manager     → { "action": "get_status" }
POST /webhook/specification-agent → { "request": "ping" }
POST /webhook/agent               → { "request": "ping" }
POST /webhook/architecture-agent  → { "request": "ping" }
POST /webhook/builder-agent       → { "request": "ping" }
POST /webhook/verification-agent  → { "request": "ping" }
```

## Document Control

All integration artifacts registered at:
- Webhook: http://localhost:5678/webhook/log-entry
- Notion DB: https://www.notion.so/22674ec0311480a7b76cc22a158c1fd4

## Notion References

- Master Index: https://www.notion.so/30e74ec031148101a7ddde4b0c7b2769
- Integration Page: https://www.notion.so/30e74ec03114814e8e37f428fc7ec655

## DELIVERABLES

- [ ] Combined Supabase migration SQL (all tables, correct order)
- [ ] Master Orchestrator n8n workflow JSON
- [ ] End-to-end test plan covering all 3 flows
- [ ] Deployment runbook (step-by-step)
- [ ] Health check script
- [ ] Document Control registration for all artifacts

**Build complete, working integration. No partial solutions. No TODOs.**
