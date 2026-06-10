# Apex Workspace Menu

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00024 |
| Version | 1.1 |
| Status | ACTIVE |
| Purpose | Low-token index of current workspace artifact groups, including uncommitted work-in-progress files |

## Use This Before Inspecting Loose Files

This menu explains what the current loose/uncommitted artifact groups are for, whether they are ready to use, and what the next action should be. It is intentionally compact so future contexts do not need to open every file just to understand the workspace.

## Artifact Groups

| Group | Current state | What it contains | Use now? | Next action |
|---|---|---|---|---|
| Autonomous delivery/tool menu package | COMMITTED | Root boot files, context index, tool menu, generated JSON menu, validator, support tools, troubleshoot pages, research, certificate | Yes | Use committed branch as authority |
| `.claude/settings.local.json` | LOCAL CONFIG | Local Claude settings for this workstation | No for repo package | Keep uncommitted unless an explicit policy says to share project-local Claude settings |
| `audit/2026-06-02/task_rls-0-postgrest-inventory/` | RLS INVENTORY WIP | One-file PostgREST inventory artifact for the RLS advisory path | Evidence only | Keep for P0 RLS rollout; do not apply RLS from it |
| `audit/claude_codex_loop/AGEN-*` and `SMOKE*` | LOOP EVIDENCE | Claude/Codex loop transcripts for Architecture, migration coordinator, verification, and smoke runs | Evidence only | Commit only when linked by a work order or signoff |
| `audit/codex_review/` | REVIEW EVIDENCE | 14 Codex review/runbook artifacts, including AGEN migration review material | Evidence only | Keep with the relevant AGEN or doctrine package, not with unrelated commits |
| `audit/compliance/` | AUDIT OUTPUT | 17 compliance checker output reports | Evidence only | Keep only if tied to a certificate or cleanup task |
| `audit/receipt_ocr_raw/` | SENSITIVE-RISK OUTPUT | 2 raw receipt OCR export artifacts | No by default | Inspect for private financial data before any staging; prefer archive outside repo if not required |
| `audit/work_gate/` | GATE RECEIPTS | 22 work-gate audit receipts, including current session receipts | Evidence only | Commit only the receipts referenced by a specific work order/certificate |
| `docs/spec/SCOPE-AGEN-AGENT-TASKS-SCHEMA-FIX-v1.md` | SUPERSEDED SPEC | Older broad AGEN task schema scope | No | Do not promote; superseded by `docs/spec/SPEC-AGEN-TASK-LINEAGE-v1.md` and `docs/policy/AGEN_TASK_LINEAGE_DESIGN_v1.md` |
| `hub/WO-APEX-CODEX-UNREACHABLE-002.json` | INCIDENT WO WIP | Codex-unreachable incident packet from 2026-06-02 | Reference only | Commit only with the matching incident/evidence package if still active |
| `registry/receipt_ocr_raw_export.py` | WIP TOOL | Receipt OCR raw export utility | Not approved | Document/approve separately or archive; do not mix with Apex autonomous-delivery commits |
| `mbw_comfyui_stitch_flow/` | SEPARATE PROJECT PACKAGE | ComfyUI MBW workflow/runbook/research/scripts plus generated cache | Separate project | Do not mix with Apex governance commits; remove generated `__pycache__` only with explicit cleanup approval |

## Decision Rules

| Situation | Action |
|---|---|
| Need to use an approved tool | Read `docs/APEX_TOOL_MENU.md` |
| Need to edit repo or promote work | Run `python registry/muscle_work_gate.py --repo . --intent write --fetch` first |
| Need to understand loose files | Read this file first |
| Need to approve a WIP tool | Add blueprint, guidance, test_record, troubleshoot; run `approve_tool.py`; update generated menu |
| Need to commit a group | Commit one group at a time with matching docs/evidence |
| File may contain private data | Inspect before staging; do not commit raw secrets or sensitive receipts |
| Need to work on Supabase | Read `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md`, set the boundary marker, then run `registry/supabase_project_guard.py` |

## Immediate Recommended Batches

| Priority | Batch | Why |
|---:|---|---|
| 1 | `audit/2026-06-02/task_rls-0-postgrest-inventory/` | P0 RLS rollout can use this as read-only evidence, but needs SQL-side confirmation before policy work |
| 2 | `audit/claude_codex_loop/AGEN-*`, `audit/codex_review/`, `hub/WO-APEX-CODEX-UNREACHABLE-002.json` | These likely belong to AGEN/SP-A evidence packages; tie each to a work order before committing |
| 3 | `audit/work_gate/` | Commit only receipts referenced by active work; otherwise leave local evidence unpromoted |
| 4 | `registry/receipt_ocr_raw_export.py` + `audit/receipt_ocr_raw/` | Sensitive-risk receipt workflow; separate review, redaction, and approval required |
| 5 | `mbw_comfyui_stitch_flow/` | Separate project package; handle outside Apex governance commits |
