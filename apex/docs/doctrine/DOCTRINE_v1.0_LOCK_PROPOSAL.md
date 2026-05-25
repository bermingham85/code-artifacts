# Doctrine v1.0 Lock — Merge Proposal (Claude-drafted, awaiting Codex review)

| Field | Value |
|---|---|
| Ref Code | _PROPOSED — Codex to allocate via doc_controller (suggest `APEX-MB-DOC-00027`)_ |
| Version | 1.0-PROPOSAL |
| Status | DRAFT — under Codex review |
| Authored | 2026-05-25 by Claude (Opus 4.7) per APEX_PARALLEL_MERGE_PLAYBOOK step 5 |
| Source proposal | This file |
| Source rules | `docs/doctrine/CLAUDE_CODEX_DOCTRINE.md` v0.2-draft (binding) + `docs/doctrine/CLAUDE_CODEX_DOCTRINE.rules.json` v0.2-draft + `docs/doctrine/conformance-checklist.md` + `docs/policy/SP-A.0b-policy-contributions.md` (R1–R14 candidates) |
| Authority | `docs/APEX_PARALLEL_MERGE_PLAYBOOK.md` step 5 (controlling) + `docs/APEX_CONTEXT_INDEX.md` operating contract (canonical) |

## What this document is

A per-rule verdict on the existing doctrine package + the SP-A.0b policy contributions, deciding which to KEEP, DOWNGRADE, or REJECT in the merged v1.0 lock. **This is a proposal.** The locked doctrine doc is NOT written here — Codex reviews the verdicts, then either Codex or a follow-up Claude turn writes the locked doc.

Per APEX_PARALLEL_MERGE_PLAYBOOK conflict resolution: existing CLAUDE_CODEX_DOCTRINE.md is the structured input; SP-A.0b is the policy feeder; APEX_CONTEXT_INDEX operating contract is the canonical role-split statement and overrides on conflict.

Per user instruction 2026-05-25 14:16Z: any **new** rule introduced by this merge cross-links to `APEX_PARALLEL_MERGE_PLAYBOOK.md`.

---

## Part A — Existing CLAUDE_CODEX_DOCTRINE.md v0.2-draft

### Foundational principles P1–P5

| Rule | Verdict | Rationale |
|---|---|---|
| **P1** Use both Claude and Codex | **KEEP** as-is. Aligns with APEX_CONTEXT_INDEX operating contract (Claude / Codex / n8n split). |
| **P2** Plan before code (30–90 min) | **KEEP** as-is. Captures the "no Claude self-review" intent. |
| **P3** Iterate until effectively silent per R15 | **KEEP** as-is — R15 already amended it. |
| **P4** Codex enriches, doesn't replace | **KEEP** as-is. |
| **P5** Claude is trigger-happy; Codex gate mandatory | **KEEP** as-is. Critical for the operating contract. |

### Strengths S1–S5

| Rule | Verdict | Rationale |
|---|---|---|
| **S1–S5** | **KEEP all** as-is. Informational; describe domain routing. No contradictions with the contract. |

### Decisions D1–D4 (slash-command mappings)

| Rule | Verdict | Rationale + Action |
|---|---|---|
| **D1** Pure code review → `/codex:review` | **KEEP with footnote.** When openai/codex-plugin-cc unavailable, `codex_bridge.py review` is the fallback (per R11 + A4 implicit). |
| **D2** Adversarial review → `/codex:adversarial-review` | **KEEP with footnote.** Fallback: `codex_bridge.py review --phase ...` (the existing bridge IS this command path). |
| **D3** Rescue → `/codex:rescue` (async) | **KEEP with footnote.** Fallback: `codex_bridge.py rescue --background` once R11 items 1–3 (background flag + timeout + rc-strict success) land in SP-A.1. |
| **D4** Continuous auto-review | **KEEP** as-is. Aligned with E2 (reserve for prod-sensitive). |

