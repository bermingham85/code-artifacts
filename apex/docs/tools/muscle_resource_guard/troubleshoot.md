# TROUBLESHOOT - muscle_resource_guard

| Field | Value |
|---|---|
| Ref Code | APEX-MB-CFG-00004 |
| Tool | muscle_resource_guard |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Script runs | `powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName smoke -MinDiskFreeGB 1 -MinMemoryFreeGB 0.1` | JSON `OK` or intentional `BLOCKED` |
| Lock directory writable | Check `.\store\locks` or passed `-LockDir` | Directory exists/writable |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| `BLOCKED` by lock | Backup/deploy/destructive/GPU lock exists | Wait, queue job, or inspect stale lock age before removal | Re-run after lock clears |
| Disk block | Free system-drive space below threshold | Free disk or lower threshold only if safe | Re-run returns OK |
| Memory block | Free memory below threshold | Stop non-critical jobs or reschedule | Re-run returns OK |
| GPU never releases | Job crashed before `-Release` | Confirm process is dead, then remove stale lock after TTL policy | GPU job can acquire lock |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added lock, disk, memory, and GPU recovery checks | Docs registered in tool menu |
