# Apex Context Index

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00009 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Low-token entry point for future Claude, Codex, and orchestrator contexts |

## Boot Rule

Read this file first. It is the compact map. Do not load large specs, transcripts, audit folders, or workflow exports unless the current task needs them.

## Current Governed Foundation

| Area | Status | Path |
|---|---|---|
| Autonomous delivery foundation certificate | APPROVED | `audit/CERT-APEX-AUTONOMOUS-DELIVERY.json` |
| Tool selection menu | ACTIVE | `docs/APEX_TOOL_MENU.md` |
| Workspace artifact menu | ACTIVE | `docs/APEX_WORKSPACE_MENU.md` |
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
- `docs/APEX_WORKSPACE_MENU.md` is the low-token cover page for loose/uncommitted artifact groups.
- `docs/APEX_TOOL_MENU.md` is generated from `docs/APEX_TOOL_MENU.json`.
- Every approved tool has a version-controlled `troubleshoot.md` for reusable fixes.
- Required approval docs exist for both support tools: blueprint, guidance, and test record.
- Completion certificate is registered in document control.

## Approved New Support Tools

| Tool | Ref | Purpose | Primary doc |
|---|---|---|---|
| `muscle_headless_inventory` | APEX-MB-CFG-00003 | Read-only laptop inventory without collecting secrets | `docs/tools/muscle_headless_inventory/guidance.md` |
| `muscle_resource_guard` | APEX-MB-CFG-00004 | Scheduled-job resource and lock gate | `docs/tools/muscle_resource_guard/guidance.md` |

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
| Need understand uncommitted artifacts | `docs/APEX_WORKSPACE_MENU.md` |
| Need update the menu | Edit `docs/APEX_TOOL_MENU.json`, then run `python registry/generate_tool_menu.py` |
| Need document-control status | `docs/DOCUMENT_REGISTER.md` |
| Need evidence/signoff | `audit/CERT-APEX-AUTONOMOUS-DELIVERY.json` |
| Need inventory tool details | `docs/tools/muscle_headless_inventory/blueprint.md` and `guidance.md` |
| Need resource guard details | `docs/tools/muscle_resource_guard/blueprint.md` and `guidance.md` |
| Need fix a known tool failure | `docs/tools/<tool>/troubleshoot.md` |
| Need verify tool docs coverage | `python registry/validate_tool_docs.py` |

## Known Boundary

The foundation is saved and certified locally. Physical laptop deployment, credentials, Tailscale/SSH binding, BIOS/WOL verification, smart plug/fingerbot setup, backup destination binding, and live n8n deployment still require authorized access and any physical actions that cannot be automated.