**Action:** add a single footnote section after D1–D4 in the locked doctrine: "When the slash-command plugin is unavailable on a station, the canonical fallback is `codex_bridge.py` via `claude_codex_loop` (APEX-MB-PY-00023). The doctrine binds the BEHAVIOUR, not the specific command surface."

### Patterns PT1–PT5

| Rule | Verdict | Rationale |
|---|---|---|
| **PT1–PT5** | **KEEP all** as-is. Patterns are tool-agnostic. The D1–D4 footnote covers any tool-availability gap. |

### Operational rules O1–O10

| Rule | Verdict | Rationale + Action |
|---|---|---|
| **O1** Pass right scope | **KEEP** as-is. |
| **O2** Model selection deliberate | **KEEP** as-is. Critical for cost + audit. |
| **O3** Async by default for rescue | **KEEP** as-is. Reinforced by R11. |
| **O4** Steerability rules | **KEEP** as-is. |
| **O5** Thread reuse | **KEEP** as-is. |
| **O6** Persistence path | **DOWNGRADE-AND-RECONCILE.** Current text says `apex_governance/codex_runs/PHASE-N/<job-id>.txt`. The active audit layout is `audit/claude_codex_loop/<phase>/attempt_NN_*.txt`. **Action:** locked doctrine accepts BOTH paths — prefer `audit/claude_codex_loop/<phase>/` for runs invoked through `claude_codex_loop.py`; keep `apex_governance/codex_runs/PHASE-N/` for direct bridge calls. Cross-link to playbook conflict rule "Troubleshooting fix appears in chat or audit only → move to `docs/tools/<tool>/troubleshoot.md`." |
| **O7** Loop hygiene (no batch-skip) | **KEEP** as-is. |
| **O8** Silent-twice rule (amended by R15) | **KEEP** as amended. R15 is the operationally-binding form. |
| **O9** No automated ship without clean review | **KEEP** as-is. |
| **O10** Executor mode delegation | **KEEP** as-is. Aligned with operating-contract role split. |

### Economics E1–E3

| Rule | Verdict | Rationale |
|---|---|---|
| **E1** Default stack | **KEEP** as-is. |
| **E2** Reserve PT4 for prod-sensitive | **KEEP** as-is. |
| **E3** Token efficiency → Codex executor | **KEEP** as-is. |

### Anti-patterns A1–A6

| Rule | Verdict | Rationale |
|---|---|---|
| **A1–A6** | **KEEP all** as-is. Critical guardrails. Especially A4 ("no Claude self-review fallback when plugin unreachable") — this is what the user just re-emphasised: "Do not self-review around Codex where Codex review is required." |

### Conformance C1–C8

| Rule | Verdict | Rationale |
|---|---|---|
| **C1–C8** | **KEEP all** as amended. R15 already retargets C1–C3 at the compound closure signal. |

### R-rule amendments R15–R20

