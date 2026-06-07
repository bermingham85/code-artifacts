# SPEC-ANIM-09 — AGEN-Builder agent: verbatim recovery from codex transcripts

**Phase:** ANIM-09 of `APEX-ANIM-MB-WO-00001`
**Parent subproject:** SP-ANIM
**Depends-on:** ANIM-08 (reuses extractor `apex/registry/agen_recovery_extract.py` APEX-MB-PY-00116)
**Blocks:** ANIM-10/11/12 only by branch stacking, not by content.
**Issued:** 2026-06-07
**Branch:** `phase/ANIM-09-AGEN-builder` (branched from `phase/ANIM-08-AGEN-verification@8be8daf`)
**Reference patterns followed (PLAN_CRITERIA §11):** doctrine R15 (silent-twice), R19 (REUSE of extractor `agen_recovery_extract.py` APEX-MB-PY-00116; rejected GREENFIELD), R20 (verbatim recovery / no invention), WO §3 ("recover from … Codex review transcripts (verbatim recovery, not invention), then commit + PR this time"), ANIM-08 precedent (same BYTE-MODE extractor flow).

---

## 1. Objective

Restore the 4 inline-recoverable AGEN-Builder agent artifacts to the live repo at `AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/` verbatim from two Codex review transcripts under `apex_governance/codex_runs/AGEN-builder-agent/`. The 5th artifact (`AGEN-SPEC-builder-integration-v1.md`) is **not inline in any of the 6 builder transcripts** — its absence is logged to `MISSING_ARTIFACTS.queue.json` (entry MA-AGEN-001-BUILDER-SPEC) and the builder is shipped without it; future recovery requires a different source (operator action).

Per WO §3 and shared-memory reference [[project_agen_five_agent_state_2026-06-07]], Builder has WKFL+PRMPT+TEST+SCRPT recoverable inline; SPEC is missing. This is exactly what ANIM-08's handover §5 promised for ANIM-09.

## 2. Pre-flight findings (informs scope)

- Live path `C:/Users/Owner/Repos/code-artifacts/AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/` had only `HANDOVER.md` + `PROJECT_INSTRUCTIONS.md` before this phase (mtime 2026-04-19). Mirrors ANIM-08's Verification pre-state exactly.
- Six builder transcripts exist under `apex_governance/codex_runs/AGEN-builder-agent/` (2026-05-25 series, IDs `3da95056` → `ed0ee8d2`). Across the six, inline-file inventory is:
  - `AGEN-WKFL-builder-agent-v1.json`: in all 6 transcripts, sizes 65725 → 75182 bytes (monotonic growth across iterations); **final size 75182 B in the latest (`ed0ee8d2`) transcript**.
  - `AGEN-PRMPT-builder-system-prompt-v1.md`: in all 6, sizes 14811 → 17496 B; final 17496 B in `ed0ee8d2`.
  - `AGEN-TEST-builder-test-plan-v1.md`: in all 6, sizes 9424 → 11156 B; final 11156 B in `ed0ee8d2`.
  - `AGEN-SCRPT-builder-supabase-migration-v1.sql`: in **transcript 1 only** (`3da95056`), 28351 B. Dropped from later transcripts because the SQL didn't change (reviewer convention of only re-inlining files that changed since last round).
  - `AGEN-SPEC-builder-integration-v1.md`: not in any of the 6 transcripts.
- Source-of-record choice per file: take the **latest** transcript for WKFL/PRMPT/TEST (final reviewer-iterated bytes), take the **only** transcript for SCRPT (transcript 1). This preserves R20 verbatim recovery and reflects the actual operational endpoint of each artifact at review-loop close.

## 3. Scope (in / out)

