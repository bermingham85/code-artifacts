# PROJECT APEX v2.2 — HARDENED BUILD SPECIFICATION

**Document:** APEX-MB-DOC-00001  
**Version:** 2.2  
**Author:** Michael Bermingham + Claude (Systems Architect)  
**Date:** 2026-02-27  
**Status:** APPROVED FOR BUILD  

**Changelog from v1.0:**
- Added fallback polling to n8n Watch Folder (Windows FSW unreliable)
- Added dead letter queue for stuck/orphaned tickets
- Added circuit breaker pattern to foreman subprocess execution
- Added process pool + warm cache to ClaudeClaw for Claude Code latency
- Split CLAUDE.md into personality contract + capabilities manifest
- Added watchdog supervisor for both Apex and ClaudeClaw processes
- Added graceful degradation: WhatsApp bridge is fully optional, never blocks boot
- Added retry logic with exponential backoff to foreman execution step
- Added file locking to hub/ writes (prevents partial reads by n8n)
- Added structured health dashboard endpoint for ClaudeClaw
- Added idempotency guard on Work Order processing (duplicate job_id rejection)
- Hardened all Windows path handling with pathlib/path.join
- Added Telegram bot token rotation support
- Added session cleanup cron for stale Claude Code sessions

**v2.0 → v2.1:**
- Enforced subscription-first rule: all Claude interactions via CLI subprocess, never direct API
- Removed `@anthropic-ai/claude-code` from dependencies (not needed, spawn CLI directly)
- Added explicit "do not add ANTHROPIC_API_KEY" note in .env template
- agent.ts and agent-pool.ts now fail loudly if CLI unavailable instead of silently falling back

**v2.1 → v2.2:**
- Added Phase 0: Context Load — mandatory pre-build inventory of existing code
- Prevents Claude Code from rebuilding already-completed work
- Explicit DO NOT REUSE list for abandoned/theoretical code (orchestrator.py, AGENT_REGISTRY, Estate-System)
- References original Apex kickoff conversations for architectural decisions

---

## OWNER CONTEXT

Michael Bermingham, Dublin, Ireland. Entrepreneur running:
- **Bermech Limited** (Airbnb rentals) — project code: BERM
- **Jesse Music** (music production) — project code: JESS
- **Taleweaver** (book automation) — project code: TALE
- **The Balding Pig** (satirical content) — project code: BALP

Michael has ADHD. All outputs must be: step-by-step, complete solutions, no overwhelm, no partial implementations.

---

## INFRASTRUCTURE (ALREADY RUNNING)

| Resource | Location | Notes |
|----------|----------|-------|
| OS | Windows 11 | C:\Users\bermi\Projects\ |
| n8n | 192.168.50.246:5678 | QNAP NAS, always-on |
| Claude Code | v2.1.15 | Authenticated, local |
| GitHub | github.com/bermingham85 | 31 repos, code-artifacts = source of truth |
| MCP filesystem | localhost:9001 | |
| MCP postgres | localhost:9002 | |
| MCP memory | localhost:9003 | |
| MCP github | localhost:9004 | |
| MCP n8n | localhost:9005 | |
| Warp memory | localhost:8765 | Context API |
| Groq API | Available | Whisper STT |
| Gemini API x4 | Available | Video analysis |
| Flux/Fal API | Available | Image generation |
| ElevenLabs API | Available | TTS (not used yet) |

**Existing doc controller state:** Partial build exists in code-artifacts. Two disconnected pieces:
1. n8n webhook stub at `/log-entry` (logs to `agent_logs` table)
2. JS class in `mcp-puppet-pipeline/src/agents/core/doc-organizer.js`

This build replaces both with a single authoritative Python doc_controller.py.

---

## DECISIONS LOCKED

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Telegram library | Grammy | Stable, TypeScript-native, middleware pipeline |
| Voice STT | Groq Whisper | Fast, accurate, free tier sufficient |
| Voice TTS | None for now | Will add ElevenLabs later |
| Memory backend | SQLite + FTS5 | Local-first, zero infrastructure, dual-sector with salience decay |
| Bot language | TypeScript | Grammy ecosystem, type safety for bot logic |
| Factory language | Python | AST parsing, subprocess management, existing skills |
| File watcher | n8n + polling fallback | Windows FSW is unreliable — see Phase 6 |
| WhatsApp bridge | Optional, never blocks boot | whatsapp-web.js breaks regularly |
| Claude Code invocation | Subprocess (`claude -p`) | SDK not mature enough yet |
| Permissions | `--dangerously-skip-permissions` | Single-user local machine, auth gate is ALLOWED_CHAT_ID |

---

## PHASE 0: CONTEXT LOAD (MANDATORY PRE-BUILD)

**Purpose:** Before writing a single line of code, inventory what already exists. This project has prior art scattered across multiple repos and local folders. Rebuilding working code wastes time and violates "Reuse > Research > Create."

**Step 0.1 — Scan local apex directory:**
```
Read C:\Users\bermi\Projects\apex\ recursively.
List every .py, .ts, .js, .json, .md file with its size and last modified date.
Note what appears functional vs. stub/placeholder.
```

**Step 0.2 — Check code-artifacts repo (source of truth):**
```
Read C:\Users\bermi\Projects\code-artifacts\ (or fetch from github.com/bermingham85/code-artifacts)
Check docs/DOCUMENT_REGISTER.md for already-registered documents.
Check if doc_controller.py, foreman.py, indexer.py, or muscles already exist here.
```

**Step 0.3 — Check for prior partial implementations:**
```
Check mcp-puppet-pipeline/src/agents/core/doc-organizer.js — extract any reusable logic for doc_controller.py
Check if n8n webhook stub at /log-entry exists in bermech-n8n-workflows repo
Check if any muscles/ already exist in apex/registry/
```

**Step 0.4 — DO NOT REUSE list (abandoned/theoretical code):**
```
SKIP: AUTOMATION_FRAMEWORK/orchestrator.py — 601 lines, theoretical only, classes defined but never wired to real execution
SKIP: AGENT_REGISTRY/ — config-only, no actual runners
SKIP: Estate-System/ — stalled at Step 9, superseded by this spec
These are absorbed into Apex conceptually but their code is not production-worthy.
```

