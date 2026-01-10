# PROJECT HANDOVER - Autonomous Task Delegation System

## IMMEDIATE CONTEXT LOAD

```bash
# Primary context source
curl http://localhost:8765/context

# Fallback: Load from GitHub
git clone https://github.com/bermingham85/code-artifacts.git
# Then read: PROJECT_MEMORY_BANK.json
```

**Code Artifacts Repo:** https://github.com/bermingham85/code-artifacts

Contains:
- `PROJECT_MEMORY_BANK.json` - Master context (~4,500 tokens)
- `sql_schemas/COMPLETE_SUPABASE_SCHEMA.sql` - All Supabase tables
- `novel_writer_workflow.json` - n8n validation stack
- `orchestrator.py` - Python multi-agent file organizer
- `MASTER_PROMPT_LIBRARY.md` - 10 shortcut prompts

---

## ACCESS CONTROL

| Resource | Endpoint | Auth |
|----------|----------|------|
| Context API | http://localhost:8765 | None |
| n8n Local | http://192.168.50.246:5678 | Basic |
| n8n Cloud | https://bermech.app.n8n.cloud | Bearer |
| n8n MCP | localhost:5678/mcp-server/http | Bearer ****KSaU |
| Supabase | ylcepmvbjjnwmzvevxid.supabase.co | Service key in .env.shared |
| PostgreSQL | 192.168.50.246:5432 | postgres/[check credentials] |

**Credentials Location:** `C:\Users\bermi\Projects\.env.shared`

---

## MEMORY SYSTEM

1. **Claude Internal Memory** - Anthropic's built-in (6 items stored)
2. **Context API** - http://localhost:8765/context (memory.json + skills)
3. **GitHub Repo** - https://github.com/bermingham85/code-artifacts
4. **Local Files:**
   - `C:\Users\bermi\Projects\PROJECT_MEMORY_BANK.json`
   - `C:\Users\bermi\.ai_context\memory.json`

**Session Start Protocol:**
1. Fetch http://localhost:8765/context
2. If empty, load PROJECT_MEMORY_BANK.json from GitHub or local
3. Check for [shortcut] triggers
4. Save skill when multi-step procedure works

---

## COMPLETED WORK

### Code Consolidation (DONE)
- [x] Extracted all working code from conversation history
- [x] Created CODE_ARTIFACTS directory structure
- [x] Pushed to GitHub: bermingham85/code-artifacts
- [x] SQL schema consolidated (25+ tables)
- [x] Novel Writer workflow with 3 validation gates
- [x] Python orchestrator (multi-agent file organizer)
- [x] Prompt library (10 shortcuts)
- [x] PROJECT_MEMORY_BANK.json created
- [x] Context API memory populated
- [x] Skill registered: code-artifacts

### Infrastructure (DONE)
- [x] Context API running on localhost:8765
- [x] 5 skills registered in .ai_context/.skills/
- [x] n8n MCP endpoint configured
- [x] Supabase project identified: ylcepmvbjjnwmzvevxid

---

## REMAINING TASKS

### Priority 1: Database Deployment
- [ ] Run COMPLETE_SUPABASE_SCHEMA.sql in Supabase SQL Editor
- [ ] Verify all 25+ tables created
- [ ] Test foreign key relationships
- [ ] Seed phrase_tracker with anti-LLM patterns

### Priority 2: n8n Workflow Import
- [ ] Import novel_writer_workflow.json to n8n
- [ ] Update credential IDs (OpenAI, Supabase)
- [ ] Test trigger mechanism
- [ ] Verify 3 validation gates fire correctly

### Priority 3: Novel Writer Data Population
- [ ] Create style_profile (is_active=true)
- [ ] Populate chapter_manifest for target book
- [ ] Add characters with speech patterns
- [ ] Set world_settings and rules

### Priority 4: Orchestrator Deployment
- [ ] Deploy orchestrator.py to C:\tools\ai_organizer\
- [ ] Create virtual environment
- [ ] Install requirements (watchdog, xxhash, pyyaml)
- [ ] Test with --process flag before --watch

### Priority 5: GitHub Task Delegation System
- [ ] Create GitHub Issues for each platform task
- [ ] Label by platform: [n8n], [supabase], [python], [claude]
- [ ] Set up GitHub Actions for task routing
- [ ] Create webhook to receive completion callbacks

---

## TASK DELEGATION PROTOCOL

### GitHub Issues as Task Queue

Create issues in `bermingham85/code-artifacts` with labels:

```
[platform:n8n] - Tasks for n8n workflows
[platform:supabase] - Database tasks
[platform:python] - Script execution
[platform:claude] - AI reasoning tasks
[status:pending] - Awaiting execution
[status:in-progress] - Being worked
[status:complete] - Done, awaiting verification
[status:verified] - Confirmed working
```

### Task Flow

```
1. Claude creates GitHub Issue with task spec
2. Issue labeled with target platform
3. Platform picks up task (webhook or polling)
4. Platform executes and reports back
5. Results posted as Issue comment
6. Claude verifies and closes or reopens
```

### n8n Webhook Receivers

```
POST https://bermech.app.n8n.cloud/webhook/github-task
{
  "action": "execute",
  "platform": "n8n",
  "task_id": "issue-123",
  "payload": { ... }
}
```

### Completion Callback

```
POST https://bermech.app.n8n.cloud/webhook/task-complete
{
  "task_id": "issue-123",
  "status": "complete",
  "result": { ... },
  "artifacts": ["url1", "url2"]
}
```

---

## YOUR INSTRUCTIONS

1. **Load Context First**
   - Fetch http://localhost:8765/context
   - Or clone https://github.com/bermingham85/code-artifacts

2. **Create GitHub Issues**
   - One issue per task from REMAINING TASKS
   - Label with platform and status
   - Include acceptance criteria

3. **Set Up Delegation Workflow**
   - Create n8n workflow: GitHub Issue → Platform Router → Execute → Callback
   - Test with one simple task first

4. **Execute in Order**
   - Priority 1 first (database must exist before workflows)
   - Each task completion unlocks next priority

5. **Report Back**
   - Update PROJECT_MEMORY_BANK.json with progress
   - Push changes to GitHub
   - Post summary when complete

---

## QUICK REFERENCE

| What | Where |
|------|-------|
| Code Artifacts | https://github.com/bermingham85/code-artifacts |
| Context API | http://localhost:8765/context |
| n8n Cloud | https://bermech.app.n8n.cloud |
| Supabase | ylcepmvbjjnwmzvevxid |
| Memory JSON | C:\Users\bermi\.ai_context\memory.json |
| Skills | C:\Users\bermi\.ai_context\.skills\ |

---

## START COMMAND

"Load context from http://localhost:8765/context, review the REMAINING TASKS, create GitHub Issues for each task labeled by platform, then execute Priority 1 (database deployment) first. Report progress after each priority level."
