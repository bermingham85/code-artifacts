# TROUBLESHOOT - muscle_json_merge

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00006 |
| Tool | muscle_json_merge |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Inputs exist | Check every path in `--inputs` | All exist |
| Inputs parse | `python -m json.tool file.json` | Exit 0 |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| JSON parse error | Invalid JSON or trailing comma | Validate each input with `python -m json.tool` and fix syntax | Re-run merge |
| Value unexpectedly changed | Later file overrides earlier key | Reorder inputs so the intended winner is last | Inspect merged output |
| Output folder missing | Parent path does not exist | Create parent folder or write to existing path | `Test-Path` output parent |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added JSON validation and override-order checks | Docs registered in tool menu |
