# Apex Active Queue

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00036 |
| Version | 1.0 |
| Status | ACTIVE |
| Updated | 2026-05-30T09:21:17Z |
| Purpose | Low-token current-state page so Claude, Codex, and future contexts stop rediscovering completed work. |

## Read First Rule

After `docs/APEX_CONTEXT_INDEX.md`, read this file before opening any work order, transcript, audit folder, or untracked artifact.

Do not paste chat history between agents as the source of truth. Pull the branch and use committed files.

## Current Branch State

| Item | State |
|---|---|
| Branch | `apex/estate-seed-00004` |
| Latest required head | `d5a3678` or later |
| Claude continuation | Completed by commits `89daf2f`, `80197a5`, `7e456f7`; packet marked complete in `hub/WO-APEX-CLAUDE-CONTINUE-005.json`. |
| AGEN task schema review | Reviewed with verdict `REVISE` in `hub/WO-APEX-AGEN-TASKS-SCHEMA-REVIEW-006.json`. |
| AGEN task lineage spec | Created in `docs/spec/SPEC-AGEN-TASK-LINEAGE-v1.md`. |
| AGEN task lineage design | Created in `docs/policy/AGEN_TASK_LINEAGE_DESIGN_v1.md`. |
| Supabase APEX project boundary | Live project `APEX / Apex Autonomous Delivery` created with id `243bed23-67d6-4f69-b382-e771c57abed7`; `JESS` protected/read-only by policy. |
| AGEN task lineage migration draft | Local draft exists with review verdict `REVISE`; nested draft branch `codex/agen-task-lineage-draft` commit `92d8189`; no production migration applied. |
| SP-A.0 split | Still open only because SP-A.2 doctrine ratification is pending; do not redo SP-A.0 work. |

## Do Not Reprocess

- Do not re-run Claude continuation batches from `WO-APEX-CLAUDE-CONTINUE-005`.
- Do not promote `docs/spec/SCOPE-AGEN-AGENT-TASKS-SCHEMA-FIX-v1.md`; it is superseded by the compact spec and design note.
- Do not commit raw `audit/claude_codex_loop/*` attempts unless directly linked by a work order or certificate.
- Do not read, print, move, or stage secret-bearing files, especially `active_projects/bermcoin/.env`.
- Do not write new Apex automation rows into `JESS`; use `APEX` unless an approved work order explicitly names another project.

## Active Next Actions

| Priority | Work | Owner | Gate |
|---|---|---|---|
| P1 | AGEN task-lineage implementation: `hub/WO-APEX-AGEN-TASK-LINEAGE-IMPLEMENT-007.json`. | Codex | Local migration draft exists but needs revision: actual `create_architecture_revision` patch and canonical `agent_task_dependencies` translation are still required. No production migration without backup and explicit approval. |
| P2 | SP-A.2 doctrine ratification: run the doctrine silent-twice loop against `docs/doctrine/APEX_DOCTRINE_v1.0.md`. | Claude+Codex bridge | Codex adversarial/ship-gate tooling required. |
| P3 | Workspace noise triage: classify untracked audit/spec/raw folders without reading secrets. | Codex | Work gate and targeted file review only. |

## Next Agent Command

Use this sequence instead of asking the user what to do next:

```powershell
git pull origin apex/estate-seed-00004
python registry\muscle_work_gate.py --repo . --intent write --fetch --allow-dirty
Get-Content docs\APEX_ACTIVE_QUEUE.md
```

Then pick the first active next action that is not blocked in the current environment.

## Current Blockers

| Blocker | Effect | Safe fallback |
|---|---|---|
| Production migration approval not yet granted | Cannot apply task-lineage SQL to live Supabase. | Draft SQL, rollback, tests, and Codex review packet only. |
| Codex CLI external review blocked without explicit approval | Cannot claim independent CLI review in this context. | Use local deterministic review findings, or get explicit approval to send named files to Codex CLI. |
| No Perplexity Pro connector in this Codex context | Cannot satisfy external-research-first route here. | Record limitation; use local governed materials only. |
| SP-A.2 needs actual Codex adversarial/ship-gate loop | Cannot honestly mark doctrine `1.0-LOCKED` from local file edits alone. | Keep doctrine `1.0-PROVISIONAL` binding and leave SP-A.0 split open. |

## Handoff Sentence

Tell any Claude/Codex context: "Pull `apex/estate-seed-00004`, read `docs/APEX_CONTEXT_INDEX.md`, then `docs/APEX_ACTIVE_QUEUE.md`; do not use chat text as authority."