In scope:
- Extract `AGEN-WKFL-builder-agent-v1.json` (75182 B) + `AGEN-PRMPT-builder-system-prompt-v1.md` (17496 B) + `AGEN-TEST-builder-test-plan-v1.md` (11156 B) from `AGEN-builder-agent-review-20260525T125754Z-ed0ee8d2.txt`. Write byte-for-byte to live repo at `AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/`.
- Extract `AGEN-SCRPT-builder-supabase-migration-v1.sql` (28351 B) from `AGEN-builder-agent-review-20260525T115148Z-3da95056.txt`. Write byte-for-byte to same live repo dir.
- Verify the WKFL JSON parses and report node count.
- Write `apex/docs/agen/ANIM-09-recovery-evidence.json` with per-file source-transcript provenance (transcript path + sha256 + byte range + per-file sha256).
- Audit at `apex/audit/anim-09/builder-restore-<ts>.json`.
- Idempotency rerun audit at `apex/audit/anim-09/builder-idempotency-rerun-<ts>.json` (full 4-file rerun proving `no_op_idempotent` on every file).
- Append `MA-AGEN-001-BUILDER-SPEC` to `apex_governance/MISSING_ARTIFACTS.queue.json` documenting the SPEC gap.

Out of scope:
- `HANDOVER.md` and `PROJECT_INSTRUCTIONS.md`: already present at live path, not overwritten.
- Re-running the AGEN-Builder codex review loop on restored inputs (silent-twice rearm) — operator decision, see [[handover_apex_anim_session_2026-06-07b]] §3.
- Any of the other 3 remaining AGEN agents (Specification/Architecture/Router) — separate ANIM-10/11/12 phases.
- ComfyUI / Wan / LTX / Hunyuan installs — ANIM-02 (already certed).
- Extractor modifications — APEX-MB-PY-00116 stays frozen at ANIM-08 bytes (its existence/SHA guard + BYTE-MODE invariants are doctrine-anchored).

## 4. Access matrix (per PLAN_CRITERIA §8)

