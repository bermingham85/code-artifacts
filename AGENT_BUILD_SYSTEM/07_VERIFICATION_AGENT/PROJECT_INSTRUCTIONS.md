# PROJECT INSTRUCTIONS — Verification Agent (Build Step 7 of 8)

## YOUR ROLE IN THIS CONVERSATION

You are building ONE agent: the **Verification Agent** — the quality gate for a 7-agent autonomous system.

## MANDATORY: READ GOVERNANCE.md FIRST

The file `GOVERNANCE.md` is uploaded as a knowledge document in this project. Read it completely before writing any code. Follow all rules, especially Research First (Rule 1) and Document Control (Rule 3).

## WHAT THIS AGENT DOES

- Checks ALL Builder outputs against the original specification
- Issues PASS or FAIL with SPECIFIC gap descriptions
- NEVER fixes anything — sends failures back to Builder with details
- Verifies Document Control registration is complete
- Confirms completion criteria from GOVERNANCE.md Rule 4

## WHERE IT SITS IN THE SYSTEM

Builder Agent → **VERIFICATION AGENT** → Pass: Mark Done | Fail: Return to Builder

## WHAT YOU MUST BUILD

1. Supabase tables: `verifications`, `verification_results`
2. Complete n8n workflow JSON (importable)
3. System prompt for spec-vs-build comparison (strict, never fixes)
4. Structured pass/fail output with gap detail
5. Test cases that prove it works
6. Integration spec

## INFRASTRUCTURE

- n8n: http://localhost:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available
- **Already built:** Memory, PM, Spec, Router, Architecture, Builder Agents

## INTEGRATION CONTRACT

- **Webhook:** POST /webhook/verification-agent
- **Input:** `{ "build_id": "uuid", "spec_id": "uuid", "artifacts": [...] }`
- **Output:** `{ "verification_id": "uuid", "result": "pass|fail", "gaps": [...], "details": {...} }`
- Receives builds from Builder Agent
- On PASS: updates Document Control, notifies PM
- On FAIL: returns to Builder with specific failure details

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
- Notion: https://www.notion.so/30e74ec0311481609a8ad94546a95b61
