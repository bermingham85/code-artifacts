# SPEC-SP-A.0 — Bootstrap kickoff (preflight inventory only)

> **Status: SUPERSEDED-BY-SPLIT (2026-05-30)** — Per `hub/WO-APEX-SP-A.0-SPLIT-001.json`, this spec did not reach silent-twice after 12 adversarial-review passes (`hub/WO-APEX-SP-A.0-STUCK-001.json`) and was formally split into `docs/spec/SPEC-SP-A.0a.md` (convergent inventory artifact) + `docs/policy/SP-A.0b-policy-contributions.md` (operational rule feeder, now absorbed by `docs/doctrine/APEX_DOCTRINE_v1.0.md`). Retained as evidence of the structural-non-convergence pattern that R14/PT9 (spec-complexity ceiling) was written to prevent. Do NOT use as a live spec template — use `PHASE_TEMPLATE.md` constrained by PT9.

This spec is **paper-only**. No code, no policy amendments, no bridge edits. Bridge hardening is performed under SP-A.1 (parent subproject's next micro-phase, repurposed from "Codex plugin install + verify" to "Codex bridge hardening + verify").

## Identity
- Phase ID: `SP-A.0`
- Title: Bootstrap kickoff (preflight)
- Parent subproject: `SP-A`
- Depends-on: none
- Blocks: SP-A.1 → all downstream
- Branch: `phase/A-0`
- Cert tag: `cert/SP-A.0@<sha>` (local tag now; PR batched per `WO-APEX-REPO-RECONCILE-001`)

## Inputs (9 authority-chain files; SHAs pinned in inventory)

Canonical hash: **SHA-256 over raw bytes**, stored at **full 64 hex** in the inventory (no truncation) so re-pin comparison cannot be defeated by collision attacks on a short prefix. Reference: `hashlib.sha256(open(path, "rb").read()).hexdigest()`. The re-pin check uses the same method on the full digest; any byte difference is a definitive content-change signal.
1. `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.md`
2. `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.rules.json`
3. `apex/docs/doctrine/conformance-checklist.md`
4. `apex_governance/PLAN_CRITERIA.md`
5. `apex_governance/SUBPROJECTS.md`
6. `apex_governance/PHASE_TEMPLATE.md`
7. `apex_governance/PROMPT_APEX_INGEST_PIPELINE.md`
8. `apex/PROJECT_APEX_v2.2.md`
9. `apex/hub/WO-BERM-RECEIPT-OCR-001.json`

## Access matrix (PLAN_CRITERIA §8)
- Read: the 9 input files above (immutable during SP-A.0); plus all SP-A.0 output files below (codex re-reads them on every adversarial-review pass and on the ship-gate review).
- Write: `apex/docs/spec/SPEC-SP-A.0*.md`, `apex_governance/findings/SP-A.0.findings.md`, `apex_governance/codex_runs/SP-A.0/<job-id>.txt`, `apex_governance/handovers/SP-A.0.handover.md`, `apex_governance/certs/PHASE-SP-A.0.codex.md`, `apex_governance/post_phase/SP-A.0/*.md` (including `cleanup-todo.md` and `cleanup-report.md`), `apex_governance/_scratch/SP-A.0/` (read-write during the phase; deleted at cleanup gate), `apex_governance/cc_runbook/INDEX.md` (status flips), `apex_governance/cc_runbook/state/spawn.log` (append), `apex_governance/certs/index.json` (create-if-missing or read-existing-then-append; atomic write via temp-file + `os.replace()` to defeat partial-write corruption). The cert-mint helper additionally implements a **collision detector** before write: it hashes the existing `index.json` immediately before the read-modify-write, and refuses to write if any other process has modified the file since the read (mtime + sha256 check). On collision, the mint aborts with a clear error and an incident WO is dropped. This is not a true file-lock — concurrent locking belongs to `WO-APEX-CERT-INDEX-LOCK-001` owned by SP-B.6 — but the detector ensures unsafe concurrent writes fail safely rather than silently corrupting the index. SP-A.0 ships with this detector + the documented single-writer assumption (SP-A.0 is the first cert and no other phase is running concurrently because SP-A.1 is BLOCKED behind SP-A.0).
- Secrets: none read, none written. `~/.codex/auth.json` is **out of access scope**; codex auth state is observed only via `codex login status`, which prints a redacted identifier and never leaves credential material in any SP-A.0 output. OPENAI_API_KEY quota status is tracked in `reference_env_keys.md` (programme memory), out of scope here.

## Outputs
- `apex/docs/spec/SPEC-SP-A.0.md` (this file)
- `apex/docs/spec/SPEC-SP-A.0.preflight-inventory.md` (the SHA-pinned table)
- `apex_governance/findings/SP-A.0.findings.md` (gap-analysis bullets; ≤10 is the expected count for a properly-scoped paper-only phase, not a hard cap — every distinct gap is logged regardless of total)
- `apex_governance/handovers/SP-A.0.handover.md` (closure version)
- `apex_governance/certs/PHASE-SP-A.0.codex.md` (minted at close)
- `apex_governance/certs/index.json` (create-if-missing or append-existing; SP-A.0 contributes exactly 1 row)
- `apex_governance/post_phase/SP-A.0/*.md` — one file per skill **derived dynamically** from the skill enumerations in `PLAN_CRITERIA.md` §1.5 + `PROMPT_APEX_INGEST_PIPELINE.md` §6B (whichever is live at SHAs pinned in the inventory). At the current pinned SHAs the derivation yields 9 skills: `review-relevant-skills`, `skill-scanner`, `tool-capability-updater`, `intelligent-task-delegator`, `conversation-task-extractor`, `research-synthesis`, `pipeline-governance` (must return 12/12 green), `automated-review-system` (must have no open rejects), `doc-coauthoring`. **This list is illustrative of the current derivation, not authoritative.** If the upstream sources change between phase open and cert mint, the SHA re-pin check forces a full pipeline restart and the post_phase output set is regenerated from the new derivation; this spec is NOT updated mid-phase to reflect the new list because the spec itself is one of the regenerated artifacts in a restart. Plus `cleanup-todo.md` and `cleanup-report.md` per §12.4 (one of each).

## Definition of Done (binary)
- [ ] All 9 authority-chain files loaded and SHA-pinned in `SPEC-SP-A.0.preflight-inventory.md`.
- [ ] **Pre-closure re-pin check + freeze**: at phase open, the 9 authority-chain SHAs are pinned in the inventory and an informal "input freeze" applies for the rest of SP-A.0 (notifying upstream authors is out of scope for SP-A.0 — no secret-backed channels are used; the freeze is a soft norm carried in this handover). Immediately before cert mint, re-hash all 9 input files. If any SHA still differs from the inventory, abort closure and re-run the entire SP-A.0 deliverable pipeline against the new inputs: update the inventory, regenerate the gap analysis, regenerate every `post_phase/SP-A.0/*.md` (deleting any files for skills no longer in the upstream lists), re-run the spec adversarial-review cycle to silent-twice, re-run the bundle adversarial-review to silent-twice, and re-run the ship-gate review on the regenerated bundle. **A "restart cycle"** = exactly one full pipeline rerun: increments by 1 each time the re-pin check detects drift and triggers a fresh execution; it does not reset within a phase. The counter is persisted as a single line appended to `apex_governance/cc_runbook/state/spawn.log` of the form `<UTC-iso> RESTART_CYCLE SP-A.0 cycle=<N>` so all operators can verify the count. If three restart cycles complete without drift-free closure, the phase is paused via an incident WO and a `WO-APEX-SP-A.0-DRIFT-001` is dropped for upstream stabilisation outside the SP-A.0 scope.
- [ ] `apex_governance/post_phase/SP-A.0/cleanup-report.md` exists per PLAN_CRITERIA §12.4. Content lists (a) every file **created** by SP-A.0 (the spec, inventory, findings, handover, cert, post_phase outputs, INDEX/spawn.log appends), (b) every file **deleted** during cleanup (the codex-unreachable flag, _scratch dir contents), (c) every file **renamed or reconciled** (none expected for a paper phase). If any of (a)/(b)/(c) is empty it is recorded explicitly as "none in this category"; the report is never empty.
- [ ] Gap-analysis written: every distinct gap recorded as its own bullet, each with the absorbing SP (target ≤10; overflow allowed, no merging or omission).
- [ ] Spec adversarial-review reaches silent-twice (two consecutive `findings=0`).
- [ ] Inventory + gap-analysis bundle adversarial-review reaches silent-twice.
- [ ] Ship-gate `review` on the bundle returns clean.
- [ ] 9 post-phase skill outputs landed. `pipeline-governance` returns **all checks green** (the canonical 12-check audit at the SHAs pinned in the inventory; if the upstream check-list length changes, the SHA re-pin restart regenerates this output and re-validates against the new length). `automated-review-system` returns no rejects. Both are hard preconditions for closure — no deferral path on either; the ship-gate review will catch any non-green result and reject closure.
- [ ] Handover delivered, INDEX → DONE, cert tag minted, `certs/index.json` appended.
- [ ] Cleanup gate green: `_scratch/SP-A.0/` removed; `post_phase/SP-A.0/cleanup-todo.md` empty (or every item has a closed deferral).
- [ ] Doctrine conformance table is part of the **cert artifact** (`PHASE-SP-A.0.codex.md`), populated at cert-mint stage from `conformance-checklist.md` (whichever version is live at mint time — the cert records the SHA of the checklist actually used, not a hardcoded version label). The pre-closure re-pin check above includes both the rules JSON and the checklist; if either's SHA differs from the inventory, closure aborts and re-runs.

## Codex commands (per stage)
| Stage | Command | Expected |
|---|---|---|
| Spec | `codex_bridge.py adversarial-review apex/docs/spec/SPEC-SP-A.0.md --phase SP-A.0` | silent-twice |
| Bundle | `codex_bridge.py adversarial-review` on inventory + findings | silent-twice |
| Ship gate | `codex_bridge.py review` over the **complete SP-A.0 deliverable set**: `SPEC-SP-A.0.md`, `SPEC-SP-A.0.preflight-inventory.md`, `SP-A.0.findings.md`, `SP-A.0.handover.md`, `PHASE-SP-A.0.codex.md`, every `post_phase/SP-A.0/*.md` (9 skill outputs + cleanup-todo.md + cleanup-report.md). | `findings=0` |
| Rescue | `codex_bridge.py rescue apex_governance --phase SP-A.0` — triggered when 5 consecutive `codex_bridge.py adversarial-review` invocations on the **same target** (single file or single bundle) have failed to reach `findings=0`. An attempt is one bridge invocation; the counter is per-target and is the count of consecutive `adversarial-review` transcripts in `apex_governance/codex_runs/SP-A.0/` (filename-ordered) for that target with non-zero `findings=` lines. The orchestrator running the bridge calls (i.e. the operator/agent currently driving SP-A.0) is responsible for monitoring the count and invoking rescue at threshold; SP-A.0 ships no automation for this — automation is tracked as part of SP-B.6 supervisor enforcement. A drift-triggered restart resets the counter for any target whose content was regenerated. | findings closed |

Every transcript persists to `apex_governance/codex_runs/SP-A.0/<job-id>.txt`. Codex calls log model = `gpt-5-codex`, reasoning = `high`, auth_mode per `~/.codex/auth.json` (currently `apikey`; user can switch to subscription via `codex login` at any time without breaking the flow).

## Rollback
SP-A.0 ships only docs. Rollback = `git restore` on the file set listed in Outputs; no data, no infra, no merged PR to revert.

## Doctrine conformance (against DRAFT v0.1; populated at cert mint, not here)
Use the table from `apex/docs/doctrine/conformance-checklist.md` as-is. SP-A.0 cert fills it; this spec does not pre-populate it to avoid divergence.

## What this spec deliberately does NOT do
- Does not amend SUBPROJECTS.md `"No code yet"` for SP-A.0. Keep SP-A.0 paper-only.
- Does not specify, scope, or run any code change to `codex_bridge.py`. Bridge hardening = SP-A.1.
- Does not enumerate the full `apex_governance/` tree as findings. Programme-wide gaps = the 8 RSC findings already attributed to their owning subprojects in the resume-protocol handover.
- Does not relax PLAN_CRITERIA §5.x. Deferral protocol stays a question for SP-A.2's doctrine lock.