| Resource | Path | RW | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-09-AGEN-builder` | RW | env_sync GitHub PAT |
| Live AGEN dir | `C:/Users/Owner/Repos/code-artifacts/AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/` | RW | local |
| Codex transcript A (latest) | `C:/Users/Owner/apex_governance/codex_runs/AGEN-builder-agent/AGEN-builder-agent-review-20260525T125754Z-ed0ee8d2.txt` (sha256 e9f74bc6…) | R | local |
| Codex transcript B (first, for SCRPT) | `C:/Users/Owner/apex_governance/codex_runs/AGEN-builder-agent/AGEN-builder-agent-review-20260525T115148Z-3da95056.txt` (sha256 e9fc8170…) | R | local |
| Codex CLI | `codex` (gpt-5.5, ChatGPT auth) | RW | shell PATH |

## 5. Inputs (with SHAs)

- Transcript A: `apex_governance/codex_runs/AGEN-builder-agent/AGEN-builder-agent-review-20260525T125754Z-ed0ee8d2.txt`, 123019 B, sha256 `e9f74bc668ff358771af18851112efd0891bd49bb76317453a8c45798ad1e318`. Source-of-record for WKFL/PRMPT/TEST.
- Transcript B: `apex_governance/codex_runs/AGEN-builder-agent/AGEN-builder-agent-review-20260525T115148Z-3da95056.txt`, 130834 B, sha256 `e9fc817013bc5a4e1b851a240d848bb578237bfbce7ebae131b725196e3f712c`. Source-of-record for SCRPT.
- Live `HANDOVER.md` + `PROJECT_INSTRUCTIONS.md`: preserved as-is (mtime 2026-04-19).
- Extractor: `apex/registry/agen_recovery_extract.py` (APEX-MB-PY-00116), unchanged from ANIM-08.

## 6. Outputs

- 4 new files at `AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/` (additive — see §3 list).
- `apex/docs/agen/ANIM-09-recovery-evidence.json` — provenance manifest (per-file source transcript + sha256 + byte ranges).
- `apex/audit/anim-09/builder-restore-<ts>.json` — restore audit.
- `apex/audit/anim-09/builder-idempotency-rerun-<ts>.json` — idempotency proof.
- `apex/docs/spec/SPEC-ANIM-09.md` (this file).
- `apex_governance/handovers/ANIM-09.handover.md`.
- `apex_governance/certs/CERT-ANIM-09.json` + index update.
- `apex_governance/codex_runs/ANIM-09/round*.txt` (transcripts).
- One row appended to `apex_governance/MISSING_ARTIFACTS.queue.json` (MA-AGEN-001-BUILDER-SPEC).

## 7. Definition of Done

- 4 inline-recoverable AGEN-Builder artifacts restored verbatim to live path; WKFL JSON parses; SHA256s recorded.
- SPEC gap logged to MISSING_ARTIFACTS queue (operator-actionable, not a phase blocker per R19 EXTEND decision).
- Recovery evidence + restore audit + idempotency rerun committed.
- Codex adversarial-review silent-twice (R15) + clean ship-gate.
- Cert minted with full doctrine-conformance table; handover written; PR opened via `_make_pr_api.py`.

## 8. Codex commands required

| Stage | Command | Persistence |
|---|---|---|
| Spec + diff | `CODEX_MODEL=gpt-5.5 codex exec --model gpt-5.5 < bundle.txt > round<n>.txt` | `apex_governance/codex_runs/ANIM-09/round<n>.txt` |
| Ship-gate | same | same dir, `ship-gate.txt` |

## 9. Test plan

- WKFL JSON parses + `nodes` array non-empty (target ≥ 30 nodes per Builder agent design).
- Per-file sha256 stable between extraction output JSON and committed on-disk blob.
- Re-running the extractor with the same `--restore` set against the same transcript produces all-`no_op_idempotent` output and writes zero bytes.
- Extractor path-escape closure verified (already covered in ANIM-08 spec round 2; reuse the unchanged code).

## 10. Pass criteria (binary)

- [ ] 4 files restored at `AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/` with byte-exact size match to transcript captures.
- [ ] WKFL JSON parses; node count reported in audit.
- [ ] Recovery-evidence.json cites BOTH source transcripts' SHA256.
- [ ] Idempotency rerun shows 4-of-4 `no_op_idempotent` (zero writes).
- [ ] MA-AGEN-001-BUILDER-SPEC row present in MISSING_ARTIFACTS.queue.json.
- [ ] Codex silent-twice + ship-gate clean.
- [ ] Cert + handover + PR opened.

## 11. Rollback plan

- Trigger: any post-restore assertion fails (JSON parse error; SHA drift between transcript slice and committed blob).
- Revert: `git revert <commit>` on `phase/ANIM-09-AGEN-builder`.
- Data restore: purely additive; HANDOVER.md and PROJECT_INSTRUCTIONS.md untouched. Rollback is safe — Builder live path returns to pre-ANIM-09 state (2 files).

## 12. Doctrine conformance table

Filled at cert time. R15 (silent-twice), R16 (loop caps), R19 (REUSE decision — chose `agen_recovery_extract.py` APEX-MB-PY-00116 over greenfield rewrite; rejected: a one-shot `extract_builder.py` because it duplicates the audited ANIM-08 invariants), R20 (verbatim recovery — byte-for-byte from two transcripts; no LLM-rewrite), P1/P2 (Codex audits, Claude builds + restores), O2 (model logged: `gpt-5.5`), O6 (transcripts persisted under codex_runs/ANIM-09/), C1–C4 + C8 (cert evidence rows).

## 13. Cleanup report (PLAN_CRITERIA §12)

- Files deleted: none.
- Files renamed: none.
- Paths reconciled: extractor writes to live path (`AGENT_BUILD_SYSTEM/06_BUILDER_AGENT/`) even though transcript `=== FILE: ===` headers reference the deprecated `apex/registry/clones/...` path. Documented in recovery-evidence.json.
- Stubs/TODOs introduced: none.
- Sandbox dir: not used.
- Scratch dir: not used.
- Known residual: silent-twice clock for the AGEN-Builder agent itself is functionally reset per [[project_agen_five_agent_state_2026-06-07]]. ANIM-09 cert covers restore-correctness only, not the agent's own R15 closure. Builder-SPEC gap logged as MA-AGEN-001-BUILDER-SPEC for operator action (source-elsewhere; not recoverable from these transcripts).