**Step 0.5 — Build decision matrix:**
```
For each component in Phases 1-10, determine ONE of:
  EXISTS_AND_WORKS → Skip build. Register with doc_controller. Move on.
  EXISTS_BUT_PARTIAL → Finish it per this spec. Don't rebuild from scratch.
  MISSING → Build fresh per this spec.

Print the decision matrix as a table before proceeding to Phase 1.
```

**Output:** A table like:

| Component | Status | Action | Location |
|-----------|--------|--------|----------|
| apex/ directory structure | EXISTS_AND_WORKS | Skip | C:\Users\bermi\Projects\apex\ |
| doc_controller.py | MISSING | Build fresh | — |
| indexer.py | EXISTS_BUT_PARTIAL | Finish | C:\Users\bermi\Projects\apex\indexer.py |
| foreman.py | MISSING | Build fresh | — |
| ... | ... | ... | ... |

**DO NOT proceed to Phase 1 until this table is complete and printed.**

---

## PHASE 1: BUILD THE ESTATE

### Apex Factory

```
C:\Users\bermi\Projects\apex\
  hub\                          → Central Mailbox (n8n watches for .json signal tickets)
    dead_letter\                → [NEW] Tickets undeliverable after 3 retries
  registry\                     → Stockroom (verified Python muscles + manifest)
    clones\                     → GitHub repos cloned here by indexer
    sources.json                → Seed config for indexer
  active_projects\              → Factory Floor
    tasks\                      → Each task: tasks\task_{uuid}\
  audit\                        → Traceable Archive (completed + stamped Work Orders)
    health\                     → Health check reports
  logs\                         → All system logs
  templates\                    → WorkOrder.json + DiagnosticTicket.json blank schemas
  docs\                         → Document Control Register
  supervisor\                   → [NEW] Watchdog configs and PID files
```

### ClaudeClaw Telegram Bridge

```
C:\Users\bermi\Projects\claudeclaw\
  src\
    env.ts                      → Environment variable loader
    config.ts                   → Typed config with defaults
    logger.ts                   → Pino logger setup
    db.ts                       → SQLite schema + migrations
    agent.ts                    → Claude Code subprocess manager
    agent-pool.ts               → [NEW] Warm process pool for latency reduction
    memory.ts                   → Dual-sector FTS5 memory system
    voice.ts                    → Groq Whisper STT handler
    media.ts                    → Photo/doc/video media handler
    scheduler.ts                → Cron-based task scheduler
    schedule-cli.ts             → CLI interface for scheduler
    whatsapp.ts                 → WhatsApp bridge (optional, graceful fail)
    health.ts                   → [NEW] Structured health dashboard
    ticket-server.ts            → [NEW] Express server for /internal/ticket
    bot.ts                      → Grammy bot setup + middleware
    index.ts                    → Entry point, boot sequence
  scripts\
    setup.ts                    → First-run setup wizard
    status.ts                   → Quick status check
    install-windows-startup.bat → Windows Task Scheduler registration
    cleanup-sessions.ts         → [NEW] Stale session cleanup
  store\                        → Runtime data (gitignored)
  workspace\uploads\            → Temp media (gitignored)
  CLAUDE.md                     → Personality contract ONLY
  CAPABILITIES.md               → [NEW] What Claude can access/do (loaded into context)
  .env                          → Secrets
  .env.example                  → Template without secrets
  package.json
  tsconfig.json
```

---

## PHASE 2: DOCUMENT CONTROL SYSTEM

Every file, script, agent, and workflow gets a reference code. No exceptions.

### Reference Code Format

```
[PROJECT]-[ORIGINATOR]-[TYPE]-[SEQ5]
```

**Projects:**

| Code | Entity |
|------|--------|
| APEX | Factory/automation system |
| CLAW | ClaudeClaw Telegram bot |
| BERM | Bermech/Airbnb |
| JESS | Jesse Music |
| TALE | Taleweaver |
| BALP | Balding Pig |

**Originators:**

| Code | Who |
|------|-----|
| MB | Michael Bermingham |
| SYS | System-generated |

**Types:**

| Code | What |
|------|------|
| WF | Workflow (n8n) |
| PY | Python script/muscle |
| TS | TypeScript module |
| CFG | Configuration |
| SCH | Schema/template |
| DOC | Documentation |
| AGT | Agent definition |

**Example:** `APEX-MB-PY-00001` = first Python script Michael created for Apex.

### Document Register

Create `C:\Users\bermi\Projects\apex\docs\DOCUMENT_REGISTER.md`:

```markdown
# Document Register — Project Apex

| Ref Code | Name | Version | Status | Created | Modified | Description | Path |
|----------|------|---------|--------|---------|----------|-------------|------|
```

(Populated automatically by doc_controller.py)

### doc_controller.py (APEX-MB-PY-00000)

Location: `C:\Users\bermi\Projects\apex\docs\doc_controller.py`

**Functions:**

| Function | Purpose |
|----------|---------|
| `issue_ref(project, originator, type)` | Next sequential ref code, registers in DOCUMENT_REGISTER.md |
| `register_doc(ref_code, name, path, description)` | Adds row to register |
| `version_bump(ref_code, change_description, changed_by)` | Increments version, logs to audit |
| `find_doc(query)` | Search by name, path, or description |
| `check_duplicate(name, path)` | Returns existing ref if match found |
| `--init` | CLI flag: creates DOCUMENT_REGISTER.md if missing |
| `--register` | CLI flag: register a new doc interactively |
| `--search "query"` | CLI flag: search register |

**Governing Rule:** Before any new file is created anywhere in this system, doc_controller.py must be called first. If a match is found, return the existing ref. Do not create duplicates.

**Audit Trail:** Every registration and version bump writes to:
`C:\Users\bermi\Projects\apex\audit\doc_audit.jsonl`

Format per line:
```json
{"timestamp": "ISO", "action": "REGISTER|VERSION_BUMP|LOOKUP", "ref_code": "...", "version": "1.0", "changed_by": "MB|SYS", "change_description": "...", "path": "..."}
```

