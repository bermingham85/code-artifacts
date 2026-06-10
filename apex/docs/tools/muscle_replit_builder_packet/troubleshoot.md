# TROUBLESHOOT - muscle_replit_builder_packet

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00024 |
| Tool | muscle_replit_builder_packet |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Instruction source exists | Check `--instruction-file` or inline instruction | Non-empty instruction |
| Mode is valid | Check command | `create`, `update`, or `inspect` |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| Empty or weak packet | Instruction file is missing detail | Add goal, constraints, expected output, tests, risks, and run steps | Generated packet contains all sections |
| Wrong mode | `--mode` does not match intended Replit action | Use `create` for new app, `update` for existing app, `inspect` for explanation | Packet title and prompt match mode |
| Secrets risk | Prompt contains credentials | Remove secrets; use credential placeholders only | Search generated packet for secret-like values |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added Replit packet quality and secret checks | Docs registered in tool menu |
