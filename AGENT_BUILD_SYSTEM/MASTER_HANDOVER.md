# AGENT BUILD SYSTEM — MASTER HANDOVER

**Document ID:** AGEN-HNDV-master-v4  
**Date:** 2026-02-22  
**Status:** Memory Agent Built, Remaining Agents Pending  
**Owner:** Michael Bermingham

> **GOVERNANCE:** All rules, naming conventions, and protocols are in `GOVERNANCE.md`.  
> That document is the single source of truth and MUST be loaded into every Claude Project.

---

## WHAT THIS IS

A 7-agent autonomous system where each agent:
- Has a specific role and expertise boundary
- Operates as a standalone n8n workflow callable via webhook
- Persists state to Supabase
- Can be built independently then joined together
- Makes decisions within its function scope

---

## THE 7 AGENTS

| # | Agent | Role | Webhook | Notion Doc |
|---|-------|------|---------|------------|
| 1 | Memory Agent | Store/retrieve context | `/memory-agent` | [Link](https://www.notion.so/30e74ec031148197be2cf0885b30326b) |
| 2 | Project Manager | Track state across sessions | `/project-manager` | [Link](https://www.notion.so/30e74ec03114812491b3cadce807f5f3) |
| 3 | Specification Agent | Force clarity, capture requirements | `/specification-agent` | [Link](https://www.notion.so/30e74ec0311481c0819edeb401857998) |
| 4 | Router Agent | Route requests to correct agent | `/agent` | [Link](https://www.notion.so/30e74ec0311481b9975ecc1e04a85c8e) |
| 5 | Architecture Agent | Decompose specs into tasks | `/architecture-agent` | [Link](https://www.notion.so/30e74ec0311481089700e059eeba7b09) |
| 6 | Builder Agent | Translate tasks to code | `/builder-agent` | [Link](https://www.notion.so/30e74ec03114810c83e5f2f60821e339) |
| 7 | Verification Agent | Check builds against specs | `/verification-agent` | [Link](https://www.notion.so/30e74ec0311481609a8ad94546a95b61) |
| 8 | Final Integration | Join all agents together | — | [Link](https://www.notion.so/30e74ec03114814e8e37f428fc7ec655) |

**Master Index:** [https://www.notion.so/30e74ec031148101a7ddde4b0c7b2769](https://www.notion.so/30e74ec031148101a7ddde4b0c7b2769)

---

## SHARED INFRASTRUCTURE

### n8n Credentials (same across ALL agent workflows)

| What | Credential Name in n8n | Credential ID |
|------|----------------------|---------------|
| Supabase API | `Supabase account` | `a7fYXsrHUIj3HcnW` |
| Postgres (direct SQL) | `Postgres - Agent System` | `1Prz5GUFcAMM2Dv1` |

### Connection Details

| Service | URL |
|---------|-----|
| n8n Local | `http://192.168.50.246:5678` |
| n8n Cloud | `https://bermech.app.n8n.cloud` |
| Supabase | `https://ylcepmvbjjnwmzvevxid.supabase.co` |
| GitHub | `bermingham85/code-artifacts` |

---

## BUILD ORDER (FOLLOW THIS SEQUENCE)

Build each agent in a **separate Claude Project**. Each project gets:

1. `GOVERNANCE.md` — uploaded as knowledge document (same file in every project)
2. `HANDOVER.md` — uploaded as knowledge document (agent-specific)
3. `PROJECT_INSTRUCTIONS.md` — pasted as the Project's custom instructions

### Sequence:

| Step | Folder | Status | Why This Order |
|------|--------|--------|----------------|
| 1 | `01_MEMORY_AGENT/` | **Built** — workflow active, tables populated | Foundational — stores context for all others |
| 2 | `02_PROJECT_MANAGER/` | Pending | State tracking for all projects |
| 3 | `03_SPECIFICATION_AGENT/` | Pending | Entry point for new projects |
| 4 | `04_ROUTER_AGENT/` | Pending | Traffic direction |
| 5 | `05_ARCHITECTURE_AGENT/` | Pending | Task decomposition |
| 6 | `06_BUILDER_AGENT/` | Pending | Code production |
| 7 | `07_VERIFICATION_AGENT/` | Pending | Quality gates |
| 8 | `08_FINAL_INTEGRATION/` | Pending | Joins all agents together |

---

## CREATING EACH CLAUDE PROJECT

For each agent folder:

1. **Create new Claude Project** named: `Agent Build: [Agent Name]`
2. **Upload knowledge documents:**
   - `GOVERNANCE.md` (from root — same file every time)
   - `HANDOVER.md` (from the agent's folder)
3. **Set project instructions:** Copy-paste contents of `PROJECT_INSTRUCTIONS.md`
4. **Start conversation** — the instructions tell Claude to AUDIT FIRST then build gaps

**IMPORTANT:** The agent MUST audit existing infrastructure before building anything. This is enforced by GOVERNANCE.md Rule 0. If the agent starts creating tables or workflows without checking what exists first, stop it and point to Rule 0.

---

## EXISTING INFRASTRUCTURE (as of 2026-02-22)

### Supabase Tables That Already Exist

| Table | Rows | Status |
|-------|------|--------|
| `agent_memories` | 40+ | Working — full-text search, tags, indexes |
| `agent_projects` | 10 | Working — all project codes populated |

### Supabase Functions That Already Exist

- `search_memories(search_query, filter_type, filter_category, filter_project, limit_count)`
- `search_memories_by_tags(search_tags, filter_type, limit_count)`
- `touch_memory(memory_id)`

### n8n Workflows That Already Exist

| Workflow | ID | Nodes | Status |
|----------|----|-------|--------|
| Memory Agent | `YuY8FL47SB12oy7J` | 20 | Active |

---

## FINAL INTEGRATION

After all 7 agents are built independently:

1. Run master Supabase migration (all tables)
2. Deploy all n8n workflows
3. Connect via Master Orchestrator workflow (step 8)
4. Test end-to-end flows:
   - New project: User → Router → Spec → Arch → Build → Verify
   - Status query: User → Router → PM
   - Memory: User → Router → Memory

---

## FOLDER STRUCTURE

```
AGENT_BUILD_SYSTEM/
├── GOVERNANCE.md                 ← THE rules (upload to EVERY project)
├── MASTER_HANDOVER.md            ← This file (system overview)
├── 01_MEMORY_AGENT/
│   ├── PROJECT_INSTRUCTIONS.md   ← Paste as Claude Project instructions
│   └── HANDOVER.md               ← Upload as knowledge document
├── 02_PROJECT_MANAGER/
│   ├── PROJECT_INSTRUCTIONS.md
│   └── HANDOVER.md
├── 03_SPECIFICATION_AGENT/
│   ├── PROJECT_INSTRUCTIONS.md
│   └── HANDOVER.md
├── 04_ROUTER_AGENT/
│   ├── PROJECT_INSTRUCTIONS.md
│   └── HANDOVER.md
├── 05_ARCHITECTURE_AGENT/
│   ├── PROJECT_INSTRUCTIONS.md
│   └── HANDOVER.md
├── 06_BUILDER_AGENT/
│   ├── PROJECT_INSTRUCTIONS.md
│   └── HANDOVER.md
├── 07_VERIFICATION_AGENT/
│   ├── PROJECT_INSTRUCTIONS.md
│   └── HANDOVER.md
└── 08_FINAL_INTEGRATION/
    ├── PROJECT_INSTRUCTIONS.md
    └── HANDOVER.md
```

---

## VERSION CONTROL

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-02-22 | Initial master handover |
| 2.0 | 2026-02-22 | Added folder structure and setup instructions |
| 3.0 | 2026-02-22 | Consolidated with governance reference |
| 4.0 | 2026-02-22 | **Post-mortem fix.** Added shared credential reference, existing infrastructure section, build status tracking, audit-first warning. Memory Agent build rebuilt existing infrastructure because handover didn't enforce audit-before-build. |

**SUPERSEDED FILES (do not use):**
- ~~AGENT_SYSTEM_CORE_RULES.md~~ → replaced by GOVERNANCE.md
- ~~AGENT_SYSTEM_CORE_RULES_V2.md~~ → replaced by GOVERNANCE.md
- ~~AGENT_SYSTEM_CORE_RULES_V3.md~~ → replaced by GOVERNANCE.md
- ~~AGENT_SYSTEM_MASTER_HANDOVER.md (old)~~ → replaced by this file
