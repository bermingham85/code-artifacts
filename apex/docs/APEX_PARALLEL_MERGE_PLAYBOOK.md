# Apex Parallel Merge Playbook

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00026 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Instructions for combining the Codex-built Apex index package with the parallel Claude governance run |

## Decision

Use the committed Apex low-token index package as the canonical product baseline.

Treat the parallel Claude run as a source of review evidence, doctrine candidates, work-order history, and candidate tools. Do not bulk-merge it into the product surface. Promote only the parts that pass the Apex approval pattern: registered artifact, purpose, exact usage, tests, evidence, troubleshooting, and rollback.

## Why This Wins

The Codex-built package now provides the selection layer the project needed:

- `docs/APEX_CONTEXT_INDEX.md` gives every future context the first page to read.
- `docs/APEX_TOOL_MENU.md` gives exact tool selection, usage, and troubleshooting links.
- `docs/APEX_WORKSPACE_MENU.md` explains loose and uncommitted artifact groups without opening each file.
- `docs/APEX_REPO_MENU.md` gives repository selection and current state.
- `registry/validate_tool_docs.py` enforces coverage for approved tools.

The Claude parallel run adds useful operating doctrine, but it is broader and noisier. Its value is highest when distilled into governed rules and approved tools, not when pasted into the main index unchanged.

## Source Tracks

| Track | Current role | Merge treatment |
|---|---|---|
| Apex index/menu package | Canonical baseline | Keep as the entry point for future Claude, Codex, and orchestrator windows |
| `docs/doctrine/` | Draft governance doctrine | Review and promote as a doctrine package after conflict checks |
| `docs/policy/` | Policy contribution feeder | Merge selected rules into doctrine, then archive or mark superseded |
| `registry/muscle_compliance_check.py` | Candidate validator tool | Promote into approved tool docs or merge its checks into `validate_tool_docs.py` |
| `registry/claude_codex_loop.py` | Candidate automation loop | Promote as an approved orchestration tool with evidence and safeguards |
| `audit/claude_codex_loop/` | Evidence transcripts | Keep only as linked evidence for approved loop/governance claims |
| `hub/WO-APEX-*.json` | Incident and split work orders | Commit with the doctrine/governance batch if still active |
| `docs/spec/SPEC-SP-A.0*` | Legacy/bootstrap specs | Review as SP-A governance history; do not make them primary context |
| `audit/receipt_ocr_raw/` | Raw OCR output | Do not commit until checked for sensitive receipt data |
| `mbw_comfyui_stitch_flow/` | Separate project package | Keep out of Apex index/governance commits unless explicitly scoped |

## Merge Order

1. Refresh the low-token maps:

```powershell
python registry\generate_repo_menu.py --root C:\Users\Owner\Repos
python registry\validate_tool_docs.py --quiet
git status --short
```

2. Review `docs/APEX_WORKSPACE_MENU.md` before opening loose folders. It already groups the Claude-side artifacts and says what each group is for.

3. Promote the compliance checker first if it remains useful:

- Either approve `registry/muscle_compliance_check.py` as `muscle_compliance_check`.
- Or absorb its unique checks into `registry/validate_tool_docs.py`.
- Required approval files if kept as a tool:
  - `docs/tools/muscle_compliance_check/blueprint.md`
  - `docs/tools/muscle_compliance_check/guidance.md`
  - `docs/tools/muscle_compliance_check/test_record.md`
  - `docs/tools/muscle_compliance_check/troubleshoot.md`
- Then update `docs/APEX_TOOL_MENU.json`, regenerate `docs/APEX_TOOL_MENU.md`, and run `python registry\validate_tool_docs.py --quiet`.

4. Promote the Claude/Codex loop second:

- Keep `registry/claude_codex_loop.py` only if it has safe defaults, bounded retries, explicit logs, no plaintext secrets, and clear failure exits.
- Create the same four tool docs under `docs/tools/claude_codex_loop/`.
- Link only selected transcript evidence from `audit/claude_codex_loop/`; do not require future contexts to read the whole audit tree.
- Add rollback instructions: disable scheduled callers, keep transcript evidence, and restore the previous script version from Git.

5. Merge doctrine third:

- Compare `docs/doctrine/CLAUDE_CODEX_DOCTRINE.md`, `.rules.json`, and `conformance-checklist.md` against the already-approved Apex operating contract.
- Keep rules that improve repeatability: Codex review gates, loop caps, evidence storage, Perplexity-first research routing, no Claude self-review fallback when Codex review is required, and explicit closure conditions.
- Downgrade or rewrite any rule that depends on unavailable plugins, impossible "silent forever" gates, unlimited token spend, or private local paths.
- Register the final doctrine package in `docs/DOCUMENT_REGISTER.md`.

6. Merge work orders and SP-A specs fourth:

- Keep active incident work orders that explain real blockers.
- Mark superseded work orders as closed or historical.
- Use SP-A specs as history unless they define an active next build phase.
- Do not let SP-A bootstrap material replace the low-token context index as the first-read document.

7. Keep sensitive or unrelated outputs out:

- Inspect raw OCR and receipt folders before staging.
- Keep `.claude/` local unless intentionally sharing project configuration.
- Keep ComfyUI workflow work in its own package unless a future task explicitly brings it into Apex.

## Conflict Resolution Rules

| Conflict | Winner |
|---|---|
| Two files claim to be the first context entry | `docs/APEX_CONTEXT_INDEX.md` |
| Tool usage is described in several places | `docs/APEX_TOOL_MENU.md` plus each tool `guidance.md` |
| Troubleshooting fix appears in chat or audit only | Move it to `docs/tools/<tool>/troubleshoot.md` |
| Claude doctrine conflicts with approved Apex security boundary | Apex security boundary wins |
| Claude doctrine adds useful stricter review gates | Keep the gate if bounded, testable, and affordable |
| Raw transcript conflicts with distilled doc | Distilled registered doc wins; transcript remains evidence only |
| A WIP script is useful but undocumented | It remains WIP until approved docs and tests exist |

## Final Product Shape

The combined best product should have this surface:

| User need | Entry point |
|---|---|
| Start any future context cheaply | `docs/APEX_CONTEXT_INDEX.md` |
| Pick a tool and know exact usage | `docs/APEX_TOOL_MENU.md` |
| Understand repo landscape | `docs/APEX_REPO_MENU.md` |
| Understand loose work | `docs/APEX_WORKSPACE_MENU.md` |
| Add a new reusable fix | `docs/tools/<tool>/troubleshoot.md` |
| Approve a WIP tool | Four docs + validator + generated menu |
| Review doctrine/history | This playbook, then `docs/doctrine/` |

## Completion Criteria

The merge is complete only when:

- The low-token indexes point to the merged doctrine/tools.
- Every promoted tool has blueprint, guidance, test record, and troubleshoot docs.
- `python registry\validate_tool_docs.py --quiet` returns OK.
- Sensitive raw outputs are excluded or explicitly approved.
- `docs/DOCUMENT_REGISTER.md` has rows for every final artifact.
- The final commit message names the promoted batch, not the whole WIP tree.
