# AGENT SYSTEM — GOVERNANCE RULES
## Applies to EVERY subproject, EVERY session, EVERY artifact. No exceptions.

**Document ID:** AGEN-GOVN-001  
**Version:** 3.0  
**Date:** 2026-02-22  
**Status:** APPROVED  
**Owner:** Michael Bermingham

---

## HOW TO USE THIS DOCUMENT

This file is uploaded as a **knowledge document** into every Claude Project in this system.  
Every agent build session MUST obey these rules. If a rule conflicts with the agent-specific handover, this document wins.

---

## RULE 1: RESEARCH FIRST — NEVER BUILD FIRST

Before writing ANY code, workflow, or prompt:

1. Search for existing proven solutions (open source, n8n community, Supabase templates)
2. Search conversation history for prior work on this topic
3. Search Notion databases for existing specs, architectures, or completed components
4. Search GitHub repos (bermingham85) for existing code
5. Only after confirming nothing suitable exists → design
6. Only after design is approved → build

**If an existing solution covers 70%+ of the requirement, ADAPT it. Do NOT rebuild from scratch.**

**Before any build, complete this checklist:**
- [ ] Searched knowledge base / conversation history
- [ ] Searched GitHub bermingham85/code-artifacts
- [ ] Searched n8n community for similar workflows
- [ ] Documented what was found (even if nothing)
- [ ] Decision documented: build / adapt / reuse + rationale

---

## RULE 2: MODULAR, CONNECTED, DOCUMENTED

Every component MUST:
- Be modular — replaceable without breaking other parts
- Follow the connectivity pattern: n8n webhooks for orchestration, Supabase for persistence, Notion for documentation
- Have its spec registered in Document Control before build starts
- Have its completion registered in Document Control when done
- Include tests that prove it meets spec

---

## RULE 3: DOCUMENT CONTROL IS MANDATORY

**Every artifact** (prompt, script, workflow, config, handover, design doc) MUST be:

1. Registered with Document Control via webhook
2. Named using the naming convention below
3. Filed in the correct location
4. Searchable with metadata tags

**Webhook:** `http://192.168.50.246:5678/webhook/log-entry`  
**Notion DB:** `https://www.notion.so/22674ec0311480a7b76cc22a158c1fd4`

### Naming Convention

```
[PROJECT]-[TYPE]-[NAME]-v[VERSION].[EXT]
```

**Project Codes:**

| Code | Project |
|------|---------|
| BPIG | The Balding Pig |
| TALE | Taleweaver |
| FINX | Financial Automation |
| AGEN | Agent Build System |
| INFR | Infrastructure / MCP / DevOps |
| MILK | Milka Musical |
| JESS | Jesse Music / Novel Factory |
| BERM | Bermech Ltd / Airbnb |
| GOVN | Governance / Storage Consolidation |
| GNRL | General / Cross-project |

**Type Codes:**

| Code | Type |
|------|------|
| SPEC | Specification document |
| ARCH | Architecture document |
| WKFL | n8n workflow JSON |
| PRMPT | Prompt / system prompt |
| SCRPT | Script (code file) |
| CNFG | Configuration file |
| TEST | Test plan or results |
| HNDV | Handover document |
| RSRCH | Research findings |
| CMPL | Completion record |
| GOVN | Governance / rules |

### Filing Locations

| What | Primary | Backup |
|------|---------|--------|
| Specs & Architecture | Notion + GitHub | — |
| n8n workflows | n8n + GitHub export | — |
| Code files | GitHub bermingham85/code-artifacts | QNAP |
| Prompts | Notion + Claude Projects + GitHub | — |
| Configs | Local machine + GitHub | QNAP |
| Handovers | Notion + GitHub | Claude Project files |

---

## RULE 4: COMPLETION MUST BE RECORDED

**"Done" means ALL of the following:**

- [ ] Spec exists and was followed
- [ ] Code/workflow runs without errors
- [ ] Tests pass proving it meets spec
- [ ] Document Control entry updated to "Completed"
- [ ] Handover notes written for next session
- [ ] Component registered in the relevant registry

