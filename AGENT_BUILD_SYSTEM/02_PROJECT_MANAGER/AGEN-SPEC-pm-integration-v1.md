# Project Manager Agent — Integration Specification

**Document ID:** AGEN-SPEC-pm-integration-v1
**Date:** 2026-02-22

---

## Endpoint

**URL:** `POST http://192.168.50.246:5678/webhook/project-manager`
**Content-Type:** `application/json`
**n8n Workflow ID:** `fbsjuiji61RErVfJ`

---

## Actions

### get_status
Retrieves current state of one or all projects with task counts, blockers, and next actions.
```json
{ "action": "get_status", "project_id": "optional-uuid" }
```

### start_session
Creates a new session and loads context.
```json
{ "action": "start_session", "project_id": "optional-uuid", "agent_name": "required-string" }
```

### end_session
Marks a session complete with summary and next steps.
```json
{ "action": "end_session", "session_id": "required-uuid", "summary": "text", "next_steps": ["array"] }
```

### update_task
Updates a task's status. Auto-unblocks dependent tasks when completing.
```json
{ "action": "update_task", "task_id": "required-uuid", "status": "required", "notes": "optional" }
```

### create_task
Creates a new task. If depends_on is provided, task starts as blocked.
```json
{ "action": "create_task", "project_id": "required-uuid", "title": "required", "description": "opt", "priority": "opt", "assigned_agent": "opt", "depends_on": ["opt-uuids"] }
```

---

## Prerequisites

1. Postgres credential in n8n pointing to: db.ylcepmvbjjnwmzvevxid.supabase.co:5432/postgres
2. Workflow activated after credential setup
