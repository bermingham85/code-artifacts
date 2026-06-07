# SPEC-ANIM-08 — AGEN-Verification agent: verbatim recovery from codex transcript

**Phase:** ANIM-08 of `APEX-ANIM-MB-WO-00001`
**Parent subproject:** SP-ANIM
**Depends-on:** ANIM-07 (parallel scaling work — independent in scope)
**Blocks:** ANIM-09+ (other AGEN agents' recovery)
**Issued:** 2026-06-07
**Branch:** `phase/ANIM-08-AGEN-verification` (branched from `phase/ANIM-07@5eed6dd`)
**Reference patterns followed (PLAN_CRITERIA §11):** doctrine R15 (silent-twice), R19 (decision: EXTEND of existing build via verbatim transcript restore — not greenfield), R20 (verbatim recovery / no invention), WO §3 ("recover from … Codex review transcripts (verbatim recovery, not invention), then commit + PR this time").

---

## 1. Objective

Restore the 5 missing AGEN-Verification agent artifacts to the live repo at `AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/` verbatim from the Codex review transcript at `apex_governance/codex_runs/AGEN-verification-agent/AGEN-verification-agent-review-20260523T012003Z-b0bd298e.txt` (the latest 2026-05-23T01:20:03Z review run, which contains the full reviewed artifact set inline between `=== FILE: <path> ===` and `=== END FILE ===` markers).

Per WO §3 and shared-memory reference [[project_agen_five_agent_state_2026-06-07]], Verification is the only AGEN agent whose **full artifact set** is inline-recoverable from its codex_runs transcript. ANIM-08 restores Verification only; ANIM-09+ will handle Builder (WKFL+PRMPT+TEST+SCRPT only — SPEC missing inline), Specification (full set with 2 open findings F-001/F-002 to address), Architecture (migration SCRPT only), Router (migration SCRPT only).

## 2. Pre-flight findings (informs scope)

- Live path `C:/Users/Owner/Repos/code-artifacts/AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/` had only 2 files committed (HANDOVER.md + PROJECT_INSTRUCTIONS.md, both dated 2026-04-19) before this phase; the canonical X clone at `X:/Automations/apex/registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/` is identical (per [[project_agen_five_agent_state_2026-06-07]]).
- Transcript inline content references the now-defunct `apex/registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/` path; per memory the content is functionally identical (the clones path was a sibling working copy of the live path during the May build).
- Per [[handover_apex_anim_wo_2026-06-07]] §6, the May gap was **deletion** (not "missing commit" as the WO body says — the memory was authoritative when written 2026-06-07; verified via `git log --all -- '*AGEN-WKFL-verification*'` returning no history anywhere). The WO §3 wording "the May gap was a missing commit step, not a deletion" is reconciled here as: there IS a recoverable May-23 artifact set INLINE in the codex transcript, so functionally this is "recover + commit + PR this time" — the WO's intent is satisfied even though the prior-state was a deletion event.

## 3. Scope (in / out)

In scope:
- Extract `AGEN-SCRPT-verification-supabase-migration-v1.sql`, `AGEN-PRMPT-verification-system-prompt-v1.md`, `AGEN-SPEC-verification-integration-v1.md`, `AGEN-TEST-verification-test-plan-v1.md`, `AGEN-WKFL-verification-workflow-v1.json` from the transcript byte-for-byte. Write to live repo at `AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/`.
- Verify the WKFL JSON parses and matches transcript node count (47 nodes).
- Persist the extraction script at `apex/registry/agen_recovery_extract.py` (APEX-MB-PY-00116) as a reusable tool for ANIM-09+ recoveries.
- Write `apex/docs/agen/ANIM-08-recovery-evidence.json` with per-file source-transcript provenance (transcript path + sha256 + byte range).
- Audit at `apex/audit/anim-08/verification-restore-<ts>.json`.

Out of scope:
- HANDOVER.md and PROJECT_INSTRUCTIONS.md: already present at live path, not overwritten.
- Re-running the AGEN-Verification codex review loop (silent-twice clock IS functionally reset per shared-memory note; restoring on disk does NOT restore the silent-twice clock — that's a doctrine question for the operator and out of scope here; logged as a known residual).
- Any of the other 4 AGEN agents (Builder/Specification/Architecture/Router) — separate ANIM-09+ phases.
- The SIGNED_OFF.json reconciliation at `apex/audit/claude_codex_loop/AGEN-migration-coordinator/SIGNED_OFF.json` — separate operator decision (not in WO scope).
- ComfyUI / Wan2.2 / LTX / Hunyuan installs — those belong to ANIM-02 which is already certed and PR'd.

## 4. Access matrix (per PLAN_CRITERIA §8)

| Resource | Path | RW | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-08-AGEN-verification` | RW | env_sync GitHub PAT |
| Live AGEN dir | `C:/Users/Owner/Repos/code-artifacts/AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/` | RW | local |
| Codex transcript | `C:/Users/Owner/apex_governance/codex_runs/AGEN-verification-agent/AGEN-verification-agent-review-20260523T012003Z-b0bd298e.txt` | R | local |
| Codex CLI | `codex` (v0.135.0, gpt-5.5, ChatGPT auth) | RW | shell PATH |

## 5. Inputs (with SHAs)

- Source transcript: `apex_governance/codex_runs/AGEN-verification-agent/AGEN-verification-agent-review-20260523T012003Z-b0bd298e.txt` (2235 lines, 7 `=== FILE:` markers, 7 `=== END FILE ===` markers — balanced).
- Live HANDOVER.md and PROJECT_INSTRUCTIONS.md: preserved as-is (2026-04-19 mtime).

## 6. Outputs

- 5 new files at `AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/` (additive — see §3 list).
- `apex/registry/agen_recovery_extract.py` (APEX-MB-PY-00116) — reusable extractor.
- `apex/docs/agen/ANIM-08-recovery-evidence.json` — provenance manifest (transcript path + sha256 + per-file byte ranges + sha256s).
- `apex/audit/anim-08/verification-restore-<ts>.json` — restore audit.
- `apex/docs/spec/SPEC-ANIM-08.md` (this file).
- `apex_governance/handovers/ANIM-08.handover.md`.
- `apex_governance/certs/CERT-ANIM-08.json` + index update.
- `apex_governance/codex_runs/ANIM-08/round*.txt` (transcripts).

## 7. Definition of Done

- 5 missing AGEN-Verification artifacts restored verbatim to live path; WKFL JSON parses; SHA256s recorded.
- Extractor script committed (`apex/registry/agen_recovery_extract.py`) and registered.
- Recovery evidence + restore audit committed.
- Codex adversarial-review silent-twice (R15) + clean ship-gate.
- Cert minted with full doctrine-conformance table; handover written; PR opened via `_make_pr_api.py`.

## 8. Codex commands required

| Stage | Command | Persistence |
|---|---|---|
| Spec + diff | `CODEX_MODEL=gpt-5.5 codex exec` adversarial bundle (inline-stdin) | `apex_governance/codex_runs/ANIM-08/round<n>.txt` |
| Ship-gate | `CODEX_MODEL=gpt-5.5 codex exec` ship-gate review | same dir, `ship-gate.txt` |

## 9. Test plan

- WKFL JSON parses + node_count > 0.
- Per-file sha256 stable between extraction and committed blob (no encoding drift on write).
- Re-running the extractor against the same transcript reproduces byte-identical output (idempotency).
- Extractor refuses to write outside the configured live dir (path-escape closed).

## 10. Pass criteria (binary)

- [ ] 5 files restored at the correct live path with non-zero size.
- [ ] WKFL JSON parses.
- [ ] Recovery-evidence.json cites the source transcript sha256.
- [ ] Codex silent-twice + ship-gate clean.
- [ ] Cert + handover + PR opened.

## 11. Rollback plan

- Trigger: any post-restore assertion fails (JSON parse error; byte drift between transcript and committed blob).
- Revert: `git revert <commit>` on `phase/ANIM-08-AGEN-verification`.
- Data restore: no destructive operation — restore is purely additive (HANDOVER.md and PROJECT_INSTRUCTIONS.md untouched).

## 12. Doctrine conformance table

Filled at cert time. R15 (silent-twice), R16 (loop caps), R19 (EXTEND via verbatim restore — not greenfield; transcript is the authoritative prior build per doctrine R20), R20 (verbatim recovery, no invention; byte-for-byte from transcript), P1/P2 (Codex audits, Claude builds + restores), O2 (model logged: `gpt-5.5`), O6 (transcripts persisted), C1–C4 + C8 (cert evidence rows).

## 13. Cleanup report (PLAN_CRITERIA §12)

- Files deleted: none.
- Files renamed: none.
- Paths reconciled: extraction writes to live path (`AGENT_BUILD_SYSTEM/07_VERIFICATION_AGENT/`) even though transcript references the deprecated clones path (`apex/registry/clones/...`). Documented in recovery-evidence.json.
- Stubs/TODOs: none introduced.
- Sandbox dir: not used.
- Scratch dir: `C:/tmp/extract_agen_verification.py` was a single-use bootstrap; the production extractor lives at `apex/registry/agen_recovery_extract.py`.
- Known residual: silent-twice clock for the AGEN-Verification agent itself is functionally reset per [[project_agen_five_agent_state_2026-06-07]]. Restoring artifacts on disk does NOT re-arm silent-twice; ANIM-08 cert covers restore-correctness only, not the agent's own R15 closure. Logged for follow-on operator decision (rerun review on restored inputs vs accept transcript-attested silent run as historical evidence).