| Rule | Verdict | Rationale |
|---|---|---|
| **R15** Compound closure signal | **KEEP** as the binding closure rule. The v0.2 amendment was correct and remains operationally-load-bearing. |
| **R16** Loop caps | **KEEP** as-is. Bounded retry semantics — critical safety property. |
| **R17** Arbiter pattern | **KEEP** as-is. Single-shot per phase. |
| **R18** Rescue + split | **KEEP** as-is. |
| **R19** Mandatory pre-flight research | **KEEP** with PATH UPDATE. Internal research roots in R19 reference legacy paths (`X:\GitHub\`, `X:\Projects\`). Locked doctrine: revise to the current path set per R10 (i.e. resolve via `APEX_REPO_MENU.md` rather than hardcoded list). Cross-link to playbook step 1 ("Refresh the low-token maps"). |
| **R20** Stuck-loop re-research | **KEEP** as-is. |

---

## Part B — SP-A.0b policy contributions (R1–R14)

| # | Verdict | New ID in locked doctrine | Notes / Cross-links |
|---|---|---|---|
| **R1** Full SHA-256 hashing | **KEEP** | **O11** | Universal, no platform dep. Adds conformance row `C9`. Cross-link: `APEX_PARALLEL_MERGE_PLAYBOOK.md` conflict rule "WIP script useful but undocumented" — hashing IS how `claude_codex_loop` already detects drift. |
| **R2** Re-pin check + restart-cycle | **KEEP** | **PT6** (re-pin check) + **PT7** (3-cycle escalation) | Concrete mechanism for drift detection. |
| **R3** Per-target attempt counting | **KEEP** | **O12** | Aligns with R16 cap (8 passes per artifact). Disambiguates "attempt." |
| **R4** Cert-index atomic write | **KEEP** | **O13** + conformance row `C10` | Until SP-B.6 supervisor enforcement lands. Implementation pattern is read-modify-detect-write. |
| **R5** Paper-primary phase exemption | **KEEP** as configurable | _spec-template addition_ | Phase spec must DECLARE paper-primary explicitly to claim the exemption. |
| **R6** Deferral protocol | **KEEP** | **PT8** + clarifies A2 | Conformance row `C11`. Required for the playbook's batch 5 (SP-A specs as history). |
| **R7** Cleanup-report 3 categories | **KEEP** | _phase-template addition_ | Phase template change only — not a new rule slot. |
| **R8** Superset repo handling | **DOWNGRADE-AND-GENERALISE** | **PT8a** (sub-rule of PT8 deferral) | R8 names `bermingham85/code-artifacts` specifically. Locked doctrine: replace with generic "when local working tree is a structural superset of the configured `origin/main`, follow the deferred-reconcile pattern PT8." Cross-link to playbook conflict rule "Two files claim to be the first context entry → `docs/APEX_CONTEXT_INDEX.md`." |
| **R9** WO naming reconciliation | **KEEP** | _doc-control matrix addition_ | Runtime vs governance WOs. Cross-link to playbook batch 4 (active hub/WO-APEX-*.json). |
| **R10** Path absolutism | **KEEP** | **O15** + cross-cuts R19 | Adopt as universal rule: doctrine docs use absolute roots `C:\Users\Owner\Repos\code-artifacts\` and `C:\Users\Owner\`. Cross-link to playbook step 1 "refresh maps." |
| **R11** Codex bridge hardening contract | **KEEP-AS-SPEC** (not doctrine) | _SP-A.1 spec requirement_ | R11 itself says "Doctrine target: none directly." Lock the items 1–3 as SP-A.1 deliverables; items 4–10 already implemented (per the source file). |
| **R12** Telegram bot memory | **DOWNGRADE** | _runbook hint, not doctrine_ | Too operational for doctrine. Lives in `reference_env_keys.md` memory + the runbook. Cross-link: APEX_CONTEXT_INDEX security boundary. |
| **R13** Paid-API balance hygiene | **KEEP** | **O14** + conformance row `C12` | Critical safety. Programme-wide assumption that paid APIs may be zero-quota at any time. **NEW RULE** — cross-link to `APEX_PARALLEL_MERGE_PLAYBOOK.md` conflict rule "Raw transcript conflicts with distilled doc → distilled wins" (memory `reference_env_keys.md` is the distilled, env_sync is the raw). |
| **R14** Spec-complexity ceiling | **KEEP** | **PT9** | The meta-rule. Per-phase spec ≤ 30 lines; operational detail goes in `docs/policy/`. Critical for making silent-twice reachable. |

---

## Part C — Conflict resolution against APEX_CONTEXT_INDEX operating contract

| Doctrine claim | Index claim | Resolved as |
|---|---|---|
| "Claude builds; Codex audits and stress-tests" (P1) | "Claude owns architecture, reasoning, documentation, review criteria, and signoff. Codex owns local code edits, scripts, tests, config updates, log parsing, and safe repair commands." | **INDEX WINS.** Index is broader and now-canonical (added 2026-05-25). Doctrine v1.0 lock adopts the index wording as the canonical statement; P1 becomes a paraphrase pointing at the index. |
| "Claude does not self-clear shipping" (PT4) | "no Claude self-review fallback when Codex review is required" (user instruction 2026-05-25 14:16Z) | **AGREEMENT** — both forbid Claude self-clearance. |
| `apex_governance/codex_runs/` paths (O6, C7) | `audit/claude_codex_loop/` paths (current audit tree) | **BOTH ACCEPTED** — see O6 verdict above. |

---

## Part D — Items deferred from this lock

Per playbook step 5: "Downgrade or rewrite any rule that depends on unavailable plugins, impossible 'silent forever' gates, unlimited token spend, or private local paths."

- The `openai/codex-plugin-cc` slash commands D1–D4: NOT downgraded (already covered by codex_bridge fallback footnote). Verifies on this station per existing audit transcripts.
- "Silent forever" gate: NOT downgraded (R15 already replaced it with R15 compound closure).
- "Unlimited token spend": NOT downgraded (R16 caps already in place; R13/O14 paid-API hygiene already keeps).
- "Private local paths": HANDLED by R10/O15 (path absolutism) + R19 path update (resolve via `APEX_REPO_MENU.md` instead of hardcoded list).

## Part E — New rules introduced by this merge (cross-linked to playbook per user instruction)

The following rules are NEW to the locked doctrine (not present in v0.2-draft and not 1-for-1 from SP-A.0b):

| New rule | Where it lives | Playbook cross-link |
|---|---|---|
| _Path-fallback footnote on D1–D4_ | `D-section footnote` | playbook §"Source Tracks" → `registry/claude_codex_loop.py` row ("Promote as an approved orchestration tool") |
| _R19 path update — resolve via APEX_REPO_MENU_ | `R19` body | playbook §"Merge Order" step 1 ("Refresh the low-token maps … `generate_repo_menu.py`") |
| _Conflict-priority statement: APEX_CONTEXT_INDEX operating contract wins over P1 wording_ | doctrine preamble | playbook §"Conflict Resolution Rules" — "Two files claim to be the first context entry → `docs/APEX_CONTEXT_INDEX.md`" |

## Completion conditions for the v1.0 lock (after Codex review)

The locked doctrine doc (not this proposal) is complete when:

1. Codex has reviewed each verdict in this proposal and flagged any disagreement.
2. The locked doctrine doc (path TBD — proposed `docs/doctrine/APEX_DOCTRINE_v1.0.md`) is written incorporating the KEEP / KEEP-with-mod verdicts above.
3. The source files (`CLAUDE_CODEX_DOCTRINE.md`, `.rules.json`, `conformance-checklist.md`, `SP-A.0b-policy-contributions.md`) are marked SUPERSEDED-BY-LOCK in their headers but NOT deleted (evidence preservation, per playbook).
4. The locked doctrine doc is registered in `docs/DOCUMENT_REGISTER.md` with an allocated ref code.
5. `docs/APEX_CONTEXT_INDEX.md` "Current Governed Foundation" table gets a new row for the locked doctrine.
6. `python registry/validate_tool_docs.py --quiet` returns OK after the register edit.
7. (Per SP-A.2 framing in `CLAUDE_CODEX_DOCTRINE.md` line 138) — the merged ruleset undergoes a silent-twice loop AT SP-A.2; until then it is operationally binding as v1.0-PROVISIONAL.

## What this proposal does NOT do

- Does NOT touch batch 1 (`muscle_compliance_check.py`) or batch 2 (`claude_codex_loop.py`) artifacts.
- Does NOT mark anything APPROVED.
- Does NOT delete the source files.
- Does NOT bulk-merge raw audit folders or transcripts.
- Does NOT stage OCR / receipt data.
- Does NOT write the locked doctrine doc itself (Codex review first).
