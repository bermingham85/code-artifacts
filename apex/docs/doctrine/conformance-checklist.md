# Doctrine conformance checklist (per phase cert)

> **SUPERSEDED-BY-LOCK 2026-05-25.** The authoritative conformance checklist now lives in `apex/docs/doctrine/APEX_DOCTRINE_v1.0.md` §9 (which incorporates PT6-PT9, O11-O15, R15-R20 and the new C9-C12 rows). This file is retained as historical evidence per `APEX_PARALLEL_MERGE_PLAYBOOK.md` step 5; do NOT paste this table into new certs — use the v1.0 §9 table instead.

Paste this table into every `apex_governance/certs/PHASE-N.codex.md`. Every row must be filled in. Empty rows block the cert.

| Rule ID | Requirement | Evidence (file path / job ID / SHA) | Status |
|---------|-------------|--------------------------------------|--------|
| P1 | Both Claude and Codex used | | |
| P2 | Plan-first time budget honoured (30-90 min, zero code first) | | |
| P3 | Two consecutive empty adversarial runs achieved | | |
| P5 | Codex ship gate executed before any ship action | | |
| PT2 | Adversarial planning loop run on plan | | |
| PT4 | Pre-ship Debbie Downer review on final diff | | |
| PT5 | Full feature cycle followed (plan -> loop -> implement -> rescue -> ship gate) | | |
| O2 | Model + reasoning effort logged for every Codex call | | |
| O3 | --background used for /codex:rescue | | |
| O6 | All transcripts archived | | |
| O7 | Every fix went back through Codex (no batch-skipped findings) | | |
| O8 | Phase advanced only after silent-twice + clean ship gate | | |
| O9 | No automated ship without clean /codex:review on final diff | | |
| C1 | Plan reached two clean consecutive adversarial runs | | |
| C2 | Diff reached two clean consecutive adversarial runs | | |
| C3 | Tests reached two clean consecutive adversarial runs | | |
| C4 | Clean ship gate | | |
| C5 | Models logged | | |
| C6 | --background used where predicted >60s | | |
| C7 | Transcripts archived path | | |
| C8 | Doctrine rule IDs cited beside conformance claims | | |

## Anti-pattern check (all must be NO)

| Rule ID | Anti-pattern | Occurred? (YES/NO) | If YES, remediation cert |
|---------|--------------|---------------------|--------------------------|
| A1 | Solo Claude run shipped without Codex review | | |
| A2 | Findings skipped as minor by Claude | | |
| A3 | Loop closed after one clean adversarial run | | |
| A4 | Fell back to Claude self-review when plugin unreachable | | |
| A5 | Tried to steer /codex:review | | |
| A6 | Ran large rescue in foreground and blocked queue | | |
