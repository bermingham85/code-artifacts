# SP-A.0b — Operational policy contributions (feeder to SP-A.2)

> **SUPERSEDED-BY-LOCK 2026-05-25.** R1-R14 have been merged into `apex/docs/doctrine/APEX_DOCTRINE_v1.0.md` (v1.0-PROVISIONAL) per `APEX_PARALLEL_MERGE_PLAYBOOK.md` step 5. Mapping: R1→O11, R2→PT6+PT7, R3→O12, R4→O13, R5→§10 spec-template addendum, R6→PT8 (with A2 clarification), R7→§10 spec-template addendum, R8→PT8a (sub-rule of PT8), R9→§11 doc-control matrix, R10→O15, R11 reclassified to SP-A.1 spec requirement, R12 reclassified to runbook hint, R13→O14, R14→PT9. This document is retained as historical evidence; do NOT add new rules here — propose them as amendments to the v1.0 doc directly. SP-A.2 will ratify v1.0 via silent-twice loop.

This document is **not** a spec. It is **not** subject to a per-phase silent-twice adversarial-review loop. It is a feeder to **SP-A.2 (Doctrine validation + lock v1.0)**: the candidate rule deltas below are merged into `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.md`, `.rules.json`, `conformance-checklist.md`, `PLAN_CRITERIA.md`, or `PHASE_TEMPLATE.md` (whichever is the natural home for each rule) and then the merged ruleset undergoes the silent-twice loop at SP-A.2.

**Provenance:** every rule below was generated as a finding during SP-A.0's 12-pass adversarial-review attempt against the original "Option A" spec (transcripts archived under `apex_governance/codex_runs/SP-A.0/SP-A.0-adv-*.txt`, plus the rescue transcript `SP-A.0-rescue-20260504T012809Z-7aa289a1.txt`). Each finding is restated here as a **rule shape** (what the doctrine should require) rather than as a defect (what the spec failed to specify).

**Status:** `IN-PROGRESS-FEEDER`. SP-A.0b's INDEX row remains in this state until SP-A.2 closes; at that point SP-A.0b inherits SP-A.2's cert by reference and flips to `DONE`.

---

## R1. Hashing standard for authority-chain inventories

**Source finding:** SP-A.0-AV-pass-J/L "SHA algorithm not specified" + SP-A.0-AV-pass-K/L "16-hex truncation enables 64-bit collision attacks".

**Rule shape:** Every preflight inventory of authority-chain inputs MUST record the **full SHA-256** (64 hex chars, no truncation) over **raw byte content with no normalisation**. Reference implementation: `hashlib.sha256(open(path, "rb").read()).hexdigest()`. The cert evidence ledger references the full digest. Re-pin checks compare the full digest. Truncated forms are permitted only for human-readable display alongside the full value, never as the comparison primitive. No alternative algorithm (git-hash-object SHA-1, SHA-1, MD5) is acceptable.

**Doctrine target:** new operational rule `O11` in `CLAUDE_CODEX_DOCTRINE.rules.json`; matching prose in `CLAUDE_CODEX_DOCTRINE.md`; conformance row `C9 — Inventory hashes are full SHA-256` added to `conformance-checklist.md`.

---

## R2. Re-pin check + restart-cycle protocol

**Source finding:** SP-A.0-AV-pass-D/E "no closure verification of input SHAs" + pass-F "drift handler ambiguity" + pass-G/H/I "stabilisation window / continuous-restart starvation / cycle definition".

**Rule shape:** Every phase that pins authority-chain SHAs at preflight MUST re-hash all pinned inputs immediately before cert mint. If any digest differs:
- The phase aborts closure.
- The deliverable pipeline reruns end-to-end (inventory regenerated, gap analysis regenerated, every post_phase output regenerated, spec adversarial-review re-run to silent-twice, ship-gate re-run).
- A "restart cycle" counter increments by 1 and is logged in `apex_governance/cc_runbook/state/spawn.log` as `<UTC-iso> RESTART_CYCLE <phase-id> cycle=<N>`.
- The counter is persistent across the phase; it does not reset.
- After **3 consecutive restart cycles** without a drift-free closure, the phase pauses via an incident WO and an upstream-stabilisation WO is dropped (`WO-APEX-<phase>-DRIFT-001`).
- `_scratch/<phase>/` is wiped at the start of every restart cycle to prevent stale data bleed.

