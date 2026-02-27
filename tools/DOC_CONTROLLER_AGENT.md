# Document Controller Agent — Reference Guide

> Read this before committing any code file. All new code files should be logged through the doc controller.

---

## Current State: PARTIAL BUILD

Two pieces exist but are not yet connected into a single pipeline.

### Piece 1 — n8n Workflow (logging stub)
- **Repo:** `bermingham85/bermech-n8n-workflows`
- **File:** `document_control_agent.json`
- **What it does:** Accepts a POST to `/log-entry`, formats the payload, writes a row to `agent_logs` in PostgreSQL.
- **What it does NOT do:** Naming validation, filing location check, duplicate detection, code quality gate.
- **Endpoint:** `POST http://<n8n-host>/webhook/log-entry`
- **Payload:**
  ```json
  {
    "agent": "repo_audit.py",
    "action": "file_created",
    "status": "completed",
    "details": "Committed to code-artifacts/tools/"
  }
  ```
- **DB table:** `agent_logs` (columns: timestamp, agent_name, action, status, details)

### Piece 2 — JS Class (naming + filing logic)
- **Repo:** `bermingham85/mcp-puppet-pipeline`
- **File:** `src/agents/core/doc-organizer.js`
- **What it does:** Enforces naming conventions, determines correct filing location, moves files, updates references.
- **Naming rules it knows:**
  - agents: `{core|specialized}-{name}.js`
  - tools: `{service}-{function}-tool.js`
  - workflows: `{project}-{type}-workflow.json`
  - logs: `{category}_{date}.log`
- **Filing rules it knows:**
  - `agents/core/` — reusable core agents
  - `agents/specialized/` — project-specific
  - `tools/` — integration and utility tools
  - `workflows/` — n8n workflows
- **Status:** Not callable from n8n. Runs only inside the mcp-puppet-pipeline Node.js process.

---

## What Needs to Be Built (Gap)

To have a working doc controller that every session can call:

1. **Wrapper webhook in n8n** that accepts a new file record (name, path, type, description) and:
   - Validates the name against conventions
   - Determines the correct repo/path
   - Logs the registration to `agent_logs`
   - Returns pass/fail + corrected name if needed

2. **OR** a Python function in `code-artifacts/tools/` (simpler, more reliable) that:
   - Takes `(file_path, file_type, description)` as args
   - Checks name against conventions
   - POSTs to the n8n `/log-entry` webhook to register it
   - Can be called at the end of any script that creates files

---

## How to Use Right Now (Interim)

Any time a new code file is created and committed, POST to the n8n log-entry webhook:

```python
import requests, os

def log_to_doc_controller(file_name, action="file_created", details=""):
    n8n_host = os.environ.get("N8N_HOST", "http://localhost:5678")
    requests.post(f"{n8n_host}/webhook/log-entry", json={
        "agent": file_name,
        "action": action,
        "status": "completed",
        "details": details
    }, timeout=5)
```

Add this call to `repo_audit.py` and any other tool script after files are written.

---

## How to Find This Next Session

Search: `github search_code "document_control_agent user:bermingham85"`  
Or go directly to: `bermingham85/bermech-n8n-workflows/document_control_agent.json`  
This reference doc: `bermingham85/code-artifacts/tools/DOC_CONTROLLER_AGENT.md`

---

## Priority Build Order

1. Add the `log_to_doc_controller()` helper to `repo_audit.py` — 10 min
2. Build a proper n8n workflow that does naming validation — 1-2 hrs
3. Wire doc-organizer.js logic into the n8n workflow via a Code node — 2-3 hrs

---

## Decision Log

| Date | Decision |
|---|---|
| 2026-02-27 | Found stub + JS class. Neither connected. Created this reference. |
