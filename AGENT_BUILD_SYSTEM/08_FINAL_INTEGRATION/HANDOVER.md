# HANDOVER: Final Integration — Build Step 8 of 8

**Document ID:** AGEN-HNDV-integration-v3  
**Date:** 2026-02-22  
**Status:** Pending (awaiting all 7 agent builds)  
**Depends on:** ALL previous steps (1-7) must be complete

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|--------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/08_FINAL_INTEGRATION/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/08_FINAL_INTEGRATION/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec03114814e8e37f428fc7ec655 | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Combined Supabase migration | Run on Supabase project `ylcepmvbjjnwmzvevxid` |
| Master Orchestrator workflow | Import into n8n `http://192.168.50.246:5678` |
| Deployment runbook | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## n8n CREDENTIALS (use EXACTLY these in workflow JSON)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

---

## AUDIT CHECKLIST (Phase 1 — do this FIRST)

| Check | Action | Expected |
|-------|--------|----------|
| All agent tables exist? | `SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'agent_%' ORDER BY tablename;` | 10 tables (see list below) |
| All n8n workflows active? | Search n8n for all agent workflows | 7 workflows, all active |
| All webhooks responding? | POST to each endpoint with test payload | 7 successful responses |

### Expected Supabase Tables

| Table | Owner Agent |
|-------|------------|
| `agent_memories` | Memory |
| `agent_projects` | Project Manager |
| `agent_tasks` | Project Manager |
| `agent_task_dependencies` | Project Manager |
| `agent_sessions` | Project Manager |
| `agent_specifications` | Specification |
| `agent_routing_logs` | Router |
| `agent_architectures` | Architecture |
| `agent_build_artifacts` | Builder |
| `agent_verifications` | Verification |

---

## Context

This is the final assembly step. All 7 agents have been built independently as n8n workflows with Supabase persistence. This step connects them into a single functioning system.

## Agent Registry

| Agent | Webhook Path | Supabase Tables |
|-------|-------------|-----------------|
| Memory | /webhook/memory-agent | agent_memories |
| Project Manager | /webhook/project-manager | agent_projects, agent_tasks, agent_task_dependencies, agent_sessions |
| Specification | /webhook/specification-agent | agent_specifications |
| Router | /webhook/agent | agent_routing_logs |
| Architecture | /webhook/architecture-agent | agent_architectures |
| Builder | /webhook/builder-agent | agent_build_artifacts |
| Verification | /webhook/verification-agent | agent_verifications |

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
1. `agent_memories` (Memory — no dependencies)
2. `agent_projects` (PM — no dependencies)
3. `agent_sessions` (PM — references agent_projects)
4. `agent_tasks` (PM — references agent_projects)
5. `agent_task_dependencies` (PM — references agent_tasks)
6. `agent_specifications` (Spec — references agent_projects)
7. `agent_routing_logs` (Router — no dependencies)
8. `agent_architectures` (Arch — references agent_specifications)
9. `agent_build_artifacts` (Builder — references agent_tasks)
10. `agent_verifications` (Verify — references agent_build_artifacts, agent_specifications)

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

## DELIVERABLES

- [ ] Infrastructure audit (all 7 agents verified)
- [ ] Gap analysis (what's missing)
- [ ] Master Orchestrator n8n workflow JSON
- [ ] Combined migration SQL (gaps only)
- [ ] End-to-end test results for all 3 flows
- [ ] Deployment runbook
- [ ] Health check script
- [ ] Document Control registration payload

**Build complete, working integration. No partial solutions. No TODOs.**