**Doctrine target:** new pattern rules `PT6` (re-pin check) and `PT7` (3-cycle escalation) in `.rules.json`; sequence diagram in `CLAUDE_CODEX_DOCTRINE.md`; PHASE_TEMPLATE.md gets a "Re-pin check + restart-cycle handling" section.

---

## R3. Adversarial-review attempt counting + rescue threshold

**Source finding:** SP-A.0-AV-pass-H/I "rescue trigger 'after 5 attempts' lacks definition; what's an attempt; who monitors".

**Rule shape:** An **attempt** = one `codex_bridge.py adversarial-review` invocation against a single target (a single file or a single named bundle). The attempt counter is per-target; counting is by ordered transcript filenames in `apex_governance/codex_runs/<phase>/` for that target. The counter increments on every non-zero `findings=` result and resets on a `findings=0` result OR on a drift-triggered restart that regenerates the target. The 5-attempt threshold (PLAN_CRITERIA §10) fires automatically once 5 consecutive non-zero results are observed; the orchestrator running the bridge calls is responsible for monitoring the counter and invoking `codex_bridge.py rescue` at threshold. Until SP-B.6 supervisor enforcement lands, this is operator/agent discipline, not automation.

**Doctrine target:** clarify `O8` (silent-twice + ship gate); add operational rule `O12` (per-target attempt counting); PHASE_TEMPLATE.md gets a "Stuck-loop policy" subsection citing this rule.

---

## R4. Cert-index atomic write + collision detector

**Source finding:** SP-A.0-AV-pass-E "atomic-write mechanism unspecified" + pass-J "single-writer assumption + concurrent-clobber risk" + pass-L "lock recommendation".

**Rule shape:** `apex_governance/certs/index.json` writes follow a **read-modify-detect-write** contract:
1. Read existing JSON (or initialise empty array if file missing).
2. Hash the existing on-disk content (mtime + sha256).
3. Append new cert row in memory.
4. Write to a sibling temp file.
5. Re-hash the on-disk content; if either mtime or sha256 differs from step 2, abort and drop incident WO `WO-APEX-CERT-INDEX-COLLISION-<n>`.
6. `os.replace()` the temp file over the live file.

This is a **collision detector**, not a full lock. True file-locking is `WO-APEX-CERT-INDEX-LOCK-001` owned by SP-B.6 (supervisor enforcement). Until SP-B.6 lands, the detector ensures unsafe concurrent writes fail safely rather than silently corrupting the index. The single-writer assumption holds at SP-A.0a/SP-A.1 because PLAN_CRITERIA §13 caps concurrent phases at 3 and SP-A.* runs serially.

**Doctrine target:** new operational rule `O13` in `.rules.json`; `PLAN_CRITERIA.md` §7 (Doc control matrix) gets a "Cert index atomic-write contract" appendix; conformance row `C10` added.

---

## R5. Paper-primary phase exemption from QA-doc requirement

**Source finding:** SP-A.0-AV-pass-F + CDX-SP-A.0-014 "PHASE_TEMPLATE expects QA-SP-X.Y.md per phase; paper-primary phases have no test report to author".

**Rule shape:** PHASE_TEMPLATE.md's mandatory `apex/docs/qa/QA-SP-X.Y.md` is **not required** for phases declared "paper-primary" (no production code shipped, no test surface to QA). Paper-primary phases instead record bridge-smoke evidence directly in the cert evidence ledger. The phase's spec MUST declare paper-primary status explicitly; absent declaration, the QA doc is required.

**Doctrine target:** PHASE_TEMPLATE.md "Outputs" section gets a "QA doc — required unless paper-primary declared" line; PLAN_CRITERIA.md §5.4 gets a "paper-primary exemption" subsection.

---

## R6. Deferral protocol (when DoD items can't be satisfied this phase)

**Source finding:** SP-A.0-AV-pass-F + pass-G AV-NEW-003 + CDX-SP-A.0-020 "deferrals (prompt registry, name_enforcer) lack approved waiver mechanism; doctrine A2 + §5.x in tension".

