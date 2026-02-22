# AGENT BUILD SYSTEM

**GitHub:** `bermingham85/code-artifacts` → `AGENT_BUILD_SYSTEM/`  
**Full URL:** https://github.com/bermingham85/code-artifacts/tree/main/AGENT_BUILD_SYSTEM  
**Backup:** QNAP NAS → `/share/Projects/AGENT_BUILD_SYSTEM/`

---

## SETUP: How to Create Each Claude Project

For **each agent** (build in order 01 → 08):

### Step 1: Create Claude Project
Name it: `Agent Build: [Agent Name]`

### Step 2: Settings → Custom Instructions
Open `PROJECT_INSTRUCTIONS.md` from the agent's folder.  
**Copy-paste the entire contents** into the project's Custom Instructions field.

### Step 3: Upload Knowledge Documents (3 files per project)
Upload these files into the project's knowledge documents:

| File | Location | Same every time? |
|------|----------|------------------|
| `GOVERNANCE.md` | Root folder | ✅ Yes — same file in every project |
| `MASTER_HANDOVER.md` | Root folder | ✅ Yes — same file in every project |
| `HANDOVER.md` | Agent's own folder (e.g. `01_MEMORY_AGENT/`) | ❌ No — different per agent |

### Step 4: Start Building
Open a conversation and send:
> Build this agent following the project instructions and handover.

The instructions + governance + handover give Claude everything it needs.

---

## BUILD ORDER (DO NOT SKIP)

| Step | Folder | Agent | Why This Order |
|------|--------|-------|----------------|
| 1 | `01_MEMORY_AGENT/` | Memory Agent | Foundational — stores context for all others |
| 2 | `02_PROJECT_MANAGER/` | Project Manager | State tracking for all projects |
| 3 | `03_SPECIFICATION_AGENT/` | Specification Agent | Entry point for new projects |
| 4 | `04_ROUTER_AGENT/` | Router Agent | Traffic direction (main entry point) |
| 5 | `05_ARCHITECTURE_AGENT/` | Architecture Agent | Task decomposition |
| 6 | `06_BUILDER_AGENT/` | Builder Agent | Code production |
| 7 | `07_VERIFICATION_AGENT/` | Verification Agent | Quality gates |
| 8 | `08_FINAL_INTEGRATION/` | Final Integration | Joins all agents together |

**Parallel builds:** Agents 1-4 must be sequential (each depends on the previous). Agents 5-7 can potentially run in parallel after Agent 4 is done. Agent 8 requires all others complete.

---

## WHAT EACH AGENT BUILD PRODUCES

Every agent build session delivers:
- Supabase table SQL (ready to run)
- n8n workflow JSON (ready to import)
- System prompt for Claude API calls
- Test cases with expected results
- Integration documentation
- Document Control registration payload

---

## FILE STRUCTURE

```
AGENT_BUILD_SYSTEM/                          ← GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/
├── README.md                                ← You are here
├── GOVERNANCE.md                            ← THE rules — upload to EVERY Claude Project
├── MASTER_HANDOVER.md                       ← System overview — upload to EVERY Claude Project
├── 01_MEMORY_AGENT/
│   ├── PROJECT_INSTRUCTIONS.md              ← Paste into Claude Project settings
│   └── HANDOVER.md                          ← Upload as knowledge document
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

## STORAGE LOCATIONS

| What | Primary Location | Backup |
|------|-----------------|--------|
| This folder | GitHub `bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/` | QNAP NAS |
| Built n8n workflows | n8n local `http://localhost:5678` | GitHub export |
| Built Supabase tables | Supabase `ylcepmvbjjnwmzvevxid` | — |
| Specs & docs | Notion + GitHub | — |
| Code artifacts | GitHub `bermingham85/code-artifacts` | QNAP NAS |

---

## SUPERSEDED FILES (DO NOT USE)

- ~~AGENT_SYSTEM_CORE_RULES.md (v1, v2, v3)~~ → replaced by `GOVERNANCE.md`
- ~~AGENT_SYSTEM_MASTER_HANDOVER.md (old)~~ → replaced by `MASTER_HANDOVER.md`
- ~~SESSION_HANDOVER_2026-02-22_v2.md rules sections~~ → replaced by `GOVERNANCE.md`
