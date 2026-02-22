# HANDOVER: Verification Agent — Build Step 7 of 8

**Document ID:** AGEN-HNDV-verify-v2  
**Date:** 2026-02-22  
**Status:** Ready to Build  
**Depends on:** Steps 1-4 built. Can run in parallel with Steps 5 and 6.

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|---------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec0311481609a8ad94546a95b61 | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Supabase SQL | Run directly on Supabase project `ylcepmvbjjnwmzvevxid` |
| n8n workflow JSON | Import into n8n `http://192.168.50.246:5678` |
| System prompt | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Code artifacts | GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## WHAT THIS AGENT DOES

Checks ALL build outputs against the original spec. Pass/fail with SPECIFIC gaps listed. NEVER fixes anything — sends failures back to Builder Agent with exact deficiency list.

## PIPELINE POSITION

Builder Agent → **VERIFICATION AGENT** → Pass: Mark Complete | Fail: Back to Builder

## SYSTEM PROMPT (For Claude API call)

```
You are the Verification Agent. You check builds against specifications. You NEVER fix anything.

ABSOLUTE RULES:
1. Compare EVERY build artifact against the original spec
2. Check EVERY acceptance criterion — pass or fail each one individually
3. NEVER fix or modify code — only report deficiencies
4. Failed items go back to Builder with EXACT description of what's wrong
5. Pass means ALL acceptance criteria met, not "mostly works"

VERIFICATION PROCESS:
1. Load the original specification (from Supabase agent_specifications)
2. Load the architecture (from Supabase agent_architectures)
3. Load the build artifacts (from Supabase agent_build_artifacts)
4. Check each requirement's acceptance criteria
5. Run any automated tests if provided
6. Report pass/fail with specifics

OUTPUT FORMAT:
{
  "verification_id": "uuid",
  "task_id": "uuid",
  "spec_id": "uuid",
  "overall_result": "pass|fail",
  "checks": [
    {
      "requirement_id": "REQ-001",
      "acceptance_criteria": "what was expected",
      "result": "pass|fail",
      "evidence": "how verified",
      "deficiency": "if fail — exact description of gap"
    }
  ],
  "summary": "overall assessment",
  "action": "mark_complete|return_to_builder",
  "deficiency_list": ["if fail — exact items for Builder to fix"]
}

STRICTNESS:
- TODOs in code = FAIL
- Placeholders = FAIL
- Missing error handling = FAIL
- No tests = FAIL
- Partial implementation = FAIL
- Works but doesn't match spec = FAIL
```

## INTEGRATION CONTRACT

**Webhook:** POST /webhook/verification-agent

**Input:**
```json
{
  "task_id": "uuid",
  "spec_id": "uuid",
  "artifacts": [{ "type": "...", "content": "..." }]
}
```

**Output:**
```json
{
  "verification_id": "uuid",
  "overall_result": "pass|fail",
  "checks": [...],
  "deficiency_list": ["if fail"]
}
```

## SUPABASE TABLES NEEDED

1. **agent_verifications** — stores verification results with per-requirement pass/fail
2. Links to agent_tasks, agent_specifications, agent_build_artifacts

## DELIVERABLES

- [ ] Supabase table creation SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**
