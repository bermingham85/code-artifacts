# TROUBLESHOOT - muscle_health_check

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00007 |
| Tool | muscle_health_check |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Script runs | `python registry/muscle_health_check.py` | JSON stdout |
| Report exists | Check reported output path | File exists |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| `overall` is `WARN` | Low disk or old heartbeat | Review report fields; clear disk or restart/check foreman | Re-run health check |
| `overall` is `ERROR` | Critical disk or n8n unreachable | Check disk, network, and n8n service | Health report returns OK/WARN |
| Manifest missing | Registry not indexed | Run indexer or restore `registry/manifest.json` | Manifest fields populated |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added health-report interpretation fixes | Docs registered in tool menu |
