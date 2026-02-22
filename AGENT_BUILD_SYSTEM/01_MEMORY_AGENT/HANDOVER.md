# HANDOVER: Memory Agent — Build Step 1 of 8

**Document ID:** AGEN-HNDV-memory-v2
**Date:** 2026-02-22
**Status:** Ready to Build

## FILE LOCATIONS

| File | Location | Purpose |
|------|----------|---------|
| This file | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/01_MEMORY_AGENT/HANDOVER.md` | Upload as Claude Project knowledge document |
| Project Instructions | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/01_MEMORY_AGENT/PROJECT_INSTRUCTIONS.md` | Paste into Claude Project Custom Instructions |
| Governance | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md` | Upload as Claude Project knowledge document (same in every project) |
| Master Handover | `GitHub: bermingham85/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md` | Upload as Claude Project knowledge document (same in every project) |
| Notion Page | https://www.notion.so/30e74ec031148197be2cf0885b30326b | Spec and status tracking |

## BUILD OUTPUTS GO TO

| Output | Destination |
|--------|-------------|
| Supabase SQL | Run directly on Supabase project `ylcepmvbjjnwmzvevxid` |
| n8n workflow JSON | Import into n8n `http://192.168.50.246:5678` |
| System prompt | Store in Notion + GitHub `bermingham85/code-artifacts` |
| Code artifacts | GitHub `bermingham85/code-artifacts` |
| Test results | Notion Document Control |

---

## CONTEXT PROMPT (Paste this into new conversation)

```
I'm building a modular autonomous agent system. This conversation focuses on building ONE agent: the Memory Agent.

**What this agent does:**
- Stores and retrieves context across conversations
- Persists decisions, preferences, patterns
- Enables ANY agent to access historical context
- Full-text search across all stored memories
- Links memories to projects and agents

**Where it sits in the system:**
- Called by ALL other agents to store/retrieve context
- Called at session start to load relevant memories
- Central knowledge authority for the entire system

**What I need you to build:**
1. Complete n8n workflow callable via webhook
2. Multiple actions: store, retrieve, search, list
3. Full-text search in Supabase with relevance ranking
4. Categorization and tagging of memories
5. Project and agent linking

**My infrastructure:**
- n8n: http://192.168.50.246:5678 (local) or https://bermech.app.n8n.cloud
- Supabase: ylcepmvbjjnwmzvevxid
- Claude API available

**Existing memory sources to integrate:**
- PROJECT_MEMORY_BANK.json (in code-artifacts repo)
- MASTER_PROMPT_LIBRARY.md (10 shortcuts)
- contexts table (33 existing rows)
- Claude's userMemories
- planning_conversations table

**Integration requirements:**
- Webhook endpoint: POST /webhook/memory-agent
- Input: { "action": "store|retrieve|search|list", ... }
- Output: { "memories": [...], "relevance": [...] }
- Must support full-text search
- Must link to projects and agents

**Deliverables needed:**
1. Supabase table creation SQL with full-text indexes
2. Search function SQL
3. Complete n8n workflow JSON (importable)
4. System prompt for Claude API (categorization)
5. Memory schema and tagging system
6. Test cases to verify it works

Build this as a complete, working module. No partial solutions.
```

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

OUTPUT FORMATS:

For STORE:
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

For RETRIEVE:
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

For SEARCH:
{
  "action": "search",
  "query": "search terms",
  "filters": {"type": "decision", "project_id": "uuid"},
  "results": [...],
  "total_results": 10
}
```

---

## SUPABASE TABLE SQL

```sql
-- Core memory storage
CREATE TABLE IF NOT EXISTS agent_memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  type TEXT NOT NULL CHECK (type IN ('decision', 'preference', 'pattern', 'context', 'relationship')),
  category TEXT CHECK (category IN ('technical', 'business', 'workflow', 'personal')),
  project_id UUID REFERENCES agent_projects(id),
  agent_source TEXT,
  content TEXT NOT NULL,
  tags TEXT[],
  related_memories UUID[],
  confidence TEXT DEFAULT 'medium' CHECK (confidence IN ('high', 'medium', 'low')),
  source TEXT DEFAULT 'conversation' CHECK (source IN ('conversation', 'import', 'explicit', 'derived')),
  created_at TIMESTAMPTZ DEFAULT now(),
  last_accessed TIMESTAMPTZ,
  access_count INTEGER DEFAULT 0
);

-- Full-text search index
CREATE INDEX idx_memories_fts ON agent_memories 
  USING gin(to_tsvector('english', content));

-- Other indexes
CREATE INDEX idx_memories_tags ON agent_memories USING gin(tags);
CREATE INDEX idx_memories_type ON agent_memories(type);
CREATE INDEX idx_memories_category ON agent_memories(category);
CREATE INDEX idx_memories_project ON agent_memories(project_id);
CREATE INDEX idx_memories_created ON agent_memories(created_at DESC);

