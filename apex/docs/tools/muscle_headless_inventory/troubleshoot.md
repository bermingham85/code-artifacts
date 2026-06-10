# TROUBLESHOOT - muscle_headless_inventory

| Field | Value |
|---|---|
| Ref Code | APEX-MB-CFG-00003 |
| Tool | muscle_headless_inventory |
| Version | 1.0 |
| Status | ACTIVE |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Script runs | `powershell -ExecutionPolicy Bypass -File .\registry\muscle_headless_inventory.ps1 -OutputDir .\audit\headless_inventory` | JSON stdout with `status: OK` |
| Output file exists | Check `output_path` from stdout | File exists |
| Tool is approved | Check `registry/TOOL_INDEX.md` | Tool appears in Approved Tools |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| Execution policy blocks script | PowerShell policy restriction | Run with `-ExecutionPolicy Bypass` for this process | Script returns JSON |
| CIM class error | WMI/CIM provider issue | Re-run as normal user first; if a class is unavailable, confirm script returns null instead of failing | Inventory JSON created |
| Output path fails | Directory or drive unavailable | Use a writable absolute output directory | `Test-Path` output directory |
| WOL data missing | BIOS setting not visible from OS | Verify WOL/AC-restore physically or with vendor tooling | Record separate BIOS evidence |

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created | Operational doc gap | Added PowerShell, CIM, output, and BIOS verification checks | Docs registered in tool menu |
