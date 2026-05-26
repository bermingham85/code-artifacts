# Apex Station Alignment

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00035 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Checklist for closing LLM breakout paths across stations and keeping fallback work gated |

## Authority Rule

All stations and LLMs use the same authority model:

| Area | Authority |
|---|---|
| Committed code | GitHub protected branches and reviewed PRs |
| Local shared artifacts | X-drive canonical/index route |
| New artifacts | X-drive inbox until promoted |
| C-drive/project-local files | Working state only |

## Required Local Shutoffs

| Breakout point | Required state |
|---|---|
| Claude repo-local command allowlist | No broad `git push *`, `git add *`, `git commit *`, or `python *` entries |
| Claude global auto-permission | `skipAutoPermissionPrompt` must be `false` |
| Codex approval policy | Must not be `never` for trusted workstations |
| X Apex path in Codex config | Must not be globally trusted as a normal writable project |
| Skill sync scripts | Must push review branches, not `main` |
| Claude/Codex loop | Must run `muscle_work_gate` before starting Claude |
| X Apex exposure to Claude | Opt-in only with `--allow-x-apex` |

## Station Verification

Run these checks on each station after pulling the latest Apex and skills alignment:

```powershell
python registry/muscle_work_gate.py --repo . --intent write --fetch
python registry/validate_tool_docs.py
```

Then inspect local LLM settings:

```powershell
Select-String -Path .claude/settings.local.json -Pattern "git push|git add|git commit|Bash\\(python \\*\\)"
Select-String -Path $env:USERPROFILE\.claude\settings.json -Pattern '"skipAutoPermissionPrompt": true'
Select-String -Path $env:USERPROFILE\.codex\config.toml -Pattern 'approval_policy = "never"|extra\\automations\\apex'
```

Expected result: no direct-publish allowlists, no global Claude auto-permission, no `approval_policy = "never"`, and no trusted X Apex project entry.

## Remaining External Controls

These cannot be fully enforced by repo files alone:

- GitHub branch protection must block direct pushes to `main`/`master`.
- X-drive canonical folders should be read-only to agents; agents write to inbox only.
- n8n, Task Scheduler, and remote runners must call `muscle_work_gate` before write/promote jobs.
- Any station-local credentials with broad GitHub write scope should be reduced to branch/PR workflow.