If ANY item is missing → it is NOT done.

---

## RULE 5: SESSION CONTINUITY — NO REPEAT RESEARCH

**At session start:**
- Load this governance doc + agent-specific handover
- Check Notion Document Control for latest state
- Check Supabase for existing data/tables
- Load prior research findings

**During session:**
- Log all decisions, research findings, and artifacts as you go
- Register artifacts with Document Control

**At session end:**
- Update handover with current state
- Register all artifacts
- Prepare next-session context

**Never re-research something already researched.** If you can't find prior research, flag the filing failure — don't redo the work.

---

## RULE 6: FOLLOW THE AGENT PIPELINE

```
Specification → Architecture → Build → Verify → Complete
```

1. **Specification Agent** forces clarity (no vague requirements)
2. **Architecture Agent** decomposes into tasks
3. **Builder Agent** writes code against spec
4. **Verification Agent** proves it works
5. **Project Manager** tracks state across sessions
6. **Router Agent** directs requests to the right specialist
7. **Memory Agent** persists context across conversations

Master Index: `https://www.notion.so/30e74ec031148101a7ddde4b0c7b2769`

---

## RULE 7: USER PREFERENCES (APPLY TO ALL BUILDS)

- **ADHD-friendly**: Step-by-step, no overwhelming info dumps
- **Complete solutions only** — never partial, never "here's a starting point"
- **One-button automation preferred** — minimize manual steps
- **n8n for orchestration** — not code-heavy Python servers
- **Supabase for database** — not raw Postgres, not SQLite
- **Desktop Commander for local file ops**
- **Email notifications only for failures** — don't spam for successes

---

## RULE 8: ANTI-PATTERNS (NEVER DO THESE)

| Don't | Do Instead |
|-------|------------|
| Build first, research later | Research first, always |
| Offer multiple options for the user to choose | Pick the best one and build it |
| Re-research previously completed work | Load from handover / Document Control |
| Skip document control registration | Register every artifact, every time |
| Say "done" without tests passing | Run tests, record results |
| Use superseded file versions | Always check for latest version |
| Create partial solutions | Complete solutions or nothing |
| Leave TODOs or placeholders in code | Fill everything in or flag as blocker |

---

## INFRASTRUCTURE REFERENCE

**Supabase:** Project `ylcepmvbjjnwmzvevxid` — `https://ylcepmvbjjnwmzvevxid.supabase.co`  
**n8n Local:** `http://192.168.50.246:5678`  
**n8n Cloud:** `https://bermech.app.n8n.cloud`  
**GitHub:** `bermingham85/code-artifacts`  
**APIs:** Anthropic (Claude), OpenAI, Gemini x4, Groq, Fal AI, Flux AI, ElevenLabs  
**MCP Servers:** Desktop Commander, Notion, Supabase, n8n, GitHub

---

## EXISTING CODE TO REUSE (RESEARCH THESE FIRST)

| Asset | Location | Reusable Pattern |
|-------|----------|------------------|
| orchestrator.py | bermingham85/code-artifacts | 4-agent pipeline, API client, logging |
| Agent-Agency MCP | agent-agency-mcp repo | 21 agents registered, monitoring tools |
| Novel Writer Validation | n8n workflow JSON | 3-stage validation gates |
| Document Control Agent | n8n local | Activity logger webhook |
| PROJECT_MEMORY_BANK.json | code-artifacts repo | Session state persistence |

---

## VERSION CONTROL FOR THIS DOCUMENT

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-02-21 | Initial rules |
| 2.0 | 2026-02-21 | Added research-first, document control |
| 3.0 | 2026-02-22 | Consolidated into single governance doc. Supersedes CORE_RULES v1, v2, v3 and SESSION_HANDOVER v2 rules sections. This is now the single source of truth. |

**This document supersedes:** `AGENT_SYSTEM_CORE_RULES.md`, `AGENT_SYSTEM_CORE_RULES_V2.md`, `AGENT_SYSTEM_CORE_RULES_V3.md`, and the rules sections of `SESSION_HANDOVER_2026-02-22_v2.md`.
