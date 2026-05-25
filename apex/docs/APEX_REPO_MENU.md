# Apex Repository Menu

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00025 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Low-token repository selection and state menu |
| Generated | 2026-05-25T13:36:00Z |

## How To Use

1. Pick the repo by purpose/state.
2. Open only its `recommended_entry` first.
3. If the repo is dirty, read its status preview before changing files.
4. Add or update low-token context files for repos that lack them.

## Repository Selection

| Repo | Class | Git | Dirty | Entry | Next action |
|---|---|---|---:|---|---|
| `code-artifacts` | DOCUMENTED_REPO | `apex/estate-seed-00004` | 29 | `README.md` | Consider adding low-token AGENTS.md or llms.txt. |
| `code-artifacts\AGENT_BUILD_SYSTEM` | DOCUMENTED_REPO | `apex/estate-seed-00004` | 0 | `README.md` | Consider adding low-token AGENTS.md or llms.txt. |
| `code-artifacts\apex` | APEX_GOVERNED | `apex/estate-seed-00004` | 29 | `docs/APEX_CONTEXT_INDEX.md` | Use Apex context/menu files before deeper reads. |
| `code-artifacts\jesse-project` | DOCUMENTED_REPO | `apex/estate-seed-00004` | 0 | `README.md` | Consider adding low-token AGENTS.md or llms.txt. |

## Dirty Repo Details

| Repo | Status preview |
|---|---|
| `code-artifacts` | M  apex/AGENTS.md<br>M  apex/CLAUDE.md<br> M apex/audit/doc_audit.jsonl<br>M  apex/docs/APEX_CONTEXT_INDEX.md<br>A  apex/docs/APEX_REPO_MENU.json<br>A  apex/docs/APEX_REPO_MENU.md<br>M  apex/docs/DOCUMENT_REGISTER.md<br> M apex/docs/doc_controller.py<br>M  apex/llms.txt<br>A  apex/registry/generate_repo_menu.py<br>?? apex/.claude/<br>?? apex/audit/claude_codex_loop/ |
| `code-artifacts\apex` | M  AGENTS.md<br>M  CLAUDE.md<br> M audit/doc_audit.jsonl<br>M  docs/APEX_CONTEXT_INDEX.md<br>A  docs/APEX_REPO_MENU.json<br>A  docs/APEX_REPO_MENU.md<br>M  docs/DOCUMENT_REGISTER.md<br> M docs/doc_controller.py<br>M  llms.txt<br>A  registry/generate_repo_menu.py<br>?? .claude/<br>?? audit/claude_codex_loop/ |

## Source Of Truth

| Need | Source |
|---|---|
| Machine-readable repo menu | `docs/APEX_REPO_MENU.json` |
| Regenerate menu | `python registry/generate_repo_menu.py --root C:\\Users\\Owner\\Repos` |
| Apex workspace artifacts | `docs/APEX_WORKSPACE_MENU.md` |
| Apex tools | `docs/APEX_TOOL_MENU.md` |