**[NEW] Thread Safety:** All writes to DOCUMENT_REGISTER.md and doc_audit.jsonl use `filelock` (pip package) to prevent corruption from concurrent foreman executions.

---

## PHASE 3: THE WORK ORDER CONTRACT

### WorkOrder.json (APEX-MB-SCH-00001)

Location: `C:\Users\bermi\Projects\apex\templates\WorkOrder.json`

```json
{
  "meta": {
    "job_id": "UUID-v4",
    "ref_code": "APEX-SYS-WF-00000",
    "created_at": "ISO-8601",
    "sender": "AGENT_ID",
    "receiver": "AGENT_ID",
    "project": "PROJECT_NAME",
    "chain_next": null,
    "idempotency_key": null,
    "retry_count": 0,
    "max_retries": 3,
    "priority": "NORMAL"
  },
  "sop": {
    "action": "SCRIPT_NAME_IN_REGISTRY",
    "inputs": [],
    "parameters": {},
    "requirements": [],
    "timeout_seconds": 300
  },
  "task_folder": "C:\\Users\\bermi\\Projects\\apex\\active_projects\\tasks\\task_{uuid}\\",
  "qa_gate": {
    "rule": "FILE_EXISTS | SIZE_GT_ZERO | CONTAINS_STRING | MULTI",
    "checks": [
      {
        "rule": "FILE_EXISTS",
        "target": "OUTPUT_PATH",
        "min_size_bytes": 0,
        "expected_string": null
      }
    ]
  },
  "status": {
    "state": "PENDING",
    "started_at": null,
    "completed_at": null,
    "duration_seconds": null,
    "diagnostic": null,
    "traceback": null,
    "qa_result": null,
    "exit_code": null
  }
}
```

**Changes from v1:**
- Added `idempotency_key` — foreman rejects duplicate job_ids that already exist in audit/
- Added `retry_count` + `max_retries` — enables automatic retry on transient failures
- Added `priority` — NORMAL | HIGH | LOW (future: priority queue in foreman)
- Added `timeout_seconds` in sop — subprocess hard kill after this (default 300s, was unbounded)
- Changed `qa_gate` to support `MULTI` rule with array of checks (compound QA)
- Added `duration_seconds` and `exit_code` in status — better diagnostics

### DiagnosticTicket.json (APEX-MB-SCH-00002)

Location: `C:\Users\bermi\Projects\apex\templates\DiagnosticTicket.json`

```json
{
  "meta": {
    "ticket_id": "UUID-v4",
    "ref_code": "APEX-SYS-WF-00000",
    "parent_job_id": "UUID-v4",
    "created_at": "ISO-8601",
    "severity": "INFO | WARN | ERROR | FATAL"
  },
  "failure": {
    "stage": "VALIDATION | EXECUTION | QA_GATE | DOC_CONTROL | TIMEOUT | IDEMPOTENCY",
    "error_type": "STRING",
    "message": "STRING",
    "traceback": "FULL_TRACEBACK_STRING"
  },
  "resolution": {
    "suggested_action": null,
    "auto_retry": false,
    "retry_count": 0,
    "resolved": false,
    "resolved_at": null
  }
}
```

**Changes from v1:**
- Added `severity` — not all diagnostics are errors (INFO for idempotency skip, WARN for retry)
- Added `TIMEOUT` and `IDEMPOTENCY` failure stages
- Added `auto_retry` flag — foreman can re-queue on transient failures
- Added `retry_count` tracking

