# HANDOVER: Router Agent — Build Step 4 of 8

**Document ID:** AGEN-HNDV-router-v2  
**Date:** 2026-02-22  
**Status:** Ready to Build  
**Depends on:** Memory Agent (Step 1), Project Manager (Step 2), Specification Agent (Step 3)

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|--------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/04_ROUTER_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/04_ROUTER_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec0311481b9975ecc1e04a85c8e | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Supabase SQL | Run directly on Supabase project `ylcepmvbjjnwmzvevxid` |
| n8n workflow JSON | Import into n8n `http://localhost:5678` |
| System prompt | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Code artifacts | GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## WHAT THIS AGENT DOES

FIRST point of contact for ALL requests. Classifies user intent, enforces phase requirements (can't build without a spec), routes to the correct specialist agent, logs all routing decisions.

## PIPELINE POSITION

**USER → ROUTER AGENT →** [Specification | Architecture | Builder | Verification | PM | Memory]

This is the **MAIN ENTRY POINT** for the entire system.

## SYSTEM PROMPT (For Claude API call)

```
You are the Router Agent. You classify user intent and route to the correct specialist agent.

ROUTING RULES:

1. New project / vague idea / requirements gathering → SPECIFICATION AGENT
2. "What's the status of..." / project queries → PROJECT MANAGER
3. "Remember..." / "What did we decide about..." → MEMORY AGENT
4. Spec exists, needs task decomposition → ARCHITECTURE AGENT
5. Architecture exists, needs code → BUILDER AGENT
6. Code exists, needs testing/validation → VERIFICATION AGENT

PHASE ENFORCEMENT (CRITICAL):
- Cannot route to Architecture without a completed spec
- Cannot route to Builder without completed architecture
- Cannot route to Verification without completed build
- If user tries to skip phases → explain why and route to correct phase

CLASSIFICATION OUTPUT:
{
  "intent": "new_project|status_query|memory_operation|architecture_request|build_request|verification_request",
  "confidence": 0.0-1.0,
  "routed_to": "agent_name",
  "reason": "why this routing decision",
  "phase_check": "passed|blocked",
  "phase_blocker": "what's missing if blocked"
}
```

## AGENT ENDPOINTS

| Agent | Endpoint |
|-------|----------|
| Specification | POST /webhook/specification-agent |
| Architecture | POST /webhook/architecture-agent |
| Builder | POST /webhook/builder-agent |
| Verification | POST /webhook/verification-agent |
| Project Manager | POST /webhook/project-manager |
| Memory | POST /webhook/memory-agent |

## INTEGRATION CONTRACT

**Webhook:** POST /webhook/agent (main entry point)

**Input:**
```json
{
  "request": "user message in natural language",
  "project_id": "optional - existing project uuid"
}
```

**Output:**
```json
{
  "routed_to": "agent_name",
  "routing_reason": "why",
  "phase_check": "passed|blocked",
  "agent_response": { "...response from downstream agent..." }
}
```

## SUPABASE TABLES NEEDED

1. **routing_logs** — every routing decision with timestamp, intent, confidence, destination

## DELIVERABLES

- [ ] Supabase table creation SQL (ready to run)
- [ ] n8n workflow JSON (ready to import — MAIN ENTRY POINT)
- [ ] System prompt for Claude API intent classification
- [ ] Phase enforcement logic
- [ ] Test cases for ALL routing paths
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**
