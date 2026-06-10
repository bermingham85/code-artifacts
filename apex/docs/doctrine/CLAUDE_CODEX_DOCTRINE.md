# Claude + Codex Doctrine — APEX governance binding (DRAFT v0.2)

> **SUPERSEDED-BY-LOCK 2026-05-25.** This file's operational role is taken over by `apex/docs/doctrine/APEX_DOCTRINE_v1.0.md` (v1.0-PROVISIONAL). This document is retained as historical evidence per `APEX_PARALLEL_MERGE_PLAYBOOK.md` step 5; it is NOT deleted. Rule IDs in the locked doc are the authoritative IDs to cite in conformance checklists going forward. For the merge verdicts that produced the lock, see `DOCTRINE_v1.0_LOCK_PROPOSAL.md`. SP-A.2 will ratify the locked doc into v1.0 via the silent-twice loop.

Status: DRAFT v0.2 — pending SP-A.2 Codex lock to v1.0. Amended from v0.1 on 2026-05-04 to add R15 (closure-rule amendment) after empirical evidence that O8 / C1-C3 as originally written are operationally unreachable. v0.1 wording retained below as historical anchor; v0.2 wording is operationally binding until SP-A.2 ratifies or rejects.
Source of truth: `docs/doctrine/media/Fu5KIG2Jm1g.transcript.md` (verbatim transcript provided 2026-05-03).

This doctrine is binding for every phase, every WO, every artifact. Every cert must include a "Doctrine conformance" section listing each rule ID and how it was satisfied. The watchdog/supervisor refuses to advance the queue when conformance is missing.

---

## Foundational principles

P1. Use both Claude and Codex. Neither alone wins. Claude builds; Codex audits and stress-tests.
P2. Plan before code. Spend 30 to 90 minutes planning per feature. Zero lines of code until the plan survives Codex.
P3. Loop until effectively silent. Iterate plan and diff through `/codex:adversarial-review` until two consecutive passes return no fresh CRITICAL or HIGH findings (medium/low residuals are policy contributions to the absorbing SP, not spec defects). See R15 for the operational closure rule.
P4. Codex is enrichment, not replacement. The plugin is a Chrome-extension-style overlay on Claude Code, not a swap.
P5. Claude is trigger-happy at ship time. A Codex review gate is mandatory before anything ships.

## Domain strengths (use the right tool for the job)

S1. Claude excels at copywriting, design thinking, design in general, and certain coding patterns.
S2. Codex is a master surgeon for targeted, numbered, step-by-step changes (1-2-3-4-5 it executes ~9/10).
S3. Codex is more token-efficient on targeted edits than Claude.
S4. Codex is stronger on edge cases, security, privacy, scaling/perf, project hygiene, and second/third-order consequences.
S5. If Claude underperforms on a specific domain, hand the keyboard to Codex (executor mode), not just adviser mode.

## The four real decisions (mapped to the seven slash commands)

D1. Pure code review (no edit, polite, not steerable) — `/codex:review`.
D2. Adversarial review of a specific plan or diff (steerable, can pinpoint scope, can use a fresh thread or reuse an existing one) — `/codex:adversarial-review`.
D3. Holistic full-codebase rescue audit (SWAT team, async, 4 to 25 minutes typical) — `/codex:rescue`.
D4. Auto-review-every-generation (expensive; reserve for production-sensitive work) — automatic gate via `/codex:review` on each diff.
Supporting commands: `/codex:status`, `/codex:result`, `/codex:cancel`, `/codex:setup`.

## The five operating patterns

PT1. Everyday code review. Use `/codex:review` on a finished but pre-ship change. Polite, broad, not steerable. Output is read-only feedback.

PT2. Adversarial planning loop. Claude drafts plan v1. `/codex:adversarial-review` against the plan and the relevant path. Claude revises to plan v2. Re-submit. Repeat until Codex is silent. Block forward motion until silent.

PT3. Background rescue in flow state. Keep building with Claude. After each meaningful feature, dispatch `/codex:rescue --background` (or `/codex:adversarial-review --background`). Poll with `/codex:status`. Read with `/codex:result`. Do not break flow waiting on the audit; integrate findings on the next pass.

PT4. Pre-ship Debbie Downer. Before any ship (deck, sheet, app, doc, config, infra change), run `/codex:review` as a hard gate focused on personal data exposure, security, privacy, performance under load, and second/third-order consequences. Claude does not self-clear shipping.