**Ticket Routing Rule:** Every DiagnosticTicket is written to `hub\` as `DIAG-{parent_job_id}.json` with `meta.receiver = "originator"` so n8n detects it and routes back.

**[NEW] File Locking on Hub Writes:** All writes to hub/ use atomic write pattern: write to `hub\.tmp\{filename}` first, then `os.rename()` into `hub\`. This prevents n8n from reading partially-written JSON files. On Windows, use `shutil.move()` as fallback if `os.rename()` fails across volumes.

---

## PHASE 4: THE INDEXER

### indexer.py (APEX-MB-PY-00001)

Location: `C:\Users\bermi\Projects\apex\indexer.py`

**Role:** Scan local folders and GitHub repos. Build manifest.json. Enforce Reuse > Research > Create.

### sources.json (APEX-MB-CFG-00001)

Location: `C:\Users\bermi\Projects\apex\registry\sources.json`

```json
{
  "local_paths": [
    "C:\\Users\\bermi\\Projects\\apex\\registry",
    "C:\\Users\\bermi\\Projects\\AUTOMATION_FRAMEWORK",
    "C:\\Users\\bermi\\Projects\\AGENT_REGISTRY"
  ],
  "github_repos": [
    "https://github.com/bermingham85/code-artifacts"
  ],
  "exclude_patterns": [
    "**/node_modules/**",
    "**/__pycache__/**",
    "**/.git/**",
    "**/venv/**",
    "**/.venv/**"
  ],
  "index_interval_minutes": 30
}
```

**Changes from v1:**
- Added `exclude_patterns` — prevents indexing junk directories
- Added `index_interval_minutes` — for scheduled re-indexing

### Logic

1. Clone/pull each GitHub repo into `registry\clones\{repo_name}\`
2. For every `.py` file found across all sources (respecting exclude_patterns):
   - Extract: filename, full path, all function names (via AST), all docstrings, all imports, last_modified
   - Generate AST hash (SHA256) for each function body — catches renamed duplicates across repos
   - **[NEW]** Skip files that haven't changed since last index (compare mtime)
3. Write to `C:\Users\bermi\Projects\apex\registry\manifest.json`

### manifest.json Schema

```json
{
  "last_indexed": "ISO-8601",
  "index_duration_seconds": 0,
  "total_skills": 0,
  "total_files": 0,
  "skills": [
    {
      "id": "UUID",
      "ref_code": "APEX-SYS-PY-00000",
      "name": "function_name",
      "file": "relative_path",
      "source": "local | github",
      "repo": "repo_name_or_null",
      "docstring": "string",
      "imports": [],
      "ast_hash": "sha256",
      "last_modified": "ISO-8601",
      "tags": [],
      "callable_as_muscle": true
    }
  ],
  "duplicates": []
}
```

**Changes from v1:**
- Added `index_duration_seconds` — performance tracking
- Added `total_files` — debugging
- Added `callable_as_muscle` flag — not all functions are standalone muscles
- Added `duplicates` array — surfaces AST hash collisions for human review

### CLI

```
python indexer.py --scan              # Full re-index
python indexer.py --scan --force      # Ignore mtime cache, re-index everything
python indexer.py --search "keyword"  # Ranked matches by name + docstring similarity
python indexer.py --stats             # Summary: skill count, last index, duplicates
python indexer.py --watch             # [NEW] Hot-reload: watch registry/ for changes
```

### Logging

All output to `C:\Users\bermi\Projects\apex\logs\indexer.log`

---

## PHASE 5: THE FOREMAN

### foreman.py (APEX-MB-PY-00002)

Location: `C:\Users\bermi\Projects\apex\foreman.py`

**Trigger:** Called by n8n with path to WorkOrder.json in hub/  
**Usage:** `python foreman.py --ticket "C:\...\hub\WO-XYZ.json"`

### Workflow (9 steps + 3 new safety steps)

#### STEP 0 — IDEMPOTENCY CHECK [NEW]

- Extract `job_id` from ticket
- Search `audit\` for any folder matching `task_{job_id}`
- If found: write DiagnosticTicket with severity=INFO, stage=IDEMPOTENCY, message="Job already processed", halt gracefully
- This prevents re-processing if n8n triggers twice on the same file (common with Windows FSW)

#### STEP 1 — INGEST

- Read and parse WorkOrder.json
- **Validate schema against template.** If invalid: write DiagnosticTicket (severity=ERROR, stage=VALIDATION), halt
- Create task folder: `active_projects\tasks\task_{job_id}\`
- Copy WorkOrder.json into task folder
- Log job_id + sender to `logs\foreman.log`

#### STEP 2 — DOC CONTROL CHECK

- Call `doc_controller.find_doc(sop.action)` to verify the skill is registered
- If unregistered: write DiagnosticTicket (stage=DOC_CONTROL), halt

#### STEP 3 — MANIFEST LOOKUP (REUSE GATE)

- Search `manifest.json` for skill matching `sop.action`
- If not found: DiagnosticTicket message="Skill not in registry. Run indexer.py --scan", halt
- If found: log skill path, proceed

#### STEP 4 — PREREQUISITE VALIDATION

- Check all `sop.inputs` exist and are non-empty
- Check all `sop.requirements` are installed (importlib check)
- On failure: DiagnosticTicket with exact missing item, stamp state=FAILED, archive, halt

#### STEP 5 — EXECUTION (with circuit breaker) [ENHANCED]

- Set `state=RUNNING`, `started_at=now`
- Run matched muscle as subprocess with inputs + parameters as args
- **[NEW] Timeout enforcement:** `subprocess.run(timeout=sop.timeout_seconds)` — hard kill on timeout
- **[NEW] Retry logic:** On non-zero exit:
  - If `retry_count < max_retries` AND error is transient (timeout, OSError, PermissionError):
    - Increment retry_count
    - Wait `2^retry_count` seconds (exponential backoff, cap at 60s)
    - Re-execute from this step
  - If retries exhausted or error is permanent: capture full traceback into DiagnosticTicket, stamp FAILED
- Capture stdout, stderr, returncode
- Write stdout to `task_folder\output.log`
- Record `exit_code` and `duration_seconds` in status

#### STEP 6 — QA GATE (with compound checks) [ENHANCED]

- If `qa_gate.rule == "MULTI"`: run each check in `qa_gate.checks[]` array, ALL must pass
- If `qa_gate.rule` is single: run as before (backwards compatible)
- Check types:
  - `FILE_EXISTS`: target must exist
  - `SIZE_GT_ZERO`: target file size > `min_size_bytes`
  - `CONTAINS_STRING`: target file must contain `expected_string`
- PASS: `qa_result=PASS`, `state=COMPLETE`, `completed_at=now`
- FAIL: `qa_result=FAIL`, write DiagnosticTicket with which specific check failed

#### STEP 7 — CHAIN

- If `chain_next` is set: copy output into new WorkOrder, drop in hub/ for next job
- **[NEW]** Chain inherits `project` and `priority` from parent unless overridden

#### STEP 8 — ARCHIVE

- Move task folder contents to `audit\YYYY-MM-DD\task_{job_id}\`
- Log final outcome with duration

#### STEP 9 — HEARTBEAT

- Write `hub\.heartbeat` with timestamp + last job status every 60s so n8n can health-check with zero logic
- **[NEW]** Also write `hub\.foreman_pid` with process PID for supervisor

#### STEP 10 — DEAD LETTER CHECK [NEW]

- On FATAL severity diagnostics (3 retries exhausted):
  - Move original WorkOrder to `hub\dead_letter\`
  - DiagnosticTicket includes `"suggested_action": "Manual review required"`
  - This prevents infinite retry loops

---

## PHASE 6: THE BLIND POSTMAN (n8n Workflow)

### APEX Blind Postman (APEX-MB-WF-00001)

Generate complete n8n workflow JSON export.

#### NODE 1 — Watch Folder Trigger (PRIMARY)

- Watch `C:\Users\bermi\Projects\apex\hub\` for new `.json` files
- Trigger on file creation only
- **[NEW] Exclude:** `.heartbeat`, `.foreman_pid`, `.tmp` directory

#### NODE 1B — Polling Fallback [NEW]

- Schedule trigger: every 30 seconds
- List all `.json` files in hub/
- Compare against `hub\.last_polled` timestamp file
- Process any files newer than last poll
- Update `.last_polled` after processing
- **Rationale:** Windows file system watchers (ReadDirectoryChangesW) are unreliable after sleep/wake, network reconnects, and high-frequency writes. This catches anything the FSW misses. The idempotency check in foreman.py prevents double-processing.

#### NODE 2 — Read File

- Read file contents, parse JSON
- **[NEW] Validation:** Check that JSON has `meta.receiver` field. If missing or malformed, log to relay.log as "MALFORMED_TICKET", do not route.

#### NODE 3 — Route by receiver (`meta.receiver` field ONLY)

| Receiver | Route to |
|----------|----------|
| `foreman` | Node 4 |
| `originator` | Node 5 |
| `claudeclaw` | Node 6 |
| default | Log "unknown receiver: {value}", halt |

#### NODE 4 — Execute Foreman

```
python C:\Users\bermi\Projects\apex\foreman.py --ticket "{{file_path}}"
```
- `shell: true` (Windows requirement)
- Timeout: 600 seconds (foreman has its own internal timeout per task)

#### NODE 5 — Notify Originator (DiagnosticTicket handler)

- Append to `C:\Users\bermi\Projects\apex\logs\relay.log`
- **[NEW] Severity-based routing:**
  - `FATAL` or `ERROR`: Send Telegram message to Michael's chat ID via bot token
  - `WARN`: Log only, no Telegram notification
  - `INFO`: Log only

#### NODE 6 — Notify ClaudeClaw

- HTTP POST to `localhost:3000/internal/ticket` with ticket JSON body
- **[NEW] Retry:** 3 attempts with 5s delay (ClaudeClaw may be restarting)
- **[NEW] Fallback:** If ClaudeClaw is unreachable after retries, fall back to direct Telegram notification (Node 5 path)

#### NODE 7 — Relay Log

- Append to `relay.log`: timestamp, job_id, receiver, action, severity

**CONSTRAINT:** n8n is a ZERO-KNOWLEDGE relay. It reads `meta.receiver` and `meta.severity` (for notification routing) only. It never transforms, interprets, or acts on any other data in the ticket.

---

## PHASE 7: CLAUDECLAW — TELEGRAM BRIDGE

### Architecture

```
Telegram message
  |
  v
