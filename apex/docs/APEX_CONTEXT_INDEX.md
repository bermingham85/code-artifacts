# Apex Context Index

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00009 |
| Version | 1.1 |
| Status | ACTIVE |
| Purpose | Low-token entry point for future Claude, Codex, and orchestrator contexts |

## Boot Rule

Read this file first. It is the compact map. Do not load large specs, transcripts, audit folders, or workflow exports unless the current task needs them.

## Current Governed Foundation

| Area | Status | Path |
|---|---|---|
| Autonomous delivery foundation certificate | APPROVED | `audit/CERT-APEX-AUTONOMOUS-DELIVERY.json` |
| APEX governance doctrine (locked) | ACTIVE (v1.0-PROVISIONAL pending SP-A.2 ratification) | `docs/doctrine/APEX_DOCTRINE_v1.0.md` |
| Tool selection menu | ACTIVE | `docs/APEX_TOOL_MENU.md` |
| Work authority gate | ACTIVE | `docs/APEX_WORK_GATE.md` |
| Active queue / next action | ACTIVE | `docs/APEX_ACTIVE_QUEUE.md` |
| Memory shortcuts / proven routes | ACTIVE | `docs/APEX_MEMORY_SHORTCUTS.md` |
| Station alignment checklist | ACTIVE | `docs/APEX_STATION_ALIGNMENT.md` |
| Supabase project isolation policy | ACTIVE | `docs/policy/SUPABASE_PROJECT_ISOLATION.md` |
| Supabase shared project boundary | ACTIVE | `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md` |
| Supabase RLS rollout plan | DRAFT | `docs/policy/SUPABASE_RLS_ROLLOUT_PLAN.md` |
| Workspace artifact menu | ACTIVE | `docs/APEX_WORKSPACE_MENU.md` |
| Repository menu | ACTIVE | `docs/APEX_REPO_MENU.md` |
| Parallel merge playbook | ACTIVE | `docs/APEX_PARALLEL_MERGE_PLAYBOOK.md` |
| Machine-readable tool menu | ACTIVE | `docs/APEX_TOOL_MENU.json` |
| Master autonomous delivery spec | ACTIVE | `docs/spec/SPEC-APEX-AUTONOMOUS-DELIVERY-SYSTEM.md` |
| Document register | ACTIVE | `docs/DOCUMENT_REGISTER.md` |
| Approved tool index | ACTIVE | `registry/TOOL_INDEX.md` |
| Tool manifest | ACTIVE | `registry/manifest.json` |

## What Is Already Done

- The Apex autonomous delivery foundation package is complete.
- The master spec defines discovery, headless laptop setup, remote access, WOL/power fallback, Claude/Codex bridge, n8n/Make orchestration, resource locks, backup/restore, troubleshooting, testing, and signoff.
- `muscle_headless_inventory` is approved.
- `muscle_resource_guard` is approved.
- `docs/APEX_TOOL_MENU.md` is the low-token cover page for tool selection.
- `docs/APEX_WORK_GATE.md` defines the authority gate for repo edits, fallback-machine continuation, and artifact promotion.
- `docs/APEX_ACTIVE_QUEUE.md` defines current branch state, completed packets, blocked items, and next actions.
- `docs/APEX_MEMORY_SHORTCUTS.md` defines reusable shortcut routes so future agents do not repeatedly remap source-of-truth, fallback, station, and handoff procedures.
- `docs/APEX_STATION_ALIGNMENT.md` defines station-level shutoffs for Claude, Codex, X-drive access, and sync scripts.
- `docs/policy/SUPABASE_PROJECT_ISOLATION.md` and `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md` define the live Supabase boundary: the instance is shared across 11 projects; new Apex work goes to `APEX`; protected project tables and rows are read-only unless explicitly authorized.
- `docs/policy/SUPABASE_RLS_ROLLOUT_PLAN.md` captures the critical RLS advisory route; do not auto-enable RLS without policies and smoke tests.
- `docs/APEX_WORKSPACE_MENU.md` is the low-token cover page for loose/uncommitted artifact groups.
- `docs/APEX_REPO_MENU.md` is the low-token cover page for repositories under scanned roots.
- `docs/APEX_PARALLEL_MERGE_PLAYBOOK.md` explains how to combine the Codex-built index package with the parallel Claude governance run.
- `docs/APEX_TOOL_MENU.md` is generated from `docs/APEX_TOOL_MENU.json`.
- Every approved tool has a version-controlled `troubleshoot.md` for reusable fixes.
- Required approval docs exist for both support tools: blueprint, guidance, and test record.
- Completion certificate is registered in document control.

## Approved New Support Tools

