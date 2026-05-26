# Apex Agent Context

This repository uses a low-token boot path. Do not load the full spec first.

## Load Order

1. Read `docs/APEX_CONTEXT_INDEX.md`.
2. Read `docs/APEX_TOOL_MENU.md` when choosing a tool.
3. Read `docs/APEX_WORK_GATE.md` before editing repos, continuing from fallback machines, or promoting artifacts.
4. Read `docs/APEX_WORKSPACE_MENU.md` when deciding what to do with loose, uncommitted, or unfamiliar artifact groups.
5. Read `docs/APEX_REPO_MENU.md` when choosing or reviewing a repository.
6. Read `registry/TOOL_INDEX.md` only when confirming approved call syntax.
7. Read `docs/DOCUMENT_REGISTER.md` only when checking artifact status or paths.
8. Read the full spec only when implementing or changing the autonomous delivery system:
   `docs/spec/SPEC-APEX-AUTONOMOUS-DELIVERY-SYSTEM.md`.

## Research Routing

Use Perplexity Pro first for external research when available. Keep web/source reads targeted. Inspect local repository files directly for code and governance facts. Do not send private code or secrets to external tools unless explicitly approved.

## Autonomous Delivery Foundation

The governed foundation package is certified complete in:

`audit/CERT-APEX-AUTONOMOUS-DELIVERY.json`

Approved support tools:

- `muscle_headless_inventory`: read-only headless laptop inventory.
- `muscle_resource_guard`: disk, memory, duplicate-job, backup/deploy/destructive, and optional GPU lock gate.
- `muscle_work_gate`: repo/artifact authority preflight for normal and fallback work.

Before any agent edits a repository, promotes artifacts, or continues work from a non-primary station, run the work gate. Local C-drive files are working state only. GitHub protected branches and the X-drive canonical/index route are the authority; fallback work stays provisional until the gate allows promotion.

Every approved tool has a version-controlled `troubleshoot.md`. Add reusable fixes there so later contexts can solve the same failure without re-researching.

Security boundary: only administer devices, services, accounts, and networks owned by or explicitly authorized for the user. No hidden access, credential bypass, plaintext secrets, or unsafe power actions.