Grammy bot (auth: ALLOWED_CHAT_ID check — FIRST middleware, before anything else)
  |
  v
Rate limiter [NEW] (max 30 messages/minute per chat_id)
  |
  v
Media handler (voice -> Groq STT, photos/docs, video -> Gemini)
  |
  v
Memory context builder (FTS5 search top 3 + 5 most recent -> prepend to prompt)
  |
  v
Agent pool [NEW] (warm Claude Code process, reuse sessions, reduce cold start)
  |
  v
Response formatter (Markdown -> Telegram HTML, split at 4096 chars)
  |
  v
Telegram reply
```

**Separate Express server on port 3000:**
```
POST /internal/ticket  -> Accept DiagnosticTicket from n8n, format, send to Telegram
GET  /health           -> [NEW] JSON health dashboard (uptime, memory count, session count, last message time)
```

### package.json Dependencies

```json
{
  "dependencies": {
    "better-sqlite3": "^9.4.3",
    "grammy": "^1.21.1",
    "cron-parser": "^4.9.0",
    "pino": "^8.0.0",
    "pino-pretty": "^10.0.0",
    "whatsapp-web.js": "^1.23.0",
    "qrcode-terminal": "^0.12.0",
    "express": "^4.18.0"
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/better-sqlite3": "^7.6.0",
    "@types/express": "^4.17.0",
    "tsx": "^4.7.0"
  },
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx watch src/index.ts",
    "setup": "tsx src/scripts/setup.ts",
    "status": "tsx src/scripts/status.ts",
    "cleanup": "tsx src/scripts/cleanup-sessions.ts"
  }
}
```

### SQLite Schema (db.ts)

```sql
-- 1. Sessions
CREATE TABLE IF NOT EXISTS sessions (
    chat_id TEXT PRIMARY KEY,
    session_id TEXT,
    process_pid INTEGER,          -- [NEW] track live process
    updated_at TEXT DEFAULT (datetime('now')),
    created_at TEXT DEFAULT (datetime('now'))
);

-- 2. Memories (dual-sector)
CREATE TABLE IF NOT EXISTS memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    topic_key TEXT,
    content TEXT NOT NULL,
    sector TEXT CHECK(sector IN ('semantic', 'episodic')) DEFAULT 'episodic',
    salience REAL DEFAULT 1.0,
    created_at TEXT DEFAULT (datetime('now')),
    accessed_at TEXT DEFAULT (datetime('now'))
);

-- 3. FTS5 virtual table over memories
CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
    content,
    content=memories,
    content_rowid=id
);

-- Triggers for FTS sync
CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
    INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
END;
CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content) VALUES ('delete', old.id, old.content);
END;
CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
    INSERT INTO memories_fts(memories_fts, rowid, content) VALUES ('delete', old.id, old.content);
    INSERT INTO memories_fts(rowid, content) VALUES (new.id, new.content);
END;

-- 4. Scheduled tasks
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    prompt TEXT NOT NULL,
    schedule TEXT NOT NULL,        -- cron expression
    next_run TEXT,
    last_run TEXT,
    status TEXT CHECK(status IN ('active', 'paused')) DEFAULT 'active'
);

-- 5. WhatsApp outbox
CREATE TABLE IF NOT EXISTS wa_outbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT CHECK(status IN ('pending', 'sent', 'failed')) DEFAULT 'pending',
    created_at TEXT DEFAULT (datetime('now'))
);

-- 6. WhatsApp messages
CREATE TABLE IF NOT EXISTS wa_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wa_chat_id TEXT,
    from_me INTEGER DEFAULT 0,
    body TEXT,
    timestamp INTEGER,
    notified INTEGER DEFAULT 0
);

-- 7. Apex notifications
CREATE TABLE IF NOT EXISTS apex_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT,
    ref_code TEXT,
    severity TEXT,                -- [NEW]
    message TEXT,
    sent_at TEXT DEFAULT (datetime('now')),
    read INTEGER DEFAULT 0       -- [CHANGED] boolean instead of text
);

-- 8. [NEW] Message log for rate limiting and analytics
CREATE TABLE IF NOT EXISTS message_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    direction TEXT CHECK(direction IN ('in', 'out')),
    message_length INTEGER,
    processing_ms INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);