PT5. Full feature cycle (Mark's daily loop). Plan with Claude → `/codex:adversarial-review` loop until silent → implement (Claude, or Codex executor where Claude is weak) → `/codex:rescue --background` on the new code → `/codex:review` ship gate → ship.

## Operational rules

O1. Always pass the right scope. `--background` for async work; explicit path for adversarial review of a specific plan/diff; explicit model selection where it matters.
O2. Choose the model deliberately. `gpt-5-codex` with high reasoning is the default for adversarial and rescue; record the model in every cert. Fall back order: `gpt-4.1`, `gpt-4o`. Never silent-fall-back without logging.
O3. Async by default for `/codex:rescue`. Audits commonly run 4 to 25 minutes; never block the queue waiting.
O4. Steerability rules. `/codex:review` is not steerable; do not try to focus it. Use `/codex:adversarial-review` for any pinpointed concern.
O5. Thread reuse. When `/codex:adversarial-review` asks new vs existing thread, choose existing only when continuity adds signal; otherwise new thread for cleanest review.
O6. Persistence. Every Codex run transcript saved to `apex_governance/codex_runs/PHASE-N/<job-id>.txt`.
O7. Loop hygiene. Every revision is itself an artifact and goes back through Codex. No batch-skipping findings as "minor". Severity is set by Codex, not Claude.
O8. Silent-twice rule (amended by R15). A phase advances on the compound closure signal defined in R15: two consecutive `/codex:adversarial-review` passes with no fresh CRITICAL or HIGH findings, AND one clean `/codex:review` ship gate. Medium/low residuals from the adversarial passes are logged as policy contributions to the absorbing SP, not as blockers.
O9. Trigger-happy mitigation. No automated ship action proceeds without an explicit clean `/codex:review` against the final diff.
O10. Executor mode authority. Claude may delegate implementation to Codex when Claude is weak on the domain; record the delegation reason in the WO.

## Economics

E1. Default stack: $100 Claude Code Max plan + $20 ChatGPT plan covering Codex CLI access. Free ChatGPT tier acceptable for light use; record in cert.
E2. Reserve PT4-style continuous auto-review for production-sensitive work; otherwise it is uneconomic.
E3. Token-efficient targeted changes go to Codex executor mode rather than Claude.

## Anti-patterns (forbidden)

A1. Solo Claude runs that ship without Codex review. Forbidden.
A2. Skipping findings labeled "minor" by Claude. Severity is Codex's call.
A3. Closing the loop after one clean adversarial run. Two consecutive clean runs required.
A4. Falling back to Claude self-review when the Codex plugin is unreachable. Forbidden — supervisor pauses queue.
A5. Editing or "steering" `/codex:review`. It is not a steerable command.
A6. Running large rescues in foreground and blocking the queue.

## Conformance checklist (per cert)

C1. Plan went through `/codex:adversarial-review` to effective silence per R15 (two consecutive passes, no fresh CRITICAL or HIGH findings; medium/low residuals carried to absorbing SP).
C2. Diff went through `/codex:adversarial-review` to effective silence per R15.
C3. Tests went through `/codex:adversarial-review` to effective silence per R15.
C4. Final `/codex:review` ship gate clean.
C5. Model and reasoning effort logged for every Codex call.
C6. Background flag used for any review predicted to exceed 60 seconds.
C7. All transcripts archived under `apex_governance/codex_runs/PHASE-N/`.
C8. Doctrine rule IDs cited next to every conformance claim in the cert.

---

## R-rules — empirical amendments accumulated during dogfooding

R15. Closure-rule amendment (added v0.2, 2026-05-04). The original O8 / C1-C3 "two consecutive empty adversarial runs" is operationally unreachable on any artifact with non-zero operational density, because `/codex:adversarial-review` enumerates angles rather than filtering by severity; a competent reviewer can always find another angle. The compound closure signal that actually fires on real artifacts is:

- (a) Two consecutive `/codex:adversarial-review` passes return no fresh CRITICAL or HIGH findings. Medium/low findings are accepted as policy contributions and logged to the absorbing subproject's policy file (not as blockers on the current phase).
- (b) One clean `/codex:review` ship-gate pass (D1 mode is severity-filtered and IS reachable; this is the ship-gate Mark's video describes as the trigger-happy mitigation).

The ship-gate `/codex:review` is the binding clean-gate. Adversarial review is the angle-finder feeding doctrine; it is never the literal "no findings" gate. R15 binds operationally from v0.2 forward; SP-A.2 will ratify into v1.0.

R16. Loop caps and HIGH-forever definition (added v0.2). Concrete bounds so the loop cannot run unbounded:

- Per-artifact adversarial-review cap: 8 passes. After pass 8 the artifact must close on R15 compound signal or escalate to R17 arbiter.
- HIGH-forever signature: 3 consecutive adversarial passes that produce one or more fresh HIGH or CRITICAL findings (where "fresh" means not a textual or semantic repeat of a finding already resolved in the same loop). Trigger R17 arbiter at the third such pass.
- Per-phase total codex spend cap: 30 calls (adversarial + ship-gate + rescue + bridge calls combined). Hitting the cap fires R17. The cap is configurable per phase in `<gov-root>/cc_runbook/state/phase_budget_SP-X.Y.json`; default 30.
- Per-phase wall-clock cap: 4 hours of active loop time (not including async background reviews). The watchdog enforces; on breach, fires R17.

Any cap firing pauses adversarial iteration on that artifact until R17 returns.

R17. Arbiter pattern (added v0.2). When any R16 cap fires, summon an independent voice that has not seen the loop:

- Spawn a fresh Claude Code context via the `spawn-context` skill (and optionally a fresh codex thread via the bridge with `--background`) with: the artifact at its current state; all adversarial-review transcripts from the loop; the HIGH/CRITICAL findings that have not been resolvable; the cap that fired.
- Arbiter prompt asks for exactly one of: (a) structural reshape of the artifact (concrete diff suggestion); (b) doctrine amendment candidate (new R-rule with rationale); (c) accept-as-is rationale (why the current state should ship despite findings).
- Arbiter output is a single JSON file at `<gov-root>/findings/SP-X.Y.arbiter.json` with `{proposal_type, proposal, reasoning, confidence}`.
- The in-loop codex then runs `adversarial-review` on the arbiter proposal itself. If the proposal passes R15, apply it (edit the artifact, amend doctrine, or accept). If the proposal also fails R15, fire R18.
- Arbiter is single-shot per phase. A second cap-fire goes straight to R18.

R18. Rescue + split (existing escalation, codified). When R17 fails: run `/codex:rescue --background` on the artifact tree, drop a stuck-loop WO, and split the phase per L2 (Option B pattern: convergent artifact + policy feeder). Only after R18 fails does the phase go BLOCKED awaiting human direction.

R19. Mandatory pre-flight research (added v0.2). Before any phase writes a spec, run two research layers and produce decisions:

- INTERNAL research — scan the user's reachable code repositories for existing or partial implementations of the phase's scope. Roots to cover at minimum: `C:\Users\Owner\Repos\`, `C:\Users\Owner\Projects\`, `X:\GitHub\`, `X:\Projects\`, `X:\Automations\`, `X:\Bermech\`, `X:\Workspace\`, `X:\Claude\`, plus any subproject's named muscles under `apex/registry/`. Output: `apex/docs/research/SP-X.Y.internal-research.md` with classification per match: `READY-TO-USE`, `EXTEND`, `REFERENCE-ONLY`, `OBSOLETE-DO-NOT-USE`.
- EXTERNAL research — search public catalogs for prior art with compatible licenses. Catalogs to cover at minimum: GitHub repo search, PyPI, npm, HuggingFace Hub, awesome-* curated lists relevant to the topic. Output: `apex/docs/research/SP-X.Y.external-research.md` with rows `{name, url, license, last-commit, stars/downloads, maintained?, fitness-score, decision}`. Decisions are: `ADOPT-AS-DEP`, `ADOPT-WITH-FORK`, `STUDY-FOR-PATTERN`, `REJECT-LICENSE`, `REJECT-FITNESS`.
- DECISION GATE — write `apex/docs/research/SP-X.Y.research-decision.md` with one of: `REUSE` (cite the artifact, spec becomes a wrapper), `EXTEND` (cite the artifact, spec adds delta), `GREENFIELD` (justify; cite the negative search results that ruled out reuse). The decision file is reviewed by the in-loop codex BEFORE the spec is written. A GREENFIELD decision must enumerate the rejected candidates with reason; otherwise it is rejected as un-researched.

The research stage is governed by the same R15 closure rule: two passes with no fresh HIGH/CRITICAL on the decision file, plus a clean ship-gate review on the bundle. Research findings are not blockers; the decision IS the gate.

R19 cuts iteration count by surfacing prior solutions before the loop opens. Skipping R19 is a doctrine violation that blocks the cert.

R20. Stuck-loop re-research (added v0.2). When R16 caps fire (before R17 arbiter), the runbook automatically re-runs internal+external research scoped to the artifact's specific stuck point — not the whole phase. The arbiter (R17) receives the re-research output as additional context. Often a stuck loop is "we are inventing a wheel that already exists"; R20 surfaces that without human intervention.

R-future. Additional R-rules accumulate here as later phases discover operational truths. Each R-rule is a candidate for inclusion at the next doctrine lock.

---

## Versioning

This doctrine is versioned in the prompt document control system. Edits require a new version, a Codex adversarial review of the diff, and a fresh ship-gate pass. Old versions are retained for audit.

Version log:
- v0.1 (2026-05-03) — initial draft from Mark's transcript.
- v0.2 (2026-05-04) — R15 amendment after empirical evidence O8/C1-C3 unreachable. Provisional until SP-A.2 lock.
