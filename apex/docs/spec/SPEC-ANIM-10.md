# SPEC-ANIM-10 — AGEN-Specification agent: verbatim recovery from codex transcript

**Phase:** ANIM-10 of `APEX-ANIM-MB-WO-00001`
**Parent subproject:** SP-ANIM
**Depends-on:** ANIM-08 (extractor APEX-MB-PY-00116)
**Issued:** 2026-06-07
**Branch:** `phase/ANIM-10-AGEN-specification` (branched from `phase/ANIM-09-AGEN-builder@ea50fef`)
**Reference patterns followed:** R15 silent-twice, R19 REUSE of extractor, R20 verbatim recovery, ANIM-08/ANIM-09 precedent.

---

## 1. Objective

Restore the **full 5-artifact** AGEN-Specification agent set to `AGENT_BUILD_SYSTEM/03_SPECIFICATION_AGENT/` verbatim from the latest 2026-05-05 Codex review transcript at `apex_governance/codex_runs/agen-spec-build/agen-spec-build-review-20260505T043244Z-d5b8c121.txt`. Per shared memory the full Specification artifact set is inline-recoverable from this single transcript (unlike Builder which required two sources and was missing SPEC).

## 2. Pre-flight findings

- Live path `AGENT_BUILD_SYSTEM/03_SPECIFICATION_AGENT/` had only `HANDOVER.md` + `PROJECT_INSTRUCTIONS.md` before this phase (mtime 2026-04-19). Mirrors ANIM-08/09 pre-state.
- 35 transcripts under `apex_governance/codex_runs/agen-spec-build/`: 28 `*-adv-*` (advisory; no `=== FILE: ===` markers) + 7 `*-review-*` (review; markers present).
- Latest review transcript (`d5b8c121`, 2026-05-05T04:32:44Z) inlines all 5 artifacts between `=== FILE: ===` markers: WKFL (45,237 B) + PRMPT (13,300 B) + SPEC (16,828 B) + TEST (14,126 B) + SCRPT (24,449 B).
- Marker balance verified: 5 `=== FILE: ` / 5 `=== END FILE ===`.
- **MA-AGEN-002 residual** (per shared memory + MISSING_SECRETS queue): the agen-spec-build review-loop closed with 2 open findings (F-001 workflow prompt drift; F-002 T5 non-determinism). These findings DO NOT block ANIM-10 restore-correctness; they are pre-existing review findings on the artifacts themselves and remain operator-actionable per the existing MA-AGEN-002 entry.

## 3. Scope (in / out)

In scope:
- Extract 5 artifacts byte-for-byte from `d5b8c121` transcript. Write to `AGENT_BUILD_SYSTEM/03_SPECIFICATION_AGENT/`.
- Verify WKFL JSON parses; report node count.
- Write `apex/docs/agen/ANIM-10-recovery-evidence.json` (per-file provenance).
- Restore audit + idempotency-rerun audit under `apex/audit/anim-10/`.
- Carry MA-AGEN-002 forward verbatim — do not re-litigate F-001/F-002 in this phase.

Out of scope:
- `HANDOVER.md` and `PROJECT_INSTRUCTIONS.md`: already present, untouched.
- Re-running the AGEN-Specification codex review loop on restored inputs (silent-twice rearm) — operator decision.
- F-001 / F-002 resolution — covered by existing MA-AGEN-002; restoration of artifacts as-was is the WO §3 mandate (verbatim recovery, not invention).
- Extractor modifications — APEX-MB-PY-00116 stays frozen.

## 4. Access matrix

