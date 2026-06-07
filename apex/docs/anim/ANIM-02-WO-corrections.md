# ANIM-02 — WO `APEX-ANIM-MB-WO-00001` corrections (F4–F6 close-out)

This file records corrections to the operator-owned Work Order surfaced by ANIM-01 and resolved (or staged for the operator) in ANIM-02. APEX does NOT edit the operator-owned WO file at `C:/Users/Owner/Documents/Claude/Projects/breaking down complex tasks/APEX-ANIM-Production-System.md`; corrections are recorded here for operator merge.

## F6 — WO §0 mislabels doctrine R20

**WO §0 quote:** *"Authority: `apex_governance/PLAN_CRITERIA.md` §0 hierarchy, `CLAUDE_CODEX_DOCTRINE` (Codex = reviewer-of-record, no Claude self-review), R20 (no guessing / preserve detail)."*

**Actual R20 (per `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.md` and `.rules.json`):** *"Stuck-loop re-research. When R16 caps fire, before R17 arbiter, automatically re-run internal+external research scoped to the artifact's stuck point. Arbiter receives the re-research output as additional context."*

**Diagnosis:** The WO's intended doctrine concept ("no guessing / preserve detail") is not labelled R20 in the locked doctrine. Closest existing match is the policy intent behind R19 (mandatory pre-flight research) + the foundational P1/P2 ("plan before code"). No existing rule ID maps to the exact phrase "no guessing / preserve detail."

**Resolution options (for operator merge into WO):**
1. **Replace citation** in WO §0: drop the `R20 (no guessing / preserve detail)` parenthetical and cite `R19 (mandatory pre-flight research)` if the intent was about evidence-grounding, or cite `P3 (silent-twice loop)` if it was about review-discipline.
2. **Add new R-rule** to doctrine for "no guessing / preserve detail" (would be `R-future`) and re-mint doctrine v1.0.1 via the SP-A.2 ratification loop.
3. **Drop the citation entirely** — ANIM-01 and ANIM-02 already operate under the spirit of "ground every claim in a file read" regardless of rule ID; the WO need not cite a specific rule for it.

**APEX recommendation:** Option 1, sub-option `R19`. ANIM-01 grounded every map claim in a filesystem read or upstream-JSON quote, which is the R19 internal-research stance applied to a documentation deliverable; matches better than R20 stuck-loop.

**Status:** OPEN_FOR_OPERATOR_REVIEW. Until merged, ANIM-* phases continue to apply the policy spirit regardless of label.

## F4 — `PHASE_STATE.json` claims Grog MP4 is 34.8MB; actual 47.98MB

Resolved by record-only update to PHASE_STATE.json. ANIM-02 does **not** alter the operator-owned `X:/Automations/apex/projects/jesse_animate/PHASE_STATE.json`; this finding is staged for jesse_animate phase 2.x housekeeping. ANIM-02 cert references it as a known-inaccurate input to ANIM-03 pre-flight (use the on-disk file's actual size when planning).

## F5 — WO §4 wrong on FLUX / Wan 2.2 / LTX install status

**Closed in ANIM-01.** ANIM-02 install scope was narrowed to HunyuanVideo + kohya_ss only. The WO §4 sentence *"To add (gated install): FLUX.1 Kontext, Wan 2.2 I2V, LTX-Video, HunyuanVideo, kohya for LoRA training."* should be amended on next WO revision to *"To add (gated install): HunyuanVideo, kohya_ss for LoRA training. (FLUX.1 Kontext, Wan 2.2 I2V, LTX-Video are already installed at C:/ComfyUI/models/ — see CERT-ANIM-01.json:deliverables.)"*

## F1 — Galinda Phase 2.2 sign-off discrepancy

**Deferred to ANIM-03 pre-flight.** ANIM-02 has no authority over Galinda's character-bible state; ANIM-03 reconciles PHASES.md (PENDING) vs PHASE_STATE.json (formally signed off) before reusing galinda as the lead character.

## Provenance

- Source of WO quote: `C:/Users/Owner/Documents/Claude/Projects/breaking down complex tasks/APEX-ANIM-Production-System.md` line 7 (ANIM-01 evidence `wo_quotes.section_0_authority_quote`).
- Source of R20 definition: `C:/Users/Owner/Repos/code-artifacts/apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.rules.json` and verbatim in `CLAUDE_CODEX_DOCTRINE.md` lines 127–128.
- ANIM-01 cert: `C:/Users/Owner/apex_governance/certs/CERT-ANIM-01.json:findings_for_followup[5]`.
