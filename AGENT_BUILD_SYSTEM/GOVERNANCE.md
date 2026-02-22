# AGENT SYSTEM — GOVERNANCE RULES
## Applies to EVERY subproject, EVERY session, EVERY artifact. No exceptions.

**Document ID:** AGEN-GOVN-001  
**Version:** 4.0  
**Date:** 2026-02-22  
**Status:** APPROVED  
**Owner:** Michael Bermingham

---

## HOW TO USE THIS DOCUMENT

This file is uploaded as a **knowledge document** into every Claude Project in this system.  
Every agent build session MUST obey these rules. If a rule conflicts with the agent-specific handover, this document wins.

---

## RULE 0: AUDIT BEFORE YOU BUILD — MANDATORY GATE

**Before writing ANY code, SQL, or workflow, you MUST complete this audit and report findings to the user.**

### Step 1: Check Supabase
- List existing tables: `SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;`
- Check for the specific tables listed in your agent's HANDOVER.md
- If a table exists, count its rows — NEVER drop a table with data

### Step 2: Check n8n
- Search for existing workflows matching this agent's name
- If a workflow exists, inspect its structure before replacing it

### Step 3: Check GitHub
- Search bermingham85/code-artifacts for existing code for this agent

### Step 4: Report
- Tell the user what exists and what's missing
- **WAIT for confirmation before building anything**

### Step 5: Build ONLY the gaps
- If infrastructure exists and works → test it, don't rebuild it
- If infrastructure exists but is broken → fix it, don't recreate it
- If infrastructure doesn't exist → build it

**CRITICAL: If the handover says something exists, VERIFY it exists before building. If it does exist, DO NOT recreate it.**

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
| CREATE TABLE when the table already exists | Check first, ALTER TABLE if columns missing |
| DROP TABLE on a table with data | Never. Use migrations. |
| Offer multiple options for the user to choose | Pick the best one and build it |
| Re-research previously completed work | Load from handover / Document Control |
| Skip document control registration | Register every artifact, every time |
| Say "done" without tests passing | Run tests, record results |
| Use superseded file versions | Always check for latest version |
| Create partial solutions | Complete solutions or nothing |
| Leave TODOs or placeholders in code | Fill everything in or flag as blocker |
| Guess n8n credential names/IDs | Use exact values from RULE 9 below |
| Use different table names than specified | Use exact canonical names from RULE 9 |

---

## RULE 9: CANONICAL TABLE NAMES AND CREDENTIALS

### Supabase Table Names (use EXACTLY these)

| Table | Owner Agent | Purpose |
|-------|------------|---------|
| `agent_memories` | Memory Agent | Context storage across conversations |
| `agent_projects` | Project Manager | Project registry (10 rows exist) |
| `agent_tasks` | Project Manager | Task tracking per project |
| `agent_task_dependencies` | Project Manager | Task dependency graph |
| `agent_sessions` | Project Manager | Session continuity log |
| `agent_specifications` | Specification Agent | Requirement documents |
| `agent_routing_logs` | Router Agent | All routing decisions |
| `agent_architectures` | Architecture Agent | Task decomposition docs |
| `agent_build_artifacts` | Builder Agent | Produced code/artifacts |
| `agent_verifications` | Verification Agent | Pass/fail results per build |

**Use these exact names. Do not abbreviate, rename, or drop the `agent_` prefix.**

### n8n Credentials (use EXACTLY these in workflows)

| What | Credential Name in n8n | Credential ID |
|------|----------------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres (direct SQL) | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |
| Anthropic Claude API | `Anthropic account` | Check n8n credentials |

### n8n Base URL

- **Local:** `http://192.168.50.246:5678`
- **Cloud:** `https://bermech.app.n8n.cloud`
- **Webhook base:** `http://192.168.50.246:5678/webhook/`

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
| 3.0 | 2026-02-22 | Consolidated into single governance doc. Supersedes CORE_RULES v1-v3. |
| 4.0 | 2026-02-22 | **Post-mortem fix.** Added RULE 0 (mandatory audit gate before building). Added RULE 9 (canonical table names and n8n credential references). Expanded anti-patterns. Root cause: Memory Agent build ignored existing infrastructure because instructions said "build" not "audit then build." |

**This document supersedes:** `AGENT_SYSTEM_CORE_RULES.md`, `AGENT_SYSTEM_CORE_RULES_V2.md`, `AGENT_SYSTEM_CORE_RULES_V3.md`, and the rules sections of `SESSION_HANDOVER_2026-02-22_v2.md`.