```

### Memory Salience Rules

| Rule | Value |
|------|-------|
| Starting salience | 1.0 |
| On access | +0.1 (cap 5.0) |
| Daily decay (episodic) | -5% per day |
| Daily decay (semantic) | -1% per day |
| Auto-delete threshold | Below 0.1 |
| Semantic triggers | "my", "I am", "prefer", "always", "never", "I like", "I hate", "remember that" |
| Manual pin (checkpoint cmd) | Set salience to 5.0, sector to semantic |

**[NEW] Decay runs as a scheduled task:** Every 6 hours, not on every query. Prevents write amplification.

### agent.ts — Claude Code Process Management

```typescript
// SUBSCRIPTION-FIRST RULE:
// All Claude interactions use the Claude Code CLI which bills to the Desktop subscription.
// NEVER import @anthropic-ai/sdk or make direct API calls.
// If the CLI binary is missing or broken, surface the error to Michael via Telegram.
// Do NOT silently fall back to API billing.
//
// Spawn strategy:
// 1. Try `claude.cmd` first (Windows npm global)
// 2. Fall back to `claude` (direct binary)
// 3. Always use shell: true
// 4. Pass --resume {sessionId} when session exists in SQLite
// 5. Pass --output-format json --dangerously-skip-permissions
// 6. Capture session_id from response, persist in sessions table
// 7. On spawn failure, wait 2s and retry once before giving up
// 8. On second failure: send Telegram message "Claude Code CLI unavailable — check installation"
//    Do NOT fall back to API. Wait for Michael to fix it.
```

### agent-pool.ts — Warm Process Pool [NEW]

```typescript
// Problem: Each `claude -p` invocation takes 2-5 seconds cold start.
// Solution: Keep one warm Claude Code process per active chat_id.
//
// IMPORTANT: These are CLI subprocess pools, NOT API clients.
// Each warm process is a `claude -p` subprocess using the Desktop subscription.
// No Anthropic API keys are involved.
//
// Pool rules:
// - Max 3 concurrent warm processes (memory constraint)
// - LRU eviction: kill oldest unused process when pool full
// - Session persistence: warm process uses --resume from SQLite
// - Health check: ping process every 30s, respawn if dead
// - Cleanup: kill all warm processes on graceful shutdown
// - Timeout: kill process if no activity for 10 minutes
```

### Bot Commands

| Command | Action |
|---------|--------|
| `/start` | Greeting with Michael's name |
| `/chatid` | Echo chat ID |
| `/newchat` | Clear session, kill warm process |
| `/memory` | Recent memories summary |
| `/forget` | Alias for /newchat |
| `/schedule list\|create\|delete\|pause\|resume` | Manage scheduled tasks |
| `/wa` | WhatsApp list or send |
| `/status` | Uptime, memory count, task count, pool status |
| `/apex` | Recent Work Orders and status from `apex\audit\` |
| `/ticket` | Drop a new Work Order ticket manually into `apex\hub\` |
| `/health` | [NEW] Full system health: Apex heartbeat, n8n status, memory stats |

### Media Handlers

| Input | Handler | Output |
|-------|---------|--------|
| Voice message | Groq Whisper STT | `[Voice transcribed]: {text}` prepended to handleMessage |
| Photo / document | Download to `workspace\uploads\` | buildPhotoMessage -> handleMessage |
| Video | Download + Gemini video analysis | Analysis text -> handleMessage |

### Boot Sequence (index.ts)

```
1. Load .env
2. Validate required env vars (fail fast with clear error)
3. Initialize SQLite (run migrations)
4. Run memory decay (if last run > 6 hours ago)
5. Start Express server on port 3000 (/internal/ticket + /health)
6. Start Grammy bot
7. [NEW] Start session cleanup cron (every hour: kill processes with no activity > 1hr)
8. Start scheduler cron
9. [NEW] Attempt WhatsApp bridge — on failure: log warning, continue without it
10. Log "ClaudeClaw online" with uptime marker
```

**Critical: WhatsApp failure at step 9 must NOT prevent steps 1-8 from completing.** WhatsApp bridge is a nice-to-have. Everything else is core.

---

## PHASE 7A: CLAUDE.md — PERSONALITY CONTRACT

Location: `C:\Users\bermi\Projects\claudeclaw\CLAUDE.md`

```markdown
# MichaelBot

You are Michael Bermingham's personal AI assistant. You run on his Windows machine in Dublin. You are accessible via Telegram. You run as a persistent background service.

## Personality (never break these)

- No em dashes. Ever.
- No AI cliches. No "Certainly!", "Great question!", "I'd be happy to", "As an AI"
- No sycophancy
- Don't narrate what you're about to do. Just do it.
- If you don't know, say so plainly.
- Step-by-step for multi-step tasks. Michael has ADHD.
- Complete solutions only. No "you could try..." without the actual implementation.

## Special Commands

- **convolife** — calculate context window % used from session JSONL
- **checkpoint** — save session summary to SQLite as semantic memory salience 5.0

## Windows Gotchas (handle proactively)

1. shell:true in all spawn() calls
2. path.join() everywhere, no hardcoded slashes
3. fileURLToPath(import.meta.url) for __dirname
4. claude may need to be claude.cmd — try both, fall back gracefully
5. WhatsApp Puppeteer: add --no-sandbox --disable-setuid-sandbox
6. better-sqlite3 may need npm rebuild on Windows
```

## PHASE 7B: CAPABILITIES.md — WHAT CLAUDE CAN DO [NEW]

Location: `C:\Users\bermi\Projects\claudeclaw\CAPABILITIES.md`

```markdown
# Capabilities Manifest

Loaded into context on every Claude Code invocation. Update this file when capabilities change.

## File System Access

- Full read/write to C:\Users\bermi\Projects\
- Apex factory: C:\Users\bermi\Projects\apex\
- Read Work Order status: apex\audit\
- Drop tickets: apex\hub\
- Check manifest: apex\registry\manifest.json
- Document register: apex\docs\DOCUMENT_REGISTER.md

## Environment

- Machine: Windows 11, C:\Users\bermi\
- GitHub: github.com/bermingham85/code-artifacts (source of truth)
- n8n: 192.168.50.246:5678
- Claude Code: v2.1.15

