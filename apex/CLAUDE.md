# Apex Claude Context

Use the low-token boot path:

1. Read `docs/APEX_CONTEXT_INDEX.md`.
2. Use `docs/APEX_TOOL_MENU.md` to choose tools with low token burn.
3. Use `docs/APEX_WORK_GATE.md` before editing repos, continuing fallback work, or promoting artifacts.
4. Use `docs/APEX_WORKSPACE_MENU.md` to understand loose artifact groups without opening every file.
5. Use `docs/APEX_REPO_MENU.md` to choose or review repositories.
6. Use `registry/TOOL_INDEX.md` for approved callable tools.
7. Use `docs/DOCUMENT_REGISTER.md` for governed artifact paths and status.
8. Load full specs only when the task requires implementation detail.

For the autonomous delivery system, the foundation is already documented, approved, and certified. Start from:

- `docs/APEX_CONTEXT_INDEX.md`
- `docs/APEX_TOOL_MENU.md`
- `docs/APEX_WORK_GATE.md`
- `docs/APEX_WORKSPACE_MENU.md`
- `docs/APEX_REPO_MENU.md`
- `audit/CERT-APEX-AUTONOMOUS-DELIVERY.json`
- `docs/spec/SPEC-APEX-AUTONOMOUS-DELIVERY-SYSTEM.md` only if deeper implementation detail is needed.

Use Perplexity Pro first for external research when available. Keep private code and secrets local unless explicitly approved.

Before any repository edit, artifact promotion, or fallback-machine continuation, run:

```bash
python registry/muscle_work_gate.py --repo . --intent write --fetch
```

Do not push protected branches or write directly into X-drive canonical folders. Local machine files are working state only until the work gate and merge/promotion route make them official.
