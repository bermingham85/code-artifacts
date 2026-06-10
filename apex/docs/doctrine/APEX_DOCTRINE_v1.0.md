# APEX Doctrine v1.0-PROVISIONAL

| Field | Value |
|---|---|
| Ref Code | _allocated at registration via doc_controller (suggested `APEX-MB-DOC-00027`)_ |
| Version | 1.0-PROVISIONAL |
| Status | ACTIVE (binding) — provisional until SP-A.2 silent-twice loop ratifies into 1.0 |
| Authored | 2026-05-25 by Claude (Opus 4.7) per `APEX_PARALLEL_MERGE_PLAYBOOK.md` step 5 |
| Supersedes | `docs/doctrine/CLAUDE_CODEX_DOCTRINE.md` v0.2-draft, `.rules.json` v0.2-draft, `conformance-checklist.md`, `DOCTRINE_v1.0_LOCK_PROPOSAL.md` (proposal), `docs/policy/SP-A.0b-policy-contributions.md` (feeder). Source files retained as evidence, marked SUPERSEDED-BY-LOCK in their headers. |
| Authority | `docs/APEX_CONTEXT_INDEX.md` operating contract (canonical) + `docs/APEX_PARALLEL_MERGE_PLAYBOOK.md` (merge governance) |

## 0. Preamble

This document is the **operationally binding doctrine** for every phase, every work order, every artifact in the APEX programme. Every cert MUST include a "Doctrine conformance" section listing each rule ID and how it was satisfied. The watchdog/supervisor refuses to advance the queue when conformance is missing.

**Conflict precedence (highest first):**
1. `docs/APEX_CONTEXT_INDEX.md` "Operating Contract" section — canonical role split (Claude/Codex/n8n/Make + Git/Apex doc-control). This document paraphrases that contract; the index wording wins on any divergence.
2. This doctrine (v1.0-PROVISIONAL).
3. `docs/APEX_PARALLEL_MERGE_PLAYBOOK.md` conflict-resolution table (for merge-time decisions only).
4. Per-tool guidance (`docs/tools/<tool>/guidance.md`).

**Operational status of v1.0-PROVISIONAL:** binding from this commit forward. SP-A.2 (Doctrine validation + lock v1.0) is the silent-twice loop that ratifies the merged ruleset into v1.0. Until SP-A.2 closes, this doc binds; rule IDs in this doc are the authoritative IDs to cite in conformance checklists.

---

## 1. Foundational principles

| ID | Rule | Severity |
|----|------|----------|
| **P1** | Use both Claude and Codex per the canonical role split in `docs/APEX_CONTEXT_INDEX.md` § Operating Contract. Neither alone wins. Claude owns architecture/reasoning/documentation/review-criteria/signoff; Codex owns local code edits/scripts/tests/config-updates/log-parsing/safe-repair commands. | critical |
| **P2** | Plan before code. Spend 30 to 90 minutes planning per feature. Zero lines of code until the plan survives Codex adversarial review per R15. | high |
| **P3** | Iterate until effectively silent per **R15**. Two consecutive `/codex:adversarial-review` passes with no fresh CRITICAL or HIGH findings AND one clean `/codex:review` ship gate. Medium/low residuals are policy contributions to the absorbing SP, not blockers. | critical |
| **P4** | Codex is enrichment, not replacement. The plugin is a Chrome-extension-style overlay on Claude Code, not a swap. | medium |
| **P5** | Claude is trigger-happy at ship time. A Codex review gate is mandatory before anything ships. | critical |

## 2. Domain strengths (use the right tool for the job)

| ID | Rule | Severity |
|----|------|----------|
| **S1** | Claude excels at copywriting, design thinking, design in general, and certain coding patterns. | info |
| **S2** | Codex is a master surgeon for targeted, numbered, step-by-step changes (1-2-3-4-5 it executes ~9/10). | info |
| **S3** | Codex is more token-efficient on targeted edits than Claude. | info |
| **S4** | Codex is stronger on edge cases, security, privacy, scaling/perf, project hygiene, and second/third-order consequences. | high |
| **S5** | If Claude underperforms on a specific domain, hand the keyboard to Codex (executor mode), not just adviser mode. | medium |

