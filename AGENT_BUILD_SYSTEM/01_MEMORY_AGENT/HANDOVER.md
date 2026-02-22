# HANDOVER: Memory Agent — Build Step 1 of 8

**Document ID:** AGEN-HNDV-memory-v3  
**Date:** 2026-02-22  
**Status:** Partially Built — Audit and Complete

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|----------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/01_MEMORY_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/01_MEMORY_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec031148197be2cf0885b30326b | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Supabase SQL | Run directly on Supabase project `ylcepmvbjjnwmzvevxid` |
| n8n workflow JSON | Import into n8n `http://localhost:5678` |
| System prompt | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Code artifacts | GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## CRITICAL: EXISTING INFRASTRUCTURE — DO NOT RECREATE

A previous build session created infrastructure that MUST be preserved. **Audit first, build only what's missing.**

### What Already Exists in Supabase

**Table: `agent_memories`** — 40 rows of real data, DO NOT DROP OR RECREATE
- Columns: id (UUID PK), type, category, project_id (FK → agent_projects), agent_source, content, tags (TEXT[]), related_memories (UUID[]), confidence, source, created_at, last_accessed, access_count
- Types in use: context (35), preference (3), pattern (1), decision (1)
- Categories in use: business (34), technical (4), workflow (1)
- Contains: Jesse Beanstalk story bible data, system preferences, infrastructure context, architecture decisions

**Table: `agent_projects`** — 10 rows of real data, DO NOT DROP OR RECREATE
- All project codes populated: AGEN, BERM, BPIG, FINX, GNRL, GOVN, INFR, JESS, MILK, TALE
- Columns: id (UUID PK), code, name, description, status, created_at, updated_at

**Functions that exist:**
- `search_memories()` — full-text search with filters
- `search_memories_by_tags()` — tag-based search
- `touch_memory()` — access tracking
- `search_v2()`, `search_by_timestamp()`, `search_legacy_v1()`, `search()` — additional variants

**Indexes that exist:** (verify during audit)
- Full-text search index on content
- GIN index on tags
- Indexes on type, category, project_id, created_at

### What Already Exists in n8n

**Workflow: "Memory Agent"** (id: YuY8FL47SB12oy7J)
- 20 nodes, active, created 2026-02-22
- May be incomplete or have issues from failed build session
- **Audit this workflow — it may need fixing or replacing, but check first**

### What Needs to Be Verified

During your audit (Step 1 of PROJECT_INSTRUCTIONS), confirm:
1. Do all required columns exist on agent_memories?
2. Do the search functions work correctly? (Test them with a query)
3. Is the n8n workflow functional? (Check node connections, test webhook)
4. Are there any missing indexes?
5. Is the webhook endpoint `/webhook/memory-agent` responding?

### What May Need to Be Added

Based on the spec, these items may be missing (verify during audit):
- RLS policies on agent_memories (if not set up)
- Error handling in n8n workflow
- Claude API integration node for categorization
- Proper response formatting in n8n workflow
- Test coverage

---

## SYSTEM PROMPT (For Claude API call - categorization)

```
You are the Memory Agent. You store and retrieve context so nothing is ever forgotten.

RULES:
1. ALWAYS store important decisions, preferences, and outcomes
2. ALWAYS retrieve relevant context when asked
3. NEVER store sensitive credentials (API keys, passwords)
4. ALWAYS categorize memories for easy retrieval
5. ALWAYS link memories to projects/agents when relevant

MEMORY TYPES:
1. DECISION - Architectural choices, technology selections, trade-offs
2. PREFERENCE - User preferences, code style, communication style
3. PATTERN - Solutions that worked, approaches that failed, reusable snippets
4. CONTEXT - Project background, domain knowledge, business rules
5. RELATIONSHIP - How systems connect, dependencies, integration points

CATEGORIZATION PROCESS:

For STORE operations:
1. Extract key information from input
2. Assign type (decision/preference/pattern/context/relationship)
3. Assign category (technical/business/workflow/personal)
4. Generate searchable tags (3-5 tags)
5. Link to project if relevant
6. Store with metadata

For RETRIEVE operations:
1. Parse what's being asked
2. Search by type, tags, project, full-text
3. Rank by relevance and recency
4. Return formatted context

OUTPUT FORMAT FOR STORE:
{
  "action": "store",
  "memory": {
    "id": "generated-uuid",
    "type": "decision",
    "category": "technical",
    "content": "the stored content",
    "tags": ["n8n", "webhook", "pattern"],
    "project_id": "uuid or null",
    "agent_source": "which agent stored this",
    "confidence": "high"
  },
  "status": "stored"
}

OUTPUT FORMAT FOR RETRIEVE:
{
  "action": "retrieve",
  "query": "what was searched",
  "results": [
    {
      "id": "uuid",
      "type": "decision",
      "content": "content",
      "tags": ["tag1", "tag2"],
      "relevance": 0.95,
      "created_at": "timestamp"
    }
  ],
  "total_results": 5
}

OUTPUT FORMAT FOR SEARCH:
{
  "action": "search",
  "query": "search terms",
  "filters": {"type": "decision", "project_id": "uuid"},
  "results": [...],
  "total_results": 10
}
```

