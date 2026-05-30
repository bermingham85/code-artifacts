# Apex Repository Menu

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00025 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Low-token repository selection and state menu |
| Generated | 2026-05-30T04:45:21Z |

## How To Use

1. Pick the repo by purpose/state.
2. Open only its `recommended_entry` first.
3. If the repo is dirty, read its status preview before changing files.
4. Add or update low-token context files for repos that lack them.

## Repository Selection

| Repo | Class | Git | Dirty | Entry | Next action |
|---|---|---|---:|---|---|
| `code-artifacts` | DOCUMENTED_REPO | `apex/estate-seed-00004` | 34 | `README.md` | Consider adding low-token AGENTS.md or llms.txt. |
| `code-artifacts\AGENT_BUILD_SYSTEM` | DOCUMENTED_REPO | `apex/estate-seed-00004` | 0 | `README.md` | Consider adding low-token AGENTS.md or llms.txt. |
| `code-artifacts\apex` | APEX_GOVERNED | `apex/estate-seed-00004` | 34 | `docs/APEX_CONTEXT_INDEX.md` | Use Apex context/menu files before deeper reads. |
| `code-artifacts\jesse-project` | DOCUMENTED_REPO | `apex/estate-seed-00004` | 0 | `README.md` | Consider adding low-token AGENTS.md or llms.txt. |

## Dirty Repo Details

| Repo | Status preview |
|---|---|
| `code-artifacts` | M apex/docs/doc_controller.py<br>?? apex/.claude/<br>?? apex/audit/claude_codex_loop/AGEN-architecture-agent-post-migration/<br>?? apex/audit/claude_codex_loop/AGEN-architecture-agent-v2/<br>?? apex/audit/claude_codex_loop/AGEN-architecture-agent/<br>?? apex/audit/claude_codex_loop/AGEN-migration-coordinator/<br>?? apex/audit/claude_codex_loop/AGEN-verification-agent/<br>?? apex/audit/claude_codex_loop/SMOKE-001/attempt_01_claude_builder.txt<br>?? apex/audit/codex_review/<br>?? apex/audit/compliance/2026-05-04T15-37-48Z.json<br>?? apex/audit/compliance/2026-05-04T15-38-30Z.json<br>?? apex/audit/compliance/2026-05-04T15-39-00Z.json |
| `code-artifacts\apex` | M docs/doc_controller.py<br>?? .claude/<br>?? audit/claude_codex_loop/AGEN-architecture-agent-post-migration/<br>?? audit/claude_codex_loop/AGEN-architecture-agent-v2/<br>?? audit/claude_codex_loop/AGEN-architecture-agent/<br>?? audit/claude_codex_loop/AGEN-migration-coordinator/<br>?? audit/claude_codex_loop/AGEN-verification-agent/<br>?? audit/claude_codex_loop/SMOKE-001/attempt_01_claude_builder.txt<br>?? audit/codex_review/<br>?? audit/compliance/2026-05-04T15-37-48Z.json<br>?? audit/compliance/2026-05-04T15-38-30Z.json<br>?? audit/compliance/2026-05-04T15-39-00Z.json |

## Source Of Truth

| Need | Source |
|---|---|
| Machine-readable repo menu | `docs/APEX_REPO_MENU.json` |
| Regenerate menu | `python registry/generate_repo_menu.py --root C:\\Users\\Owner\\Repos` |
| Apex workspace artifacts | `docs/APEX_WORKSPACE_MENU.md` |
| Apex tools | `docs/APEX_TOOL_MENU.md` |
