# Apex Tool Menu

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00012 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Low-token tool selection menu with current state, exact use path, and editable troubleshooting links |
| Generated | 2026-05-25T13:17:03Z |

## How To Use This Menu

1. Pick the tool by outcome.
2. If you only need the command, use the `Exact call` column.
3. If you need safe usage detail, open that tool's `guidance.md`.
4. If it fails, open that tool's `troubleshoot.md`.
5. When a new fix is discovered, append it to the tool's `troubleshoot.md` under `Reusable Fix Log`.

Do not load every tool document up front. This menu is the cover page. Load only the selected row's guidance or troubleshoot file.

## Approved Tool Selection

| Need | Tool | State | Exact call | How to | Troubleshoot |
|---|---|---|---|---|---|
| Inventory a headless laptop | `muscle_headless_inventory` | APPROVED | `powershell -ExecutionPolicy Bypass -File .\registry\muscle_headless_inventory.ps1 -OutputDir .\audit\headless_inventory` | `docs/tools/muscle_headless_inventory/guidance.md` | `docs/tools/muscle_headless_inventory/troubleshoot.md` |
| Gate a scheduled or GPU job | `muscle_resource_guard` | APPROVED | `powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName report-batch -MinDiskFreeGB 10 -MinMemoryFreeGB 2` | `docs/tools/muscle_resource_guard/guidance.md` | `docs/tools/muscle_resource_guard/troubleshoot.md` |
| Copy or back up a file | `muscle_file_copy` | APPROVED | `python registry/muscle_file_copy.py --source "C:/path/source.txt" --dest "C:/path/dest.txt"` | `docs/tools/muscle_file_copy/guidance.md` | `docs/tools/muscle_file_copy/troubleshoot.md` |
| Transform or count text | `muscle_text_transform` | APPROVED | `python registry/muscle_text_transform.py --input in.txt --output out.txt --operation upper` | `docs/tools/muscle_text_transform/guidance.md` | `docs/tools/muscle_text_transform/troubleshoot.md` |
| Merge JSON files | `muscle_json_merge` | APPROVED | `python registry/muscle_json_merge.py --inputs "base.json,override.json" --output "merged.json"` | `docs/tools/muscle_json_merge/guidance.md` | `docs/tools/muscle_json_merge/troubleshoot.md` |
| Check Apex health | `muscle_health_check` | APPROVED | `python registry/muscle_health_check.py` | `docs/tools/muscle_health_check/guidance.md` | `docs/tools/muscle_health_check/troubleshoot.md` |
| Drop a WorkOrder into the pipeline | `muscle_drop_ticket` | APPROVED | `python registry/muscle_drop_ticket.py --action muscle_health_check --project APEX` | `docs/tools/muscle_drop_ticket/guidance.md` | `docs/tools/muscle_drop_ticket/troubleshoot.md` |
| Build a Replit Agent packet | `muscle_replit_builder_packet` | APPROVED | `python registry/muscle_replit_builder_packet.py --instruction-file docs/spec/my_claude_build.md --mode create --project APEX` | `docs/tools/muscle_replit_builder_packet/guidance.md` | `docs/tools/muscle_replit_builder_packet/troubleshoot.md` |

## Pending Tool Queue

These are not production-callable until their blueprint, guidance, test record, troubleshoot page, and approval status are complete.

| Tool | State | Missing |
|---|---|---|
| `muscle_gdrive_download` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |
| `muscle_gdrive_watcher` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |
| `muscle_ocr_batch_retrieve` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |
| `muscle_ocr_batch_submit` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |
| `muscle_ocr_receipt` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |
| `muscle_receipt_dedup_check` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |
| `muscle_receipt_dedup_mark` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |
| `muscle_sheets_append` | PENDING | `blueprint.md, guidance.md, test_record.md, troubleshoot.md` |

## Maintenance Rule

When a tool fails and a reusable fix is found:

1. Add the fix to `docs/tools/<tool>/troubleshoot.md`.
2. Include date, symptom, likely cause, fix, verification command, and any prevention rule.
3. Keep the fix short and operational.
4. Commit the change so future contexts inherit the repair.

## Source Of Truth

| Need | Source |
|---|---|
| Approved callable tools | `registry/TOOL_INDEX.md` |
| Artifact status and paths | `docs/DOCUMENT_REGISTER.md` |
| Tool metadata | `registry/manifest.json` |
| Machine-readable menu source | `docs/APEX_TOOL_MENU.json` |
| Tool approval standard | `docs/NAMING_CONVENTION.md` |