---

## EXPECTED TABLE SCHEMA (For reference — DO NOT CREATE, verify against existing)

The `agent_memories` table should have these columns:

| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | gen_random_uuid() |
| type | TEXT | CHECK: decision, preference, pattern, context, relationship |
| category | TEXT | CHECK: technical, business, workflow, personal |
| project_id | UUID FK | References agent_projects(id) |
| agent_source | TEXT | Which agent stored this |
| content | TEXT NOT NULL | The memory content |
| tags | TEXT[] | Searchable tags array |
| related_memories | UUID[] | Links to related memories |
| confidence | TEXT | CHECK: high, medium, low |
| source | TEXT | CHECK: conversation, import, explicit, derived |
| created_at | TIMESTAMPTZ | Default now() |
| last_accessed | TIMESTAMPTZ | Updated on read |
| access_count | INTEGER | Default 0 |

---

## N8N WORKFLOW STRUCTURE (Target Design)

```
Webhook (POST /webhook/memory-agent)
    ↓
Switch Node (action?)
    │
    ├── store → Code Node (validate/prepare)
    │            ↓
    │            HTTP Request (Claude API - categorize) [OPTIONAL]
    │            ↓
    │            Supabase Insert (agent_memories)
    │            ↓
    │            Respond to Webhook
    │
    ├── retrieve → Supabase Function (search_memories)
    │               ↓
    │               Code Node (format results)
    │               ↓
    │               Respond to Webhook
    │
    ├── search → Supabase Function (search_memories / search_memories_by_tags)
    │             ↓
    │             Code Node (format results)
    │             ↓
    │             Respond to Webhook
    │
    └── list → Supabase Select (with filters)
               ↓
               Code Node (format list)
               ↓
               Respond to Webhook
```

**Webhook Input Schema:**
```json
// Store
{
  "action": "store",
  "content": "what to remember",
  "type": "decision|preference|pattern|context|relationship",
  "category": "technical|business|workflow|personal",
  "tags": ["tag1", "tag2"],
  "project_id": "optional uuid",
  "agent_source": "which agent is storing"
}

// Retrieve/Search
{
  "action": "retrieve|search",
  "query": "search terms",
  "type": "optional filter",
  "category": "optional filter",
  "project_id": "optional filter",
  "limit": 10
}

// List
{
  "action": "list",
  "type": "optional filter",
  "project_id": "optional filter",
  "limit": 20
}
```

---

## TEST CASES

**Test 1: Store memory**
Input: `POST /webhook/memory-agent` with `{"action": "store", "content": "Test memory from audit session", "type": "context", "tags": ["test", "audit"]}`
Expected: Memory stored, ID returned, appears in agent_memories table

**Test 2: Search memories (full-text)**
Input: `{"action": "search", "query": "database primary keys"}`
Expected: Returns relevant results with relevance scores

**Test 3: Retrieve by type**
Input: `{"action": "retrieve", "type": "preference", "limit": 5}`
Expected: Returns the 3 existing preference memories

**Test 4: Tag search**
Input: `{"action": "search", "tags": ["core", "preferences"]}`
Expected: Returns memories with matching tags

**Test 5: List with project filter**
Input: `{"action": "list", "project_id": "<JESS project UUID>", "limit": 20}`
Expected: Returns Jesse-related memories

**Test 6: Verify existing data preserved**
Input: `SELECT COUNT(*) FROM agent_memories`
Expected: >= 40 rows (original data intact)

---

## INTEGRATION SPECIFICATION

**Called by:** All agents (store/retrieve), Router Agent, Session start
**Calls:** None (passive storage)
**Stores:** agent_memories table

**Common use cases:**
1. Session start: Load relevant project context
2. Decision made: Store for future reference
3. Pattern found: Store reusable solution
4. Question asked: Search for previous decisions

**Context loading pattern:**
```
At session start:
1. Get project_id from Project Manager
2. Call Memory Agent: search by project_id
3. Also search by common tags
4. Return compiled context
```

---

## AFTER COMPLETING THIS BUILD

Return with:
- [ ] Infrastructure audit documented
- [ ] All gaps identified and filled
- [ ] n8n workflow complete and tested
- [ ] All 6 test cases passing
- [ ] Existing 40 memories preserved
- [ ] Integration documentation complete

**Notion Reference:** https://www.notion.so/30e74ec031148197be2cf0885b30326b
