# PROJECT INSTRUCTIONS — Router Agent (Build Step 4 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Router Agent** — the traffic director and entry point for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow **RULE 0 (Audit Before Build)** and the 5-phase sequence: Audit → Gap Analysis → Build Gaps → Test → Document.

## START WITH AUDIT (RULE 0)

**Before writing ANY code, SQL, or workflow:**

1. Check Supabase for existing table `agent_routing_logs`
2. Check n8n for existing "Router Agent" workflow
3. Report findings to the user
4. **WAIT for confirmation before building anything**

## WHAT THIS AGENT DOES

- FIRST point of contact for ALL requests
- Analyzes intent and routes to correct specialist agent
- Prevents wrong agent from handling wrong task
- Enforces phase requirements (can't build without spec)
- Logs all routing decisions

## WHERE IT SITS IN THE SYSTEM

**USER → ROUTER AGENT →** [Specification | Architecture | Builder | Verification | PM | Memory]

## WHAT YOU MUST DELIVER

1. Supabase `agent_routing_logs` table (verify or create)
2. Complete n8n workflow JSON as the MAIN ENTRY POINT
3. System prompt for intent classification
4. Phase enforcement logic
5. Test cases for all routing paths
6. Integration spec

## INFRASTRUCTURE

- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- **Already built:** Memory Agent, Project Manager, Specification Agent

### n8n Credentials (use EXACTLY these)

| What | Credential Name | Credential ID |
|------|----------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

## AGENT ENDPOINTS THIS ROUTER CONNECTS TO

| Agent | Endpoint |
|-------|----------|
| Specification | POST /webhook/specification-agent |
| Architecture | POST /webhook/architecture-agent |
| Builder | POST /webhook/builder-agent |
| Verification | POST /webhook/verification-agent |
| Project Manager | POST /webhook/project-manager |
| Memory | POST /webhook/memory-agent |

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/agent (main entry point)
- **Input:** `{ "request": "user message", "project_id": "optional" }`
- **Output:** `{ "routed_to": "agent_name", "agent_response": {...} }`

## DELIVERABLES CHECKLIST

- [ ] Infrastructure audit documented
- [ ] Gap analysis completed
- [ ] Supabase table SQL (if needed)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases for all routing paths
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build ONLY what's missing. Preserve everything that works. No partial solutions. No TODOs.**

## REFERENCE

- Agent-specific details: See `HANDOVER.md` (knowledge document)
- Rules and naming: See `GOVERNANCE.md` (knowledge document)
- Notion: https://www.notion.so/30e74ec0311481b9975ecc1e04a85c8e
