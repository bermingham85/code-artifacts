# TROUBLESHOOT - muscle_text_transform

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00005 |
| Tool | muscle_text_transform |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Input file exists | `Test-Path in.txt` | `True` |
| Operation is supported | Check guidance | `upper`, `lower`, `strip`, `replace`, or `word_count` |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| Replace does nothing | `--find` string does not exactly match text | Check casing and whitespace; test on a small sample | Inspect output file |
| Output overwrites input unexpectedly | Same input/output path used | Use a separate output path unless overwrite is intended | Compare input backup |
| Encoding error | Non-UTF text input | Convert the file to UTF-8 before running | Re-run and inspect output |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added transform-specific failure checks | Docs registered in tool menu |
