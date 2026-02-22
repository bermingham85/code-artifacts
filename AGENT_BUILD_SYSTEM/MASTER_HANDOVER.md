# AGENT BUILD SYSTEM — MASTER HANDOVER

**Document ID:** AGEN-HNDV-master-v3  
**Date:** 2026-02-22  
**Status:** Architecture Complete, Build Pending  
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

## BUILD ORDER (FOLLOW THIS SEQUENCE)

Build each agent in a **separate Claude Project**. Each project gets:

1. `GOVERNANCE.md` — uploaded as knowledge document (same file in every project)
2. `PROJECT_INSTRUCTIONS.md` — pasted as the Project's custom instructions
3. `HANDOVER.md` — uploaded as knowledge document (agent-specific)

### Sequence:

| Step | Folder | Why This Order |
|------|--------|----------------|
| 1 | `01_MEMORY_AGENT/` | Foundational — stores context for all others |
| 2 | `02_PROJECT_MANAGER/` | State tracking for all projects |
| 3 | `03_SPECIFICATION_AGENT/` | Entry point for new projects |
| 4 | `04_ROUTER_AGENT/` | Traffic direction |
| 5 | `05_ARCHITECTURE_AGENT/` | Task decomposition |
| 6 | `06_BUILDER_AGENT/` | Code production |
| 7 | `07_VERIFICATION_AGENT/` | Quality gates |
| 8 | `08_FINAL_INTEGRATION/` | Joins all agents together |

---

## CREATING EACH CLAUDE PROJECT

For each agent folder:

1. **Create new Claude Project** named: `Agent Build: [Agent Name]`
2. **Upload knowledge documents:**
   - `GOVERNANCE.md` (from root — same file every time)
   - `HANDOVER.md` (from the agent's folder)
3. **Set project instructions:** Copy-paste contents of `PROJECT_INSTRUCTIONS.md`
4. **Start conversation** — the instructions tell Claude exactly what to build

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
├── README.md                     ← You are here
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

**SUPERSEDED FILES (do not use):**
- ~~AGENT_SYSTEM_CORE_RULES.md~~ → replaced by GOVERNANCE.md
- ~~AGENT_SYSTEM_CORE_RULES_V2.md~~ → replaced by GOVERNANCE.md
- ~~AGENT_SYSTEM_CORE_RULES_V3.md~~ → replaced by GOVERNANCE.md
- ~~AGENT_SYSTEM_MASTER_HANDOVER.md (old)~~ → replaced by this file