## MCP Servers

- filesystem: localhost:9001
- postgres: localhost:9002
- memory: localhost:9003
- github: localhost:9004
- n8n: localhost:9005

## APIs Available

- Groq (Whisper STT + LLM)
- Gemini x4 (video analysis, multimodal)
- Flux / Fal (image generation)
- ElevenLabs (TTS, not active yet)

## Active Projects

- APEX: Automation factory
- CLAW: This bot
- BERM: Bermech Airbnb (23 Hampton Wood Green)
- JESS: Jesse Music / Novel Factory
- TALE: Taleweaver book automation
- BALP: The Balding Pig satirical content
```

**Rationale for split:** CLAUDE.md is the personality contract that rarely changes. CAPABILITIES.md is the capability manifest that changes whenever you add a new MCP server, API, or project. Updating capabilities doesn't risk accidentally changing personality rules.

---

## PHASE 8: REGISTRY STARTER MUSCLES

Create in `C:\Users\bermi\Projects\apex\registry\` — register each with doc_controller.py first.

### muscle_file_copy.py (APEX-MB-PY-00003)

- Copies file from source to destination
- Args: `--source PATH --dest PATH`
- Validates source exists before copy
- Creates destination directory if missing

### muscle_text_transform.py (APEX-MB-PY-00004)

- Text transformations: upper, lower, strip, replace, word_count
- Args: `--input PATH --output PATH --operation upper|lower|strip|replace --find STR --replace STR`
- Reads from file, writes result to file

### muscle_json_merge.py (APEX-MB-PY-00005)

- Merges two or more JSON files (deep merge)
- Args: `--inputs PATH,PATH,... --output PATH`
- Handles key conflicts: last file wins

### muscle_health_check.py (APEX-MB-PY-00006)

- Reports: disk space, Python version, pip package count, skill count from manifest, last index time, foreman heartbeat age, n8n reachability
- Args: `--output PATH` (defaults to `audit\health\health_report.json`)
- Output is structured JSON

### muscle_drop_ticket.py (APEX-MB-PY-00007)

- Creates and drops a new WorkOrder into hub/ from CLI args
- Args: `--action MUSCLE_NAME --project PROJECT --inputs PATH,PATH --qa-rule FILE_EXISTS --qa-target PATH`
- Generates UUID, timestamps, writes atomically to hub/

### Every Muscle Must:

1. Accept args via argparse
2. Call `doc_controller.check_duplicate()` before writing any output file
3. Print clear stdout on success (structured: `{"status": "OK", "output": "path"}`)
4. Exit code 1 + print JSON traceback on failure
5. Have docstring: purpose, inputs, outputs, ref_code, author
6. **[NEW]** Be importable as a Python module (not just CLI) — foreman can import and call directly as optimization

---

## PHASE 9: SUPERVISOR [NEW]

### supervisor.py (APEX-MB-PY-00008)

Location: `C:\Users\bermi\Projects\apex\supervisor\supervisor.py`

**Role:** Watchdog process that monitors both Apex and ClaudeClaw health.

**Checks (every 60 seconds):**

| Check | Healthy | Action on Failure |
|-------|---------|-------------------|
| Foreman heartbeat | `.heartbeat` file < 120s old | Log warning, write DiagnosticTicket |
| ClaudeClaw health | GET `localhost:3000/health` returns 200 | Attempt restart via `npm start` in claudeclaw dir |
| Hub dead letter count | `hub\dead_letter\` has < 10 files | Telegram alert to Michael |
| Disk space | C: drive > 5GB free | Telegram alert |
| n8n reachability | HTTP GET to 192.168.50.246:5678 | Log warning |

**Auto-start:** Registered as Windows Scheduled Task via `install-windows-startup.bat`

**Logs to:** `C:\Users\bermi\Projects\apex\logs\supervisor.log`

---

## PHASE 10: DEMO WORK ORDER

### WO-DEMO-001.json (APEX-MB-WF-00002)

Location: `C:\Users\bermi\Projects\apex\hub\WO-DEMO-001.json`

```json
{
  "meta": {
    "job_id": "WO-DEMO-001",
    "ref_code": "APEX-MB-WF-00002",
    "created_at": "2026-02-27T12:00:00Z",
    "sender": "human_originator",
    "receiver": "foreman",
    "project": "apex_factory_test",
    "chain_next": null,
    "idempotency_key": "demo-001-initial",
    "retry_count": 0,
    "max_retries": 3,
    "priority": "NORMAL"
  },
  "sop": {
    "action": "muscle_health_check",
    "inputs": [],
    "parameters": {},
    "requirements": [],
    "timeout_seconds": 60
  },
  "task_folder": "C:\\Users\\bermi\\Projects\\apex\\active_projects\\tasks\\task_WO-DEMO-001\\",
  "qa_gate": {
    "rule": "FILE_EXISTS",
    "checks": [
      {
        "rule": "FILE_EXISTS",
        "target": "C:\\Users\\bermi\\Projects\\apex\\audit\\health\\health_report.json",
        "min_size_bytes": 10,
        "expected_string": null
      }
    ]
  },
  "status": {
    "state": "PENDING",
    "started_at": null,
    "completed_at": null,
    "duration_seconds": null,
    "diagnostic": null,
    "traceback": null,
    "qa_result": null,
    "exit_code": null
  }
}
```

---

## INITIALIZATION SEQUENCE

Execute in this exact order:

```
1. Create all directories (apex + claudeclaw)
2. python doc_controller.py --init
3. Register all scripts created in this build via doc_controller
4. python indexer.py --scan
5. python foreman.py --ticket "C:\Users\bermi\Projects\apex\hub\WO-DEMO-001.json"
6. cd claudeclaw && npm install && npm run build
7. Import Blind Postman workflow JSON into n8n
8. python supervisor\supervisor.py --check (single health check run)
9. Print summary table
```

### Expected Summary Table

| Component | Status | Notes |
|-----------|--------|-------|
| Apex directory structure | check/cross | |
| Document register (DOCUMENT_REGISTER.md) | check/cross | |
| doc_controller.py | check/cross | Ref: APEX-MB-PY-00000 |
| indexer.py | check/cross | Ref: APEX-MB-PY-00001 |
| foreman.py | check/cross | Ref: APEX-MB-PY-00002 |
| supervisor.py | check/cross | Ref: APEX-MB-PY-00008 |
| manifest.json (skill count) | check/cross | N skills indexed |
| Starter muscles (5) | check/cross | Refs: 00003-00007 |
| n8n workflow JSON | check/cross | Ref: APEX-MB-WF-00001 |
| ClaudeClaw TypeScript build | check/cross | |
| Demo Work Order result | PASS/FAIL | |
| Health report | path | |

**When all pass:**

```
APEX FACTORY FLOOR IS LIVE.
CLAUDECLAW BRIDGE IS READY.
SUPERVISOR WATCHDOG IS ACTIVE.
MESSAGE YOUR BOT ON TELEGRAM TO BEGIN.
```

---

## DESIGN PRINCIPLES (NON-NEGOTIABLE)

1. **Local first.** No cloud AI calls inside any Muscle or Foreman logic.
2. **Reuse > Research > Create.** Doc control check + manifest check mandatory before anything new is created.
3. **No duplicates.** doc_controller.check_duplicate() blocks repeat builds.
4. **Zero-knowledge relay.** n8n reads meta.receiver (and severity for notification routing) only. Never transforms data.
5. **Traceable.** Every job has a task folder. Every document has a ref code. Every change has an audit entry.
6. **Rigid QA.** Every Work Order stamped PASS or FAIL. No ambiguity. Compound checks supported.
7. **Self-diagnosing.** Every failure produces a DiagnosticTicket routed back to Michael's Telegram.
8. **Deterministic.** Same input = same output. Idempotency enforced.
9. **Phone-first.** Everything Michael needs is reachable from Telegram.
10. **One system.** Improving Claude Code improves the factory. Improving the factory improves the phone experience.
11. **[NEW] Graceful degradation.** Optional components (WhatsApp, warm pool) fail without taking down core.
12. **[NEW] Self-healing.** Supervisor restarts failed components. Retry logic handles transient errors. Dead letter queue catches persistent failures.
13. **[NEW] Observable.** Health endpoints, structured logs, heartbeats, and a Telegram-accessible /health dashboard.
14. **[NEW] Subscription-first.** All Claude interactions go through the Claude Code CLI (`claude -p` subprocess) which uses the Claude Desktop subscription. Direct Anthropic API calls (`@anthropic-ai/sdk`) are prohibited unless the CLI is unavailable AND Michael explicitly approves the fallback. No `ANTHROPIC_API_KEY` in any `.env` file by default.

---

## APPENDIX A: FULL REFERENCE CODE REGISTRY (THIS BUILD)

| Ref Code | Name | Type |
|----------|------|------|
| APEX-MB-DOC-00001 | This specification | Documentation |
| APEX-MB-PY-00000 | doc_controller.py | Python script |
| APEX-MB-PY-00001 | indexer.py | Python script |
| APEX-MB-PY-00002 | foreman.py | Python script |
| APEX-MB-PY-00003 | muscle_file_copy.py | Python muscle |
| APEX-MB-PY-00004 | muscle_text_transform.py | Python muscle |
| APEX-MB-PY-00005 | muscle_json_merge.py | Python muscle |
| APEX-MB-PY-00006 | muscle_health_check.py | Python muscle |
| APEX-MB-PY-00007 | muscle_drop_ticket.py | Python muscle |
| APEX-MB-PY-00008 | supervisor.py | Python script |
| APEX-MB-WF-00001 | Blind Postman (n8n) | Workflow |
| APEX-MB-WF-00002 | Demo Work Order | Work Order |
| APEX-MB-SCH-00001 | WorkOrder.json template | Schema |
| APEX-MB-SCH-00002 | DiagnosticTicket.json template | Schema |
| APEX-MB-CFG-00001 | sources.json | Configuration |
| CLAW-MB-TS-00001 | ClaudeClaw bot (all src/) | TypeScript |
| CLAW-MB-DOC-00001 | CLAUDE.md | Documentation |
| CLAW-MB-DOC-00002 | CAPABILITIES.md | Documentation |

---

## APPENDIX B: .env TEMPLATE (claudeclaw)

```env
# Telegram
TELEGRAM_BOT_TOKEN=
ALLOWED_CHAT_IDS=