**Rule shape:** When a DoD item cannot be satisfied within a phase because the supporting infrastructure belongs to a later subproject (e.g. SP-A.0 cannot register specs in the prompt registry because SP-B.5 builds the registry), the phase MUST:
1. Log a finding in `findings/<phase>.findings.md` with severity ≥ medium, citing the absorbing SP and the rule that could not be satisfied.
2. Cite the finding in the cert's "deferred DoD items" subsection with explicit rule reference.
3. NOT relax the rule in the spec. Deferral is operational; the rule itself stands.
4. The absorbing SP's cert MUST close every deferral inherited from earlier phases (e.g. SP-B.5 closes by registering all earlier-phase specs retroactively).

This is doctrine A2-compliant: deferred ≠ skipped, as long as the deferral has a tracked closure path with an owning SP.

**Doctrine target:** new pattern rule `PT8` (deferral protocol) + anti-pattern clarification on `A2`; conformance row `C11` (deferrals tracked with absorbing SP) added.

---

## R7. Cleanup-report content categorisation

**Source finding:** SP-A.0-AV-pass-I "cleanup-report 'No files changed' contradicts paper-primary phase that creates docs" + pass-M "spawn-log-append vs created-file ambiguity".

**Rule shape:** `cleanup-report.md` per PLAN_CRITERIA §12.4 lists files in three categories:
- **(a) Created** — files that did not exist before the phase opened.
- **(b) Modified** — files that existed before the phase and received append-only or in-place edits (e.g. `INDEX.md` status flips, `spawn.log` appends, `findings/<phase>.findings.md` row additions).
- **(c) Deleted/renamed/reconciled** — files removed during cleanup (e.g. the codex-unreachable flag, `_scratch/<phase>/` contents) or path-reconciled (legacy `bermi` paths rewritten to `Owner`).

Each category is non-empty or explicitly stated as "none in this category". An empty file is never acceptable.

**Doctrine target:** PLAN_CRITERIA.md §12.4 gets the three-category structure made explicit; PHASE_TEMPLATE.md "Cleanup report" form gets the three subsections.

---

## R8. Repo source-of-truth handling when local working tree is a superset of `origin/main`

**Source finding:** CDX-SP-A.0-008 "local working tree is structural superset of origin/main; PLAN_CRITERIA §0a 'merged-PR per phase' cannot be satisfied conventionally" + RSC-SP-A.0-002 "sys.path UNC injection from network share".

**Rule shape:** When the local working tree is a structural superset of `bermingham85/code-artifacts` `origin/main` (the documented "source of truth"), the per-phase "PR merged to main" DoD CANNOT be satisfied as a small focused PR — naive PR would dump unrelated content. Resolution path:
1. Drop `WO-APEX-REPO-RECONCILE-001` to record the divergence and the migration plan.
2. Each phase that produces local-only artifacts mints a **local cert tag** at `cert/<phase>@<sha>` against the local working tree.
3. The merged-PR DoD is tagged `DEFERRED-RECONCILE` in the cert and inherited by SP-B.4 (CI on code-artifacts) which closes the reconcile by orchestrating a structural sync with origin/main.
4. Until SP-B.4 closes, no phase blocks on PR-merged status; cert tag is the closure signal.

**Doctrine target:** PLAN_CRITERIA.md §0a gets a "DEFERRED-RECONCILE" exception clause; SP-B.4's scope is amended to include the reconcile.

---

## R9. WO naming convention reconciliation

**Source finding:** CDX-SP-A.0-006 "muscle_drop_ticket.py generates UUID-named WOs; runbook prescribes WO-APEX-SP-X.Y-<n>.json; two conventions in active use; name_enforcer.py does not yet cover SP-X.Y format".

**Rule shape:** Two valid WO file-name conventions:
- **Runtime WOs (uuid-named):** `WO-<uuid>.json` in `apex/hub/`. Generated by `muscle_drop_ticket.py`; ephemeral; tracks pipeline runtime tickets.
- **Governance WOs (named):** `WO-APEX-<SCOPE>-<N>.json` in `apex/hub/`. Hand-authored or generated by named-WO helpers; durable; tracks structural/incident/closure WOs.

