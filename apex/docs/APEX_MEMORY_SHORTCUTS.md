# Apex Memory Shortcuts

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00040 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Reusable route map so future agents stop remapping the same Apex authority, station, repo, and handoff paths |

## Use This When

Read this after `docs/APEX_CONTEXT_INDEX.md` when the next agent is about to ask:

- Which copy is official?
- Which machine or folder should be trusted?
- Which gate must run before edits?
- Which previous station-alignment work already happened?
- Where should a Claude, Codex, Oz, or fallback agent resume?

This file is a shortcut map only. It does not replace the gate, active queue, document register, or source files.

## Shared Source Location

This file is the shared Claude/Codex/Oz shortcut source:

`C:/Users/Owner/Repos/code-artifacts/apex/docs/APEX_MEMORY_SHORTCUTS.md`

Repository path:

`apex/docs/APEX_MEMORY_SHORTCUTS.md`

Claude, Codex, Oz, and delegated agents may add short rows here when they discover a repeatable route that prevents future remapping. Add only stable shortcuts with a source anchor, such as a committed doc, issue, PR, work-gate audit, or approved tool page.

Do not use private chat text as the durable source. If a shortcut came from a chat, turn it into a row here and link the repo/issue/PR/audit evidence that makes it verifiable.

## Fixed Boot Route

| Need | Shortcut route |
|---|---|
| Start any Apex context | `docs/APEX_CONTEXT_INDEX.md`, then this file, then `docs/APEX_ACTIVE_QUEUE.md` |
| Edit a repo | `docs/APEX_WORK_GATE.md`, then `python registry/muscle_work_gate.py --repo . --intent write --fetch` |
| Continue on fallback hardware | `python registry/muscle_work_gate.py --repo . --mode fallback --intent write --fetch` |
| Promote artifacts | `python registry/muscle_work_gate.py --repo . --intent promote --fetch` |
| Choose an approved tool | `docs/APEX_TOOL_MENU.md`, then `registry/TOOL_INDEX.md` for exact call syntax |
| Decide what loose files mean | `docs/APEX_WORKSPACE_MENU.md` before opening audit folders |
| Choose or inspect a repo | `docs/APEX_REPO_MENU.md` |
| Align a station or LLM install | `docs/APEX_STATION_ALIGNMENT.md` |
| Handle shared Supabase work | `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md`, then `docs/policy/SUPABASE_PROJECT_ISOLATION.md` |
| Check current blockers | `docs/APEX_ACTIVE_QUEUE.md` |
| Check document authority | `docs/DOCUMENT_REGISTER.md` |

## Authority Shortcuts

| Area | Treat as official only when |
|---|---|
| Code | It is on a reviewed/accepted GitHub branch or PR route. Local C-drive files are working state. |
| X-drive canonical artifacts | They reached `X:/Apex/Canonical` through the manifest/index promotion route. Agents do not overwrite canonical folders directly. |
| New artifacts | They are in `X:/Apex/Inbox/<station>` until promoted. |
| Fallback-machine work | The fallback gate passed and later promotion/merge makes it official. |
| Chat summaries | They are hints only. Pull/read committed files and issue handoffs before acting. |
| Timestamps | They are evidence, not authority. Do not pick "latest" by modified time alone. |

## Proven Routes From This Work

| Problem seen | Established route |
|---|---|
| LLMs ignore repeated prose instructions | Put the rule in repo boot docs, station alignment, tool gates, and handoff text. Make the gate command the first action before write/promotion. |
| Agents keep searching every C drive for stale copies | Use GitHub branch/PR status plus `muscle_work_gate`; only inspect C-drive copies when the manifest says work was never promoted. |
| X-drive overwrite risk | Keep `X:/Apex/Canonical` out of normal trusted project roots. New files go to `X:/Apex/Inbox/<station>` until promoted. |
| Direct GitHub push risk | Use branch protection where available, repo-local task branches, and PR merge route. Do not allow broad `git push *` in LLM settings. |
| Scheduled sync can move stale state | Disable unsafe scheduled tasks where possible. If task permissions block disable, guard the wrapper so it defaults to no-op unless explicitly enabled. |
| Lost Claude/Codex screen after restart | Resume from the GitHub handoff issue and committed docs, not from terminal scrollback. Start the agent in the Apex repo and repeat the gate rule in the handoff prompt. |
| Cross-station rollout uncertainty | Treat each station as unverified until it has pulled current docs/skills and passed the station alignment checklist. |

## Known Handoff Anchors

| Anchor | Use |
|---|---|
| `docs/APEX_ACTIVE_QUEUE.md` | Current branch state, do-not-reprocess list, next actions, and blockers. |
| `docs/APEX_STATION_ALIGNMENT.md` | Station-level shutoffs for Claude, Codex, X exposure, sync scripts, and task runners. |
| `https://github.com/bermingham85/warp-skills/issues/5` | Oz/team handoff for station alignment and remaining rollout work. |
| `https://github.com/bermingham85/code-artifacts/pull/4` | Apex work-gate/station-alignment PR route that remains the current Apex PR anchor. |
| `https://github.com/bermingham85/warp-machine-setup/pull/1` | Merged guardrail showing Codex sync was made opt-in after task disable was denied. |
| `audit/work_gate/` | Work-gate evidence. Inspect only targeted records, not the whole folder by default. |

## Agent Short Prompts

Use these exact small prompts in handoffs instead of re-explaining the whole history.

| Target | Prompt |
|---|---|
| Claude/Codex Apex continuation | Pull the current Apex branch, read `docs/APEX_CONTEXT_INDEX.md`, `docs/APEX_MEMORY_SHORTCUTS.md`, and `docs/APEX_ACTIVE_QUEUE.md`; run `muscle_work_gate` before edits or promotion; do not treat local C-drive files, chat text, or X canonical folders as writable authority. |
| Fallback laptop work | Run `python registry/muscle_work_gate.py --repo . --mode fallback --intent write --fetch`; work is provisional until promotion or PR merge passes. |
| Station alignment | Pull current Apex and skills, read `docs/APEX_STATION_ALIGNMENT.md`, verify Claude/Codex settings, scheduled jobs, branch protection, and X-drive trust; record blockers in the handoff issue. |
| Supabase work | Read shared-boundary and isolation policies first; do not write to `JESS`; do not enable RLS until SQL-side inventory, policies, rollback, and smoke tests exist. |

## Do Not Re-derive

- The authority model is already documented in `docs/APEX_WORK_GATE.md`.
- The current queue and stale-work exclusions are in `docs/APEX_ACTIVE_QUEUE.md`.
- Station shutoffs are in `docs/APEX_STATION_ALIGNMENT.md`.
- Workspace noise triage is in `docs/APEX_WORKSPACE_MENU.md`.
- Tool call syntax is in `registry/TOOL_INDEX.md`.
- External research should use Perplexity Pro first when available; this Codex context may not have that connector.

## Update Rule

When a shortcut prevents repeated investigation, add one row here with:

- The repeated problem.
- The proven route.
- The source document, issue, PR, or audit record that proves it.

Do not paste long transcripts into this file.
