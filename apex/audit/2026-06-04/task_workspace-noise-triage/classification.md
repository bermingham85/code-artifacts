# Workspace Noise Triage

| Field | Value |
|---|---|
| Date | 2026-06-04 |
| Scope | P4 untracked workspace classification |
| Method | Filename/group counts only for sensitive-risk areas; no secret or receipt contents read |
| Live service writes | None |

## Classification Summary

| Group | Classification | Action |
|---|---|---|
| `.claude/settings.local.json` | Local workstation config | Keep uncommitted unless explicitly shared |
| `audit/2026-06-02/task_rls-0-postgrest-inventory/` | P0 RLS advisory evidence | Keep for RLS rollout; no RLS changes from this alone |
| `audit/claude_codex_loop/AGEN-*`, `SMOKE*` | Claude/Codex loop evidence | Commit only when tied to work order/signoff |
| `audit/codex_review/` | Review evidence | Tie to relevant AGEN/doctrine work before commit |
| `audit/compliance/` | Compliance reports | Evidence only |
| `audit/receipt_ocr_raw/` | Sensitive-risk raw OCR outputs | Do not stage without privacy review |
| `audit/work_gate/` | Work-gate receipts | Evidence only; commit selectively |
| `docs/spec/SCOPE-AGEN-AGENT-TASKS-SCHEMA-FIX-v1.md` | Superseded AGEN schema scope | Do not promote |
| `hub/WO-APEX-CODEX-UNREACHABLE-002.json` | Incident work order WIP | Commit only with matching evidence package |
| `registry/receipt_ocr_raw_export.py` | WIP receipt OCR utility | Separate documentation/approval needed |
| `mbw_comfyui_stitch_flow/` | Separate ComfyUI project package | Do not mix with Apex governance commits |

## Evidence

- `git status --short` showed only untracked loose groups after P1 commit.
- File counts gathered without opening sensitive-risk contents:
  - RLS inventory: 1 file.
  - Codex review: 14 files.
  - Compliance reports: 17 files.
  - Receipt OCR raw: 2 files.
  - Work-gate receipts: 22 files.
- Claude/Codex loop evidence groups listed by directory name only.

## Result

Updated `docs/APEX_WORKSPACE_MENU.md` to v1.1 so future contexts can route or avoid loose groups without reading each folder.
