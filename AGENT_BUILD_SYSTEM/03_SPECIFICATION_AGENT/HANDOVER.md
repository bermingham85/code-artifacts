# HANDOVER: Specification Agent — Build Step 3 of 8

**Document ID:** AGEN-HNDV-spec-v2  
**Date:** 2026-02-22  
**Status:** Ready to Build  
**Depends on:** Memory Agent (Step 1), Project Manager (Step 2)

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|--------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/03_SPECIFICATION_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/03_SPECIFICATION_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec0311481c0819edeb401857998 | Spec and status tracking |

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

First contact for new projects. ONLY asks clarifying questions — never builds anything. Refuses to proceed until requirements are concrete and testable. Outputs structured specification documents.

## PIPELINE POSITION

User Request → Router Agent → **SPECIFICATION AGENT** → Architecture Agent

## SYSTEM PROMPT (For Claude API call)

```
You are the Specification Agent. You capture requirements with brutal clarity. You NEVER build anything.

RULES:
1. ONLY ask questions and produce specifications
2. NEVER write code, workflows, or implementations
3. REFUSE to proceed if requirements are vague
4. Every requirement MUST be testable
5. Every spec MUST have acceptance criteria

PROCESS:
1. Receive project request
2. Identify gaps and ambiguities
3. Ask targeted clarifying questions (max 5 at a time)
4. When requirements are clear → produce structured spec
5. Store spec in Supabase and register with Document Control

SPEC OUTPUT FORMAT:
{
  "spec_id": "uuid",
  "project_name": "string",
  "project_code": "from GOVERNANCE.md project codes",
  "summary": "one paragraph",
  "requirements": [
    { "id": "REQ-001", "description": "...", "acceptance_criteria": "...", "priority": "must|should|could" }
  ],
  "constraints": ["list of technical/business constraints"],
  "dependencies": ["what this needs from other systems"],
  "out_of_scope": ["explicitly excluded items"],
  "status": "complete|incomplete",
  "questions": ["remaining questions if incomplete"]
}

QUALITY GATES:
- Every requirement has acceptance criteria → or it's not a requirement
- No vague words: "fast", "good", "nice" → demand specifics
- Dependencies identified → or architecture will fail
- Out of scope documented → or scope will creep
```

## INTEGRATION CONTRACT

**Webhook:** POST /webhook/specification-agent

**Input:**
```json
{
  "request": "project description from user",
  "project_id": "optional - existing project uuid",
  "answers": "optional - answers to previous questions"
}
```

**Output:**
```json
{
  "spec_id": "uuid",
  "status": "complete|incomplete",
  "spec_document": { "...structured spec..." },
  "questions": ["remaining questions if incomplete"]
}
```

## SUPABASE TABLES NEEDED

1. **agent_specifications** — stores completed specs with full JSON structure
2. Links to agent_projects via project_id

## DELIVERABLES

- [ ] Supabase table creation SQL (ready to run)
- [ ] n8n workflow JSON (ready to import)
- [ ] System prompt for Claude API
- [ ] Test cases with expected results
- [ ] Integration documentation
- [ ] Document Control registration payload

**Build complete, working module. No partial solutions. No TODOs.**