| Resource | Path | RW | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-10-AGEN-specification` | RW | env_sync GitHub PAT |
| Live AGEN dir | `C:/Users/Owner/Repos/code-artifacts/AGENT_BUILD_SYSTEM/03_SPECIFICATION_AGENT/` | RW | local |
| Codex transcript | `C:/Users/Owner/apex_governance/codex_runs/agen-spec-build/agen-spec-build-review-20260505T043244Z-d5b8c121.txt` (sha256 `94929417…`, 119,756 B) | R | local |
| Codex CLI | `codex` (gpt-5.5, ChatGPT auth) | RW | shell PATH |

## 5. Inputs (with SHAs)

- Transcript: 119,756 B, sha256 `94929417c8ec150c60c8d880378438466cf077e98b8cd57cc6593deae7d5ce95`.
- Live `HANDOVER.md` + `PROJECT_INSTRUCTIONS.md`: preserved (mtime 2026-04-19).
- Extractor: `apex/registry/agen_recovery_extract.py` (APEX-MB-PY-00116), unchanged.

## 6. Outputs

- 5 new files at `AGENT_BUILD_SYSTEM/03_SPECIFICATION_AGENT/`.
- `apex/docs/agen/ANIM-10-recovery-evidence.json`.
- `apex/audit/anim-10/spec-restore-2026-06-07T10-15-00Z.json` (extractor stdout JSON; current state is `no_op_idempotent×5` because the bytes were written by the same call's first run — see §13 cleanup note).
- `apex/audit/anim-10/spec-idempotency-rerun-2026-06-07T10-17-00Z.json` (explicit second rerun proving 5/5 `no_op_idempotent`).
- `apex/docs/spec/SPEC-ANIM-10.md` (this file).
- `apex_governance/handovers/ANIM-10.handover.md`.
- `apex_governance/certs/CERT-ANIM-10.json` + index update.
- `apex_governance/codex_runs/ANIM-10/round*.txt`.

## 7. Definition of Done

- 5 byte-exact restores; WKFL parses; per-file SHA256s recorded.
- Recovery evidence + restore + idempotency-rerun audits committed.
- MA-AGEN-002 still tracked as OPEN; not closed.
- Codex silent-twice + ship-gate clean.
- Cert + handover + PR opened.

## 8. Codex commands

`CODEX_MODEL=gpt-5.5 codex exec --model gpt-5.5 < bundle.txt > round<n>.txt` per ANIM-09 pattern.

## 9. Test plan

- WKFL parses as JSON; node count ≥ 30.
- Per-file sha256 equals transcript byte-slice sha256 (extractor BYTE-MODE invariant).
- Idempotency rerun = 5/5 `no_op_idempotent`.
- Path-escape closure (inherited from extractor; not re-exercised).

## 10. Pass criteria (binary)

- [ ] 5 files restored at byte-exact size.
- [ ] WKFL parses; nodes reported.
- [ ] Evidence cites transcript SHA.
- [ ] Idempotency rerun all-no_op.
- [ ] MA-AGEN-002 untouched (still OPEN).
- [ ] Silent-twice + ship-gate clean.
- [ ] Cert + handover + PR opened.

## 11. Rollback plan

Additive only; HANDOVER + PROJECT_INSTRUCTIONS untouched. `git revert <commit>` safe.

## 12. Doctrine conformance table

Filled at cert time. R15 (silent-twice), R19 (REUSE extractor), R20 (verbatim BYTE-MODE), P1/P2, O2 (`gpt-5.5`), O6 (transcripts persisted).

## 13. Cleanup report

- Files deleted: none.
- Files renamed: none.
- Paths reconciled: transcript `=== FILE: ===` headers reference `apex/registry/clones/...` deprecated path; extractor writes to live path; documented in evidence.
- Stubs/TODOs: none introduced.
- Sandbox/Scratch dirs: not used.
- Audit-file note: `spec-restore-2026-06-07T10-15-00Z.json` was generated by a single extractor call after the live dir already had the files (because the first invocation in this session wrote them before the redirect target path-resolution issue showed up on a separate JSON-parse step; the bytes themselves landed on disk). The audit therefore shows 5×`no_op_idempotent` rather than 5×`write`. This is functionally equivalent evidence: the byte-identity match is the same proof either way (transcript slice SHA == on-disk SHA). The explicit second rerun `spec-idempotency-rerun-2026-06-07T10-17-00Z.json` re-confirms it. R20 verbatim claim is unaffected.
- Known residual: MA-AGEN-002 (F-001/F-002 in WKFL) remains OPEN. ANIM-10 cert covers restore-correctness, not F-001/F-002 closure.