-- Full-text search function
CREATE OR REPLACE FUNCTION search_memories(
  search_query TEXT,
  filter_type TEXT DEFAULT NULL,
  filter_category TEXT DEFAULT NULL,
  filter_project UUID DEFAULT NULL,
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  type TEXT,
  category TEXT,
  content TEXT,
  tags TEXT[],
  project_id UUID,
  relevance REAL,
  created_at TIMESTAMPTZ
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    m.id,
    m.type,
    m.category,
    m.content,
    m.tags,
    m.project_id,
    ts_rank(to_tsvector('english', m.content), plainto_tsquery('english', search_query)) as relevance,
    m.created_at
  FROM agent_memories m
  WHERE 
    (search_query IS NULL OR to_tsvector('english', m.content) @@ plainto_tsquery('english', search_query))
    AND (filter_type IS NULL OR m.type = filter_type)
    AND (filter_category IS NULL OR m.category = filter_category)
    AND (filter_project IS NULL OR m.project_id = filter_project)
  ORDER BY relevance DESC, m.created_at DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- Update access tracking
CREATE OR REPLACE FUNCTION update_memory_access()
RETURNS TRIGGER AS $$
BEGIN
  -- This would be called when memory is retrieved
  UPDATE agent_memories 
  SET last_accessed = now(), access_count = access_count + 1
  WHERE id = NEW.id;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Tag search function
CREATE OR REPLACE FUNCTION search_memories_by_tags(
  search_tags TEXT[],
  limit_count INTEGER DEFAULT 10
)
RETURNS TABLE (
  id UUID,
  type TEXT,
  content TEXT,
  tags TEXT[],
  match_count INTEGER
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    m.id,
    m.type,
    m.content,
    m.tags,
    array_length(m.tags & search_tags, 1) as match_count
  FROM agent_memories m
  WHERE m.tags && search_tags
  ORDER BY match_count DESC, m.created_at DESC
  LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;
```

---

## N8N WORKFLOW STRUCTURE

```
Webhook (POST /memory-agent)
    ↓
Switch Node (action?)
    │
    ├── store → Code Node (extract/categorize)
    │            ↓
    │            HTTP Request (Claude - categorization) [OPTIONAL]
    │            ↓
    │            Supabase Insert (agent_memories)
    │
    ├── retrieve → Code Node (build query)
    │               ↓
    │               Supabase Function (search_memories)
    │               ↓
    │               Code Node (format results)
    │
    ├── search → Same as retrieve with different params
    │
    └── list → Supabase Select (with filters)
               ↓
               Code Node (format list)
    ↓
Respond to Webhook (return results)
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

## MEMORY SCHEMA (Knowledge Doc)

```json
{
  "memory": {
    "id": "uuid",
    "type": "decision|preference|pattern|context|relationship",
    "category": "technical|business|workflow|personal",
    "content": "the actual memory content",
    "tags": ["searchable", "tags"],
    "project_id": "uuid or null",
    "agent_source": "which agent created this",
    "related_memories": ["uuid1", "uuid2"],
    "confidence": "high|medium|low",
    "source": "conversation|import|explicit|derived",
    "created_at": "timestamp",
    "last_accessed": "timestamp",
    "access_count": 0
  }
}
```

---

## CORE PREFERENCES TO SEED (Knowledge Doc)

```
TYPE: preference
CATEGORY: workflow
CONTENT: Michael prefers complete solutions, never partial. Step-by-step instructions. No overwhelming information dumps. One-button automation preferred. ADHD-friendly formatting.

TYPE: preference
CATEGORY: technical
CONTENT: Use n8n for orchestration (not code-heavy Python). Supabase for database. Desktop Commander MCP for local file ops. Claude for complex reasoning. OpenAI for structured outputs.

TYPE: pattern
CATEGORY: technical
CONTENT: Standard pattern: Webhook → n8n → Supabase → Response. File processing: Watch → Process → Store. AI pipeline: Trigger → Multi-AI → Validate → Output.

TYPE: context
CATEGORY: business
CONTENT: Active businesses: Bermech Ltd (Airbnb Dublin), Jesse Music (streaming), Taleweaver (book automation), Balding Pig (satirical products). Based in Ireland.

TYPE: decision
CATEGORY: technical
CONTENT: Agent system architecture: 7 agents (Spec, Arch, Builder, Verify, PM, Router, Memory). All callable via n8n webhooks. State in Supabase. Modular build approach.
```

---

## TEST CASES

**Test 1: Store memory**
Input: `{"action": "store", "content": "We decided to use UUID primary keys", "type": "decision", "tags": ["database", "supabase"]}`
Expected: Memory stored, ID returned

**Test 2: Search memories**
Input: `{"action": "search", "query": "database primary keys"}`
Expected: Returns stored decision with high relevance

**Test 3: Retrieve by type**
Input: `{"action": "retrieve", "type": "preference", "limit": 5}`
Expected: Returns all preferences

**Test 4: Tag search**
Input: `{"action": "search", "tags": ["n8n", "webhook"]}`
Expected: Returns all memories with matching tags

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

## IMPORT EXISTING KNOWLEDGE

```sql
-- Import from existing contexts table (if exists)
INSERT INTO agent_memories (type, category, content, tags, source)
SELECT 
  'context',
  'business',
  context_value,
  ARRAY['imported', 'legacy'],
  'import'
FROM contexts;

-- Import core preferences
INSERT INTO agent_memories (type, category, content, tags, confidence, source) VALUES
('preference', 'workflow', 'Complete solutions only, never partial. Step-by-step. No overwhelming info. One-button automation.', ARRAY['adhd', 'style', 'core'], 'high', 'explicit'),
('preference', 'technical', 'n8n for orchestration, Supabase for database, Desktop Commander for files.', ARRAY['stack', 'tools', 'core'], 'high', 'explicit'),
('pattern', 'technical', 'Webhook → n8n → Supabase → Response', ARRAY['pattern', 'n8n', 'workflow'], 'high', 'explicit');
```

---

## AFTER BUILDING

Return to Master Handover with:
- [ ] Supabase table and functions created
- [ ] n8n workflow JSON (exportable)
- [ ] Core preferences seeded
- [ ] Full-text search working
- [ ] Integration tested

**Notion Reference:** https://www.notion.so/30e74ec031148197be2cf0885b30326b
