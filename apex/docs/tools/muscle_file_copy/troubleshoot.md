# TROUBLESHOOT - muscle_file_copy

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00004 |
| Tool | muscle_file_copy |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Source exists | `Test-Path "C:\path\source.txt"` | `True` |
| Destination parent is valid | Check drive/root path | Parent drive exists |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| Source not found | Wrong path or escaping | Use quoted absolute paths; prefer forward slashes in CLI calls | Re-run with `Test-Path` on source |
| Access denied | Destination protected or file locked | Choose writable destination or close locking process | Copy a small test file to the same folder |
| Destination unexpected | Relative path resolved from current working directory | Use absolute destination path | Check output JSON path |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added fast checks and common copy failures | Docs registered in tool menu |