| Tool | Ref | Purpose | Primary doc |
|---|---|---|---|
| `muscle_headless_inventory` | APEX-MB-CFG-00003 | Read-only laptop inventory without collecting secrets | `docs/tools/muscle_headless_inventory/guidance.md` |
| `muscle_resource_guard` | APEX-MB-CFG-00004 | Scheduled-job resource and lock gate | `docs/tools/muscle_resource_guard/guidance.md` |
| `muscle_work_gate` | APEX-MB-PY-00029 | Repo/artifact authority preflight for normal and fallback work | `docs/tools/muscle_work_gate/guidance.md` |

Use `registry/TOOL_INDEX.md` for exact call syntax.

## Reusable Templates

| Template | Ref | Path |
|---|---|---|
| Task Packet | APEX-MB-SCH-00002 | `docs/templates/apex_task_packet_template.json` |
| Completion Certificate | APEX-MB-DOC-00003 | `docs/templates/apex_completion_certificate_template.md` |
| Workflow Blueprint | APEX-MB-DOC-00004 | `docs/templates/apex_workflow_blueprint_template.md` |

## Operating Contract

- Claude owns architecture, reasoning, documentation, review criteria, and signoff.
- Codex owns local code edits, scripts, tests, config updates, log parsing, and safe repair commands.
- n8n/Make owns orchestration, webhooks, schedules, branching, retries, and error workflows.
- Git and Apex document control are the source of truth for artifacts.

## Security Boundary

Only configure devices, networks, accounts, services, and APIs that the user owns or is explicitly authorized to administer.

Do not:

- Bypass authentication.
- Hide access or create unauthorized persistence.
- Store plaintext secrets in repo files.
- Power-cycle during active writes, backups, or deployments except under documented emergency recovery.
- Use smart plugs, fingerbots, WOL, or remote access without explicit authorization and safety checks.

## External Research Rule

Use Perplexity Pro first for external research when available. Ask for concise synthesis with source links and prefer official/primary sources. If unavailable, say so and use targeted source reads. Do not send private repo code or secrets to external research tools unless explicitly approved.

## When To Load More

| Need | Load |
|---|---|
| Need exact autonomous architecture | `docs/spec/SPEC-APEX-AUTONOMOUS-DELIVERY-SYSTEM.md` |
| Need approved call syntax | `registry/TOOL_INDEX.md` |
| Need choose a tool | `docs/APEX_TOOL_MENU.md` |
| Need edit a repo, use fallback work, or promote artifacts | `docs/APEX_WORK_GATE.md`, then `python registry/muscle_work_gate.py --repo . --intent write --fetch` |
| Need avoid rediscovering Apex routes | `docs/APEX_MEMORY_SHORTCUTS.md` |
| Need align another station or LLM install | `docs/APEX_STATION_ALIGNMENT.md` |
| Need write to Supabase project tables | `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md`, `docs/policy/SUPABASE_PROJECT_ISOLATION.md`, then set `$env:APEX_BOUNDARY_DOC_READ='APEX-MB-DOC-00038-v1.0'` and run `python registry\supabase_project_guard.py --expect-code APEX` |
| Need understand uncommitted artifacts | `docs/APEX_WORKSPACE_MENU.md` |
| Need choose or review a repo | `docs/APEX_REPO_MENU.md` |
| Need combine parallel Claude/Codex work | `docs/APEX_PARALLEL_MERGE_PLAYBOOK.md` |
| Need apex governance doctrine | `docs/doctrine/APEX_DOCTRINE_v1.0.md` (v1.0-PROVISIONAL pending SP-A.2 ratification) |
| Need update the menu | Edit `docs/APEX_TOOL_MENU.json`, then run `python registry/generate_tool_menu.py` |
| Need refresh repo index | `python registry/generate_repo_menu.py --root C:\Users\Owner\Repos` |
| Need know what to do next | `docs/APEX_ACTIVE_QUEUE.md` |
| Need document-control status | `docs/DOCUMENT_REGISTER.md` |
| Need evidence/signoff | `audit/CERT-APEX-AUTONOMOUS-DELIVERY.json` |
| Need inventory tool details | `docs/tools/muscle_headless_inventory/blueprint.md` and `guidance.md` |
| Need resource guard details | `docs/tools/muscle_resource_guard/blueprint.md` and `guidance.md` |
| Need fix a known tool failure | `docs/tools/<tool>/troubleshoot.md` |
| Need verify tool docs coverage | `python registry/validate_tool_docs.py` |

## Known Boundary

The foundation is saved and certified locally. Physical laptop deployment, credentials, Tailscale/SSH binding, BIOS/WOL verification, smart plug/fingerbot setup, backup destination binding, and live n8n deployment still require authorized access and any physical actions that cannot be automated.
