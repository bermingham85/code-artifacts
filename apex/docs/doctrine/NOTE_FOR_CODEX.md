# Note for Codex reviewer (WO-APEX-PROMOTE-DOCTRINE-003)

**STATUS — OUTDATED (2026-05-25 ~21:30Z).** Written by Claude AFTER Codex had already completed Batch 3 in parallel. Codex wrote `APEX_DOCTRINE_v1.0.md` at 20:49Z, annotated the four source files at 20:50Z, and updated `DOCUMENT_REGISTER.md` + `APEX_CONTEXT_INDEX.md` at 21:28-21:32Z, before this note was authored. The text below describes work Claude was offering to do that **Codex had already done**. This file is kept as historical provenance only; the canonical doctrine is `APEX_DOCTRINE_v1.0.md`.

---

Claude has drafted **both** deliverables for this batch in one turn (operating-contract documentation role):

1. **`DOCTRINE_v1.0_LOCK_PROPOSAL.md`** — per-rule verdicts (KEEP / DOWNGRADE / REJECT) with rationale. This is the WORKING DOC for verdict review.
2. **`APEX_DOCTRINE_v1.0.md`** — the resulting LOCKED doctrine (v1.0-PROVISIONAL pending your review). This is the FINAL DELIVERABLE.

Your job per the Task Packet (`hub/WO-APEX-PROMOTE-DOCTRINE-003.json`) is now:

- **Review BOTH together.** Check that every verdict in the proposal is faithfully represented in the locked doc. Disagree freely — emit a counter-proposal as Task Result rather than silently editing either file.
- **Allocate the ref code** for `APEX_DOCTRINE_v1.0.md` via `doc_controller.py` (the proposal suggests `APEX-MB-DOC-00027`; verify availability).
- **Update the source files** with SUPERSEDED-BY-LOCK headers (write scope #2–#5 in the Task Packet). Do NOT delete bodies.
- **Add the register row** in `docs/DOCUMENT_REGISTER.md`.
- **Update `docs/APEX_CONTEXT_INDEX.md`** "Current Governed Foundation" table with the doctrine row.
- **Run `validate_tool_docs --quiet`** after each register edit.

### What Claude did NOT do
- Did NOT touch Batch 1 (`muscle_compliance_check`) files — your patches preserved.
- Did NOT touch Batch 2 (`claude_codex_loop`) files — your patches + approval preserved.
- Did NOT mark anything "Approved" in this batch — this is doctrine, not tool approval.
- Did NOT stage raw audit subtrees or OCR/receipt data.
- Did NOT push the branch — that requires explicit user instruction (per status 2026-05-25 14:16Z update).

### Cross-links honoured (per user instruction 2026-05-25 14:16Z)
Every new rule in `APEX_DOCTRINE_v1.0.md` carries an explicit cross-link to `APEX_PARALLEL_MERGE_PLAYBOOK.md`:
- D1–D4 bridge fallback footnote → playbook §"Source Tracks"
- PT6 re-pin check → playbook §"Conflict Resolution Rules"
- PT8a superset-repo handling → playbook §"Conflict Resolution Rules"
- O6 transcript path reconciliation → playbook §"Conflict Resolution Rules"
- O14 paid-API hygiene → playbook §"Conflict Resolution Rules" (distilled-over-raw)
- O15 path absolutism → playbook §"Merge Order" step 1
- R19 path-update → playbook §"Merge Order" step 1

### Tracked separately (NOT this batch)
- Batch 1 hygiene remediation — the FAILs `muscle_compliance_check` correctly reports (stale paths, duplicate refs, header/register mismatches, older muscles missing docs, one `.env`) need their own Task Packet. Claude has flagged this as a follow-up but has not opened the WO yet.
