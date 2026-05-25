# TROUBLESHOOT - muscle_drop_ticket

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00008 |
| Tool | muscle_drop_ticket |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Target action approved | Check `registry/TOOL_INDEX.md` | Target tool appears approved |
| Hub exists | `Test-Path hub` | `True` |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| Ticket not picked up | n8n watcher or foreman not running | Run health check; inspect hub and audit folders | Ticket moves to audit or dead letter |
| QA fails | Wrong QA rule or target path | Use a QA target produced by the action | Completion report shows QA pass |
| Duplicate job skipped | Idempotency key or job already processed | Use a new job ID/key for a new run | New ticket accepted |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added ticket lifecycle checks | Docs registered in tool menu |