# Claude — uses Desktop subscription via CLI, no API key needed
# ANTHROPIC_API_KEY is intentionally absent. Do not add one.
CLAUDE_PATH=claude.cmd

# Groq (STT)
GROQ_API_KEY=

# Gemini (video analysis)
GEMINI_API_KEY=

# Apex
APEX_HUB_PATH=C:\Users\bermi\Projects\apex\hub
APEX_AUDIT_PATH=C:\Users\bermi\Projects\apex\audit
APEX_MANIFEST_PATH=C:\Users\bermi\Projects\apex\registry\manifest.json

# Express
TICKET_SERVER_PORT=3000

# WhatsApp (optional)
WA_ENABLED=false
```

---

## APPENDIX C: BUILD ORDER FOR CLAUDE CODE SESSION

When loading this spec into a Claude Code session, execute phases in this order:

```
Phase 0  → Scan existing code, build decision matrix (10 min)
Phase 1  → Create directories (5 min)
Phase 2  → doc_controller.py + init (15 min)
Phase 3  → Templates (5 min)
Phase 4  → indexer.py (20 min)
Phase 5  → foreman.py (30 min)
Phase 8  → Starter muscles (15 min)
Phase 9  → supervisor.py (10 min)
Phase 10 → Demo Work Order (5 min)
--- VERIFY DEMO PASSES ---
Phase 6  → n8n workflow JSON (15 min)
Phase 7  → ClaudeClaw full build (45 min)
--- VERIFY BOT RESPONDS ON TELEGRAM ---
```

**Total estimated build time: ~3 hours across 2 sessions**

Session 1: Phases 0-5, 8-10 (factory floor, ~1.5 hrs)
Session 2: Phases 6-7 (n8n workflow + ClaudeClaw, ~1.5 hrs)