`name_enforcer.py` MUST recognise both patterns. The two are NOT interchangeable — runtime WOs cannot serve as governance WOs and vice versa. SP-B.2 (`name_enforcer` extension) lands the validator; until then, governance WOs are written directly with the canonical name.

**Doctrine target:** PLAN_CRITERIA.md §7 doc-control matrix gets a "Work Orders" subdivision into runtime vs governance; SP-B.2 scope expanded.

---

## R10. Path absolutism in the runbook

**Source finding:** CDX-SP-A.0-002 + RSC-SP-A.0-003 "runbook cites paths under bare `apex/...` and `apex_governance/...`; literal interpretation does not exist on this filesystem; absolute roots needed; codex_bridge hardcodes Windows-only paths".

**Rule shape:** `00_KICKOFF.md` Step 1, `PROMPT_APEX_INGEST_PIPELINE.md`, and any new doctrine doc MUST cite paths with their absolute roots. The two roots are: `C:\Users\Owner\Repos\code-artifacts\` (containing `apex/`) and `C:\Users\Owner\` (containing `apex_governance/`). Path drift between these roots and bare `apex/`/`apex_governance/` is a doctrine finding, not a stylistic one. Any path reconcile (e.g. legacy `C:\Users\bermi\Projects\apex\`) is logged in `apex_governance/PATH_RECONCILE.log` per PLAN_CRITERIA §0/§12.1.

In parallel: tooling that hardcodes Windows-specific roots (e.g. `codex_bridge.GOVERNANCE_ROOT`) MUST be parameterised via environment variable or config file before SP-B.4 (CI) opens, to allow CI to run on non-Windows or relocated checkouts.

**Doctrine target:** PLAN_CRITERIA.md §0a "Source of truth" section gets a "Path roots" subsection; SP-B.4 scope explicitly covers tooling parameterisation.

---

## R11. Codex bridge hardening contract (for SP-A.1 to satisfy)

**Source finding:** RSC-SP-A.0-005 "codex_bridge background flag ignored, timeout=None; rescue/--background calls block forever" + CDX-SP-A.0-018 "detect_unreachable returns success on parseable JSON regardless of subprocess returncode; partial failure could silent-pass".

**Rule shape:** The codex bridge (`apex_governance/cc_runbook/codex_bridge.py`) is the reviewer-of-record IFF the openai/codex-plugin-cc is unreachable. To qualify as the reviewer, it MUST:
1. Honour the `background` flag with true async (spawn + poll job-id model), or fall back to a documented synchronous mode that is clearly labelled "blocks until codex returns".
2. Enforce a sane subprocess timeout (default 25 minutes for rescue, 5 minutes for review/adversarial-review); on timeout, kill the codex subprocess and return rc=2 with a clear error.
3. Treat success as **(parseable findings JSON) AND (subprocess returncode 0)**, not either alone. Partial-failure outputs (JSON emitted before crash) MUST NOT silent-pass.
4. Auth-mode is `subscription` by default (codex OAuth via `codex login`); `OPENAI_API_KEY` is loaded from env_sync ONLY when `CODEX_AUTH_MODE=apikey` is explicitly set.
5. Capture stdout/stderr as bytes and decode UTF-8 with `errors="replace"` — never let the locale codec (cp1252 on Windows) crash the reader.
6. Write all stdout to operator console with `errors="replace"` encoding too — same cp1252 hazard on the way out.
7. Pass the prompt via stdin (`-`) to dodge the Windows 8191-char command-line limit on detailed specs.
8. Pin codex's working directory to `GOVERNANCE_ROOT` via `-C` so reviews target the prompt's named path, not unrelated files codex finds in the cwd.
9. `_build_review_prompt` inlines the target file content verbatim and instructs codex to review **only** that file.
10. `parse_findings_count` returns -1 (unknown) when no `{"findings":[…]}` JSON is found; the bridge treats `-1 + rc != 0` as failure exit 2, never silent-passes.

Items 4-10 are already implemented in the SP-A.0 working tree. Items 1-3 are open and **constitute SP-A.1's primary scope**.

**Doctrine target:** none directly; this is SP-A.1's spec checklist. Cited here as the policy contribution because the bridge's role as reviewer-of-record is doctrine-bearing (A4: "no Claude self-review fallback when plugin unreachable" implicitly requires a working bridge).

---

## R12. Telegram bot hygiene + memory of working channels

**Source finding:** CDX-SP-A.0-007 + the in-session discovery that `TELEGRAM_BOT_TOKEN` (machine_portable.json) returns 401 while `MBMyPA_BOT_TOKEN` (user_portable.json) works; memory file `reference_env_keys.md` updated.

**Rule shape:** When the runbook prescribes a Telegram notification (e.g. `00_KICKOFF.md` Step 9 programme close, CODEX_BRIDGE.md "Codex unreachable" path), the operator MUST resolve the working bot token via the `reference_env_keys.md` memory **before** consulting `X:\env_sync\machine_portable.json` directly. The memory holds the verified-working channel; env_sync is the raw source. When a token rotates or stops working, the discovery is logged in memory in the same operation that discovers it.

**Doctrine target:** PLAN_CRITERIA.md §8 (Access point matrix) gets a note on Telegram-channel verification preceding env_sync lookup; PROMPT_APEX_INGEST_PIPELINE.md §0 "do not interactively prompt the user" subsection extended to cover bot-token discovery.

---

## R13. Paid-API balance hygiene

**Source finding:** CDX-SP-A.0-009 "ANTHROPIC_API_KEY zero quota; OPENAI_API_KEY was zero-quota at SP-A.0 entry; pattern of depleted accounts".

**Rule shape:** Programme-wide assumption: paid APIs (Anthropic, OpenAI/Codex, ElevenLabs, Suno, Gemini, Flux/Fal, Groq) may be at zero quota at any time. Every phase that is about to consume a paid API MUST run a 1-call balance probe before committing to a long workload. On zero-quota, the phase pauses via the runbook's "API unreachable" path (drop incident WO, Telegram alert, no Claude self-review fallback). Top-ups are an out-of-band human action; the runbook does not retry until balance is restored. Memory `reference_env_keys.md` records each key's last-known balance state and the date.

**Doctrine target:** PLAN_CRITERIA.md §10 (Failure and rollback) gets a "Paid-API zero-quota" subsection; PROMPT_APEX_INGEST_PIPELINE.md §3 "secret/access resolution" extended.

---

## R14. Spec-complexity ceiling for adversarial silent-twice

**Source finding:** the empirical SP-A.0 result itself — 12 passes on a 100-line spec, structurally non-converging.

**Rule shape:** Codex `/codex:adversarial-review` is **structurally non-converging** on detailed specs (>50 lines of operational density). Convergence is reachable only on artifacts the reviewer cannot find a fresh angle on:
- A SHA-pinned inventory of fixed inputs.
- A short binary-verifiable manifest.
- A code diff against a tightly-scoped surface.

Therefore: per-phase specs that aim for silent-twice MUST be ≤30 lines and limited to identity, inputs, outputs, and binary DoD. Any operational detail (locking, drift handling, hashing rules, rescue thresholds, restart cycles, no-deferral rules) goes in **policy docs** (this directory: `apex/docs/policy/`) which are reviewed at doctrine-lock time (e.g. SP-A.2), not at per-phase time. The doctrine lock's silent-twice loop runs against the merged ruleset, not against individual contributions.

This is the meta-rule that makes the rest of this document make sense.

**Doctrine target:** PLAN_CRITERIA.md §3 (Micro-phase lifecycle) gets an explicit "Silent-twice scope" rule restricting per-phase specs to identity/inputs/outputs/DoD; PHASE_TEMPLATE.md gets a "Spec-complexity ceiling" warning at the top; new pattern rule `PT9` in `.rules.json`.

---

## Closure notes

- These 14 rules are SP-A.0b's content. They are the source material for SP-A.2's adversarial-review loop, not artifacts requiring their own loop.
- SP-A.0b's INDEX status stays `IN-PROGRESS-FEEDER` until SP-A.2 closes; at that point SP-A.0b inherits SP-A.2's cert tag by reference and flips to `DONE`.
- Any new rule discovered during SP-A.1 or SP-A.2 that is policy-shaped (not phase-shaped) should be appended to this doc; SP-A.0b stays open as the staging area until SP-A.2 closes.