## 3. The four real decisions (mapped to the seven slash commands)

| ID | Rule | Command |
|----|------|---------|
| **D1** | Pure code review (no edit, polite, not steerable) | `/codex:review` |
| **D2** | Adversarial review of a specific plan or diff (steerable, scope-controlled, can use a fresh or existing thread) | `/codex:adversarial-review` |
| **D3** | Holistic full-codebase rescue audit (SWAT team, async, 4-25 minutes typical) | `/codex:rescue` |
| **D4** | Auto-review-every-generation (expensive; reserve for production-sensitive work) | automatic via `/codex:review` |

Supporting commands: `/codex:status`, `/codex:result`, `/codex:cancel`, `/codex:setup`.

**Tool-availability footnote (NEW in v1.0):** when the openai/codex-plugin-cc slash commands are unavailable on a station, the canonical fallback is `apex_governance/cc_runbook/codex_bridge.py` invoked via `claude_codex_loop` (APEX-MB-PY-00023, approved 2026-05-25 by Codex per `hub/WO-APEX-PROMOTE-CLAUDE-CODEX-LOOP-002.json`). Doctrine binds the **behaviour** (severity-filtered ship gate, severity-counted adversarial loop), not the specific command surface.

## 4. The five operating patterns

| ID | Pattern | Severity |
|----|---------|----------|
| **PT1** | Everyday code review pre-ship via `/codex:review`. Polite, broad, not steerable. | high |
| **PT2** | Adversarial planning loop: Claude drafts plan v1 → `/codex:adversarial-review` against plan + relevant path → Claude revises → re-submit → repeat until R15 compound closure. Block forward motion until R15 satisfied. | critical |
| **PT3** | Background rescue in flow state: keep building with Claude; after each meaningful feature, dispatch `/codex:rescue --background`. Poll with `/codex:status`. Read with `/codex:result`. Do not break flow. Integrate findings on the next pass. | high |
| **PT4** | Pre-ship Debbie Downer: before any ship (deck, sheet, app, doc, config, infra change), run `/codex:review` as a hard gate focused on PII, security, privacy, performance under load, second/third-order consequences. Claude does NOT self-clear shipping. | critical |
| **PT5** | Full feature cycle (Mark's daily loop): Plan with Claude → `/codex:adversarial-review` loop until R15 → implement (Claude, or Codex executor where Claude is weak) → `/codex:rescue --background` on the new code → `/codex:review` ship gate → ship. | high |
| **PT6** | **(NEW from R2)** Re-pin check: every phase that pins authority-chain SHAs at preflight MUST re-hash all pinned inputs immediately before cert mint. Any digest mismatch aborts closure and triggers the restart-cycle protocol. | critical |
| **PT7** | **(NEW from R2)** Restart-cycle escalation: on drift detection, the deliverable pipeline reruns end-to-end; `restart_cycle` counter increments and is logged in `apex_governance/cc_runbook/state/spawn.log`. Counter is persistent and does not reset. After **3 consecutive restart cycles** without drift-free closure, drop incident WO `WO-APEX-<phase>-DRIFT-001` and pause the phase. `_scratch/<phase>/` wiped at start of every restart cycle. | critical |
| **PT8** | **(NEW from R6)** Deferral protocol: when a DoD item cannot be satisfied within a phase because the supporting infrastructure belongs to a later SP, the phase MUST log the finding (severity ≥ medium) in `findings/<phase>.findings.md` with absorbing-SP reference, cite it in the cert's "deferred DoD items" subsection, NOT relax the rule in the spec, and the absorbing SP MUST close every deferral inherited from earlier phases. A2-compliant: deferred ≠ skipped iff the deferral has a tracked closure path with an owning SP. | critical |
| **PT8a** | **(NEW from R8 — sub-rule of PT8)** Generic superset-repo handling: when the local working tree is a structural superset of the configured `origin/main`, the per-phase "PR merged to main" DoD cannot be satisfied as a small focused PR. Resolution: each phase mints a local cert tag at `cert/<phase>@<sha>` against the local working tree; merged-PR DoD is tagged `DEFERRED-RECONCILE` and inherited by the SP that owns CI for the repo. Until that SP closes, no phase blocks on PR-merged status; cert tag is the closure signal. | high |
| **PT9** | **(NEW from R14)** Spec-complexity ceiling: per-phase specs that aim for silent-twice MUST be ≤30 lines and limited to identity, inputs, outputs, and binary DoD. Operational detail (locking, drift handling, hashing rules, rescue thresholds, restart cycles, no-deferral rules) goes in `docs/policy/`; the policy material is reviewed at doctrine-lock time, not at per-phase time. The doctrine lock's silent-twice loop runs against the merged ruleset, not against individual contributions. | critical |

## 5. Operational rules

| ID | Rule | Severity |
|----|------|----------|
| **O1** | Always pass the right scope. `--background` for async work; explicit path for adversarial review of a specific plan/diff; explicit model selection where it matters. | high |
| **O2** | Choose the model deliberately. Default for adversarial and rescue: `gpt-5-codex` with high reasoning (or `gpt-5.2` for `codex_bridge.py` per its `CODEX_MODEL=gpt-5.2` convention). Record the model in every cert. Fallback order: `gpt-4.1`, `gpt-4o`. Never silent-fallback without logging. | high |
| **O3** | Async by default for `/codex:rescue`. Audits commonly run 4-25 minutes; never block the queue waiting. | high |
| **O4** | Steerability rules. `/codex:review` is NOT steerable; do not try to focus it. Use `/codex:adversarial-review` for any pinpointed concern. | medium |
| **O5** | Thread reuse. When `/codex:adversarial-review` asks new vs existing thread, choose existing only when continuity adds signal; otherwise new thread for cleanest review. | low |
| **O6** | Persistence (PATH RECONCILED in v1.0). Every Codex run transcript saved to one of two canonical roots: (a) `audit/claude_codex_loop/<phase>/attempt_NN_*.txt` for runs invoked through `claude_codex_loop.py`; (b) `apex_governance/codex_runs/PHASE-N/<job-id>.txt` for direct bridge calls. Both are valid. Phase certs cite the root used. | high |
| **O7** | Loop hygiene. Every revision is itself an artifact and goes back through Codex. No batch-skipping findings as "minor". Severity is set by Codex, not Claude. | critical |
| **O8** | Phase advance gate — superseded by R15 (compound closure signal). Original text retained in `CLAUDE_CODEX_DOCTRINE.md` v0.2 history for audit. Effective rule is R15. | critical |
| **O9** | No automated ship action proceeds without an explicit clean `/codex:review` against the final diff. | critical |
| **O10** | Executor-mode authority. Claude MAY delegate implementation to Codex when Claude is weak on the domain; record the delegation reason in the WO. | medium |
| **O11** | **(NEW from R1)** Full SHA-256 hashing standard. Every preflight inventory of authority-chain inputs MUST record the **full SHA-256** (64 hex chars, no truncation) over raw byte content with no normalisation. Reference: `hashlib.sha256(open(path, "rb").read()).hexdigest()`. Truncated forms permitted only for human-readable display alongside the full value, never as the comparison primitive. No alternative algorithm (git-hash-object SHA-1, SHA-1, MD5) is acceptable. | critical |
| **O12** | **(NEW from R3)** Per-target attempt counting. An "attempt" = one `codex_bridge.py adversarial-review` invocation against a single target (single file or single named bundle). The counter is per-target; counting is by ordered transcript filenames in the configured codex_runs root. Increments on every non-zero `findings=` result; resets on `findings=0` OR on a drift-triggered restart that regenerates the target. The R16 8-pass cap fires when 8 consecutive non-zero results are observed on the same target. | high |
| **O13** | **(NEW from R4)** Cert-index atomic write. `apex_governance/certs/index.json` writes follow read-modify-detect-write: (1) read existing JSON (or initialise empty array); (2) hash on-disk content (mtime + sha256); (3) append cert row in memory; (4) write to sibling temp file; (5) re-hash on-disk content — if mtime or sha256 differs from step 2, abort and drop `WO-APEX-CERT-INDEX-COLLISION-<n>`; (6) `os.replace()` temp over live. Collision detector, not full lock; true file-locking is owned by the supervisor-enforcement SP. | high |
| **O14** | **(NEW from R13)** Paid-API balance hygiene. Programme-wide assumption: paid APIs (Anthropic, OpenAI/Codex, ElevenLabs, Suno, Gemini, Flux/Fal, Groq) may be at zero quota at any time. Every phase about to consume a paid API MUST run a 1-call balance probe before committing to a long workload. On zero-quota: phase pauses via "API unreachable" path (drop incident WO, Telegram alert, no Claude self-review fallback). Top-ups are out-of-band human actions; runbook does not retry until balance is restored. Memory `reference_env_keys.md` records each key's last-known balance state and date. | critical |
| **O15** | **(NEW from R10)** Path absolutism. Doctrine docs and runbook prescripts MUST cite paths with their absolute roots. The two roots are: `C:\Users\Owner\Repos\code-artifacts\` (containing `apex/`) and `C:\Users\Owner\` (containing `apex_governance/`). Path drift between these roots and bare `apex/`/`apex_governance/` is a doctrine finding, not a stylistic one. Any path reconcile (e.g. legacy `C:\Users\bermi\Projects\apex\`) is logged in `apex_governance/PATH_RECONCILE.log`. Tooling that hardcodes Windows-only roots MUST be parameterised via env var or config file before any CI/non-Windows SP opens. | high |

## 6. Economics

| ID | Rule | Severity |
|----|------|----------|
| **E1** | Default stack: $100 Claude Code Max plan + $20 ChatGPT plan covering Codex CLI access. Free ChatGPT tier acceptable for light use; record in cert. | info |
| **E2** | Reserve PT4-style continuous auto-review for production-sensitive work; otherwise it is uneconomic. | medium |
| **E3** | Token-efficient targeted changes go to Codex executor mode rather than Claude. | low |

## 7. Anti-patterns (forbidden)

| ID | Rule | Severity |
|----|------|----------|
| **A1** | Solo Claude runs that ship without Codex review. Forbidden. | critical |
| **A2** | Skipping findings labelled "minor" by Claude. Severity is Codex's call. **PT8 clarification:** deferred ≠ skipped only when the deferral has a tracked closure path with an owning SP per PT8; deferral without that path counts as A2. | high |
| **A3** | Closing the loop after one clean adversarial run. R15 requires the compound signal. | critical |
| **A4** | Falling back to Claude self-review when the Codex plugin is unreachable. Forbidden — supervisor pauses queue. Fallback to `codex_bridge.py` is permitted per the D-section tool-availability footnote; Claude self-review is not. | critical |
| **A5** | Editing or "steering" `/codex:review`. It is not a steerable command. | medium |
| **A6** | Running large rescues in foreground and blocking the queue. | high |

## 8. R-rule amendments (kept in numeric series for traceability)

| ID | Rule | Severity |
|----|------|----------|
| **R15** | Compound closure signal (binding). The phase advance signal is: (a) two consecutive `/codex:adversarial-review` passes with no fresh CRITICAL or HIGH findings — medium/low residuals are policy contributions logged to the absorbing SP, not blockers; AND (b) one clean `/codex:review` ship-gate pass. Adversarial review enumerates angles and is never the literal no-findings gate; ship-gate review is severity-filtered and IS the binding clean-gate. | critical |
| **R16** | Loop caps. Per-artifact adversarial-review cap: 8 passes (see O12 for the counter definition). HIGH-forever signature: 3 consecutive adversarial passes with one or more fresh HIGH or CRITICAL findings (fresh = not a textual or semantic repeat of a finding resolved in the same loop). Per-phase total codex spend cap: 30 calls (configurable in `<gov-root>/cc_runbook/state/phase_budget_SP-X.Y.json`; default 30). Per-phase wall-clock cap: 4 hours of active loop time (excluding async background reviews). Any cap firing pauses iteration and fires R17. | critical |
| **R17** | Arbiter pattern. When R16 caps fire, summon an independent voice that has not seen the loop. Spawn a fresh Claude Code context via the `spawn-context` skill (and optionally a fresh codex thread via the bridge with `--background`) with: artifact at current state, all adversarial transcripts, unresolved HIGH/CRITICAL, the cap that fired. Arbiter prompt asks for exactly one of: (a) structural reshape with concrete diff suggestion; (b) doctrine amendment candidate with rationale (new R-rule); (c) accept-as-is rationale. Output: single JSON at `<gov-root>/findings/SP-X.Y.arbiter.json` with `{proposal_type, proposal, reasoning, confidence}`. In-loop codex then runs `adversarial-review` on the arbiter proposal. If passes R15, apply (edit artifact, amend doctrine, or accept). If fails R15, fire R18. Single-shot per phase. | critical |
| **R18** | Rescue + split. When R17 fails: run `/codex:rescue --background` on the artifact tree, drop a stuck-loop WO, and split the phase per L2 (convergent artifact + policy feeder). Only after R18 fails does the phase go BLOCKED awaiting human direction. | critical |
| **R19** | Mandatory pre-flight research (PATH UPDATED in v1.0). Before any phase writes a spec, run two research layers: **INTERNAL** — scan the user's reachable code repositories for existing/partial implementations. Roots are resolved at runtime via `docs/APEX_REPO_MENU.md` (the canonical repo registry) rather than a hardcoded list. Output: `apex/docs/research/SP-X.Y.internal-research.md` with per-match classification `READY-TO-USE`, `EXTEND`, `REFERENCE-ONLY`, `OBSOLETE-DO-NOT-USE`. **EXTERNAL** — search public catalogs (GitHub, PyPI, npm, HuggingFace Hub, awesome-* lists relevant to topic). Output: `apex/docs/research/SP-X.Y.external-research.md` with rows `{name, url, license, last-commit, stars/downloads, maintained?, fitness-score, decision}`. Decisions: `ADOPT-AS-DEP`, `ADOPT-WITH-FORK`, `STUDY-FOR-PATTERN`, `REJECT-LICENSE`, `REJECT-FITNESS`. **DECISION GATE** — write `apex/docs/research/SP-X.Y.research-decision.md` with one of: `REUSE` (cite artifact; spec becomes a wrapper), `EXTEND` (cite artifact; spec adds delta), `GREENFIELD` (must enumerate rejected candidates with reason — otherwise rejected as un-researched). Decision is codex-reviewed BEFORE spec opens. R19 governed by R15 closure rule. Skipping R19 is a doctrine violation that blocks the cert. | critical |
| **R20** | Stuck-loop re-research. When R16 caps fire, BEFORE R17 arbiter, the runbook automatically re-runs internal+external research scoped to the artifact's specific stuck point (not the whole phase). R17 arbiter receives the re-research output as additional context. Often a stuck loop is "we are inventing a wheel that already exists"; R20 surfaces that without human intervention. | high |

## 9. Conformance checklist (per cert)

Paste this table into every `apex_governance/certs/PHASE-N.codex.md`. Every row must be filled in. Empty rows block the cert.

| Rule ID | Requirement | Evidence (file path / job ID / SHA) | Status |
|---------|-------------|--------------------------------------|--------|
| **P1** | Both Claude and Codex used per the operating-contract role split | | |
| **P2** | Plan-first time budget honoured (30-90 min, zero code first) | | |
| **P5** | Codex ship gate executed before any ship action | | |
| **PT2** | Adversarial planning loop run on plan | | |
| **PT4** | Pre-ship Debbie Downer review on final diff | | |
| **PT5** | Full feature cycle followed (plan → loop → implement → rescue → ship gate) | | |
| **PT6** | Re-pin check executed at phase preflight + immediately before cert mint | | |
| **PT7** | Restart-cycle counter logged (or "none in this phase") | | |
| **PT8** | All deferrals tracked with absorbing SP reference | | |
| **PT9** | Per-phase spec ≤30 lines; operational detail confined to `docs/policy/` | | |
| **O2** | Model + reasoning effort logged for every Codex call | | |
| **O3** | `--background` used for `/codex:rescue` | | |
| **O6** | All transcripts archived (cite root used: claude_codex_loop or governance) | | |
| **O7** | Every fix went back through Codex (no batch-skipped findings) | | |
| **O9** | No automated ship without clean `/codex:review` on final diff | | |
| **O11** | All inventory hashes are full SHA-256 (no truncation) | | |
| **O13** | Cert-index write used the atomic detect-and-replace pattern | | |
| **O14** | Paid-API balance probe ran for every paid-API call (or N/A) | | |
| **O15** | All cited paths use absolute roots `C:\Users\Owner\…` | | |
| **R15** | Compound closure signal satisfied: two clean adversarial passes + one clean ship gate | | |
| **R16** | No R16 cap fired (or arbiter R17 closed it) | | |
| **R19** | INTERNAL + EXTERNAL research + DECISION GATE completed before spec opened | | |
| **C5** (legacy) | Models logged | _superseded by O2_ | |
| **C6** (legacy) | `--background` used where predicted >60s | _absorbed into O3_ | |
| **C7** (legacy) | Transcripts archived path | _superseded by O6_ | |
| **C8** (legacy) | Doctrine rule IDs cited beside conformance claims | _now the structural rule of this table itself_ | |
| **C9** | _(allocated by R1→O11)_ — Inventory hashes are full SHA-256 | | |
| **C10** | _(allocated by R4→O13)_ — Cert-index atomic write contract honoured | | |
| **C11** | _(allocated by R6→PT8)_ — Deferrals tracked with absorbing SP | | |
| **C12** | _(allocated by R13→O14)_ — Paid-API balance hygiene per O14 | | |

### Anti-pattern check (all must be NO)

| Rule ID | Anti-pattern | Occurred? | If YES, remediation cert |
|---------|--------------|-----------|--------------------------|
| **A1** | Solo Claude run shipped without Codex review | | |
| **A2** | Findings skipped as minor by Claude (without PT8 closure path) | | |
| **A3** | Loop closed after one clean adversarial run (R15 violation) | | |
| **A4** | Fell back to Claude self-review when plugin unreachable | | |
| **A5** | Tried to steer `/codex:review` | | |
| **A6** | Ran large rescue in foreground and blocked queue | | |

## 10. Spec-template addenda (referenced by PT9, R5)

These two rules amend the per-phase spec template rather than living in the doctrine body, but are listed here for traceability:

- **Paper-primary exemption (R5):** PHASE_TEMPLATE.md's mandatory `apex/docs/qa/QA-SP-X.Y.md` is NOT required for phases declared "paper-primary" (no production code shipped, no test surface to QA). Paper-primary phases record bridge-smoke evidence directly in the cert evidence ledger. Absent explicit declaration in the phase spec, the QA doc is required.
- **Cleanup-report three-category structure (R7):** `cleanup-report.md` per PLAN_CRITERIA §12.4 lists files in three categories: (a) Created — files that did not exist before the phase opened; (b) Modified — files that existed and received append-only or in-place edits; (c) Deleted/renamed/reconciled — files removed or path-reconciled. Each category is non-empty or explicitly stated as "none in this category". An empty file is never acceptable.

## 11. Doc-control matrix (referenced by R9)

| Object | Pattern | Owner |
|--------|---------|-------|
| Governance WO (durable; structural/incident/closure tracking) | `WO-APEX-<SCOPE>-<N>.json` in `apex/hub/` | Hand-authored or generated by named-WO helpers; `name_enforcer.py` MUST recognise this pattern |
| Runtime WO (ephemeral; pipeline runtime tickets) | `WO-<uuid>.json` in `apex/hub/` | Generated by `muscle_drop_ticket.py`; ephemeral |

The two are NOT interchangeable. Runtime WOs cannot serve as governance WOs and vice versa.

## 12. Items reclassified out of doctrine in v1.0

The following items from `SP-A.0b-policy-contributions.md` were considered for inclusion but reclassified to other surfaces:

- **R11 (Codex bridge hardening contract)** — kept as SP-A.1 spec requirement (the spec's own deliverable checklist), NOT a doctrine rule. The bridge's role as reviewer-of-record is doctrine-bearing (A4 implicitly requires a working bridge), but the specific items 1-3 (background flag, timeout, rc-strict success) are SP-A.1's work product, not amendments to this doctrine. Items 4-10 are already implemented in the current bridge per the source file.
- **R12 (Telegram bot memory)** — moved to runbook hint, not doctrine. Operationally too detailed for doctrine. Lives in `reference_env_keys.md` memory + PLAN_CRITERIA.md §8 (Access point matrix) + PROMPT_APEX_INGEST_PIPELINE.md §0.

## 13. New rules introduced by this lock (per playbook user-instruction: cross-link to playbook)

The following rules are NEW to this lock (not 1-for-1 from v0.2-draft or SP-A.0b):

| New element | Where it lives | Playbook cross-link |
|---|---|---|
| Path-fallback footnote on D1-D4 (`codex_bridge.py` via `claude_codex_loop` when plugin unavailable) | §3 footnote | `APEX_PARALLEL_MERGE_PLAYBOOK.md` § Source Tracks → `registry/claude_codex_loop.py` row ("Promote as an approved orchestration tool") |
| R19 path update (resolve roots via `APEX_REPO_MENU.md`) | §8 R19 body | `APEX_PARALLEL_MERGE_PLAYBOOK.md` § Merge Order step 1 ("Refresh the low-token maps … `generate_repo_menu.py`") |
| Conflict-priority statement: `APEX_CONTEXT_INDEX.md` Operating Contract wins over any divergent doctrine wording (§0) | §0 preamble | `APEX_PARALLEL_MERGE_PLAYBOOK.md` § Conflict Resolution Rules: "Two files claim to be the first context entry → `docs/APEX_CONTEXT_INDEX.md`" |
| O6 dual-path acceptance (`audit/claude_codex_loop/<phase>/` AND `apex_governance/codex_runs/PHASE-N/`) | §5 O6 | `APEX_PARALLEL_MERGE_PLAYBOOK.md` § Conflict Resolution Rules: "Raw transcript conflicts with distilled doc → distilled wins; transcript remains evidence only" |

## 14. Versioning + ratification

- **v0.1** (2026-05-03) — initial draft from Mark's transcript. Source: `docs/doctrine/media/Fu5KIG2Jm1g.transcript.md`.
- **v0.2** (2026-05-04) — R15 amendment after empirical evidence O8/C1-C3 unreachable; R16-R20 added. Provisional until SP-A.2 lock.
- **v1.0-PROVISIONAL** (2026-05-25, this document) — merge lock per `APEX_PARALLEL_MERGE_PLAYBOOK.md` step 5: KEEP/DOWNGRADE verdicts applied to v0.2-draft, SP-A.0b's R1-R14 promoted into the operational/pattern series, source files marked SUPERSEDED-BY-LOCK. Conflict precedence reaffirmed with APEX_CONTEXT_INDEX.md as canonical. Binding from this commit; SP-A.2 silent-twice loop ratifies into v1.0.

This document follows R15 closure semantics for any future amendment: every revision requires Codex adversarial review of the diff plus a clean ship-gate pass. The whole file is itself a doctrine-class artifact subject to SP-A.2's loop.

---

**End of doctrine v1.0-PROVISIONAL.**
