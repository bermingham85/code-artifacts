# SPEC-ANIM-12 — AGEN-Router agent: verbatim recovery from codex transcript (1 of 5)

**Phase:** ANIM-12 of `APEX-ANIM-MB-WO-00001`
**Parent subproject:** SP-ANIM
**Depends-on:** ANIM-08 (extractor APEX-MB-PY-00116)
**Issued:** 2026-06-07
**Branch:** `phase/ANIM-12-AGEN-router` (branched from `phase/ANIM-11-AGEN-architecture@b897019`)
**Reference patterns followed:** R15 silent-twice, R19 REUSE, R20 verbatim, ANIM-09 round-1 fix pattern (in-repo MA mirror).

---

## 1. Objective

Restore the **1 of 5 inline-recoverable** AGEN-Router agent artifact (Supabase migration SCRPT) to `AGENT_BUILD_SYSTEM/04_ROUTER_AGENT/` byte-for-byte from the AGEN-migration-coordinator codex review transcript. The other 4 artifacts (WKFL, PRMPT, SPEC, TEST) are not inline in any codex_runs transcript and are logged as separate MA queue rows.

## 2. Pre-flight findings

- Live path `AGENT_BUILD_SYSTEM/04_ROUTER_AGENT/` had only `HANDOVER.md` + `PROJECT_INSTRUCTIONS.md` before this phase (mtime 2026-04-19).
- No `AGEN-router*` codex_runs subdirectory exists — Router never had its own build/review loop directory in the May 2026 work. The router migration SCRPT appears inline only in the **AGEN-migration-coordinator** transcripts (which review the cross-agent migration coordination, bundling each agent's SCRPT).
- Two migration-coordinator transcripts exist:
  - `AGEN-migration-coordinator-review-20260523T051624Z-66e87eaa.txt` (710,212 B)
  - `AGEN-migration-coordinator-review-20260523T052539Z-3dd63aeb.txt` (711,026 B)
  Both inline `AGEN-SCRPT-router-supabase-migration-v1.sql` at 21,019 B (size identical across both, indicating SCRPT did not change between the two coordinator rounds). The **latest** (`3dd63aeb`) is taken as source-of-record.
- Grep across all 200+ codex_runs transcripts for `AGEN-WKFL-router|AGEN-PRMPT-router|AGEN-SPEC-router|AGEN-TEST-router` returned zero hits. None of the runtime artifacts beyond SCRPT have inline byte content anywhere.

## 3. Scope (in / out)

In scope:
- Extract `AGEN-SCRPT-router-supabase-migration-v1.sql` (21,019 B, 458 SQL lines) byte-for-byte. Write to live path.
- Recovery evidence + restore audit + idempotency rerun audit (1/1 no_op).
- Append **four** rows to MA queue (in external + in-repo mirror): MA-AGEN-001-ROUTER-WKFL, MA-AGEN-001-ROUTER-PRMPT, MA-AGEN-001-ROUTER-SPEC, MA-AGEN-001-ROUTER-TEST.

Out of scope:
- WKFL/PRMPT/SPEC/TEST runtime artifacts (operator-actionable per the new MA rows).
- HANDOVER + PROJECT_INSTRUCTIONS already at live path.
- Re-running AGEN-Router codex review loop.
- Other AGEN agents (Builder/Specification/Architecture/Verification — separate phases).
- Extractor modifications.

## 4. Access matrix

| Resource | Path | RW |
|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-12-AGEN-router` | RW |
| Live AGEN dir | `C:/Users/Owner/Repos/code-artifacts/AGENT_BUILD_SYSTEM/04_ROUTER_AGENT/` | RW |
| Codex transcript | `…/AGEN-migration-coordinator-review-20260523T052539Z-3dd63aeb.txt` (sha256 `0cad3c58…`, 711,026 B) | R |
| Codex CLI | `codex` (gpt-5.5) | RW |

## 5. Inputs (with SHAs)

- Transcript: 711,026 B, sha256 `0cad3c58f5825dbb486ffd4606a9220b301fc71583dda8eace9eef554f54b078`. Contains 29 inline files including SCRPT migrations for builder/architecture/router and full verification artifact set; only the **router SCRPT** is in ANIM-12 scope.
- Extractor: unchanged.

## 6. Outputs

- 1 restored file at live path.
- `apex/docs/agen/ANIM-12-recovery-evidence.json`.
- `apex/audit/anim-12/router-restore-2026-06-07T10-40-00Z.json`.
- `apex/audit/anim-12/router-idempotency-rerun-2026-06-07T10-42-00Z.json`.
- `apex/audit/anim-12/missing-artifacts-queue-rows.json` (4 MA rows mirrored in-repo).
- Spec + handover + cert + codex_runs/ANIM-12/*.

## 7. Definition of Done

- 1 byte-exact restore.
- 4 MA queue rows in repo + external.
- Idempotency rerun 1/1 no_op.
- Silent-twice + ship-gate clean.
- Cert + handover + PR.

## 8. Codex commands

`CODEX_MODEL=gpt-5.5 codex exec --model gpt-5.5 < bundle.txt > round<n>.txt`.

## 9. Test plan

- SCRPT size + sha exact match to transcript byte-slice.
- Idempotency rerun 1/1 no_op.
- Path-escape closure inherited.

## 10. Pass criteria

- [ ] SCRPT restored at byte-exact size.
- [ ] Evidence cites transcript SHA.
- [ ] Idempotency rerun no_op.
- [ ] 4 MA queue rows present (repo + external).
- [ ] Silent-twice + ship-gate clean.
- [ ] Cert + handover + PR.

## 11. Rollback plan

Additive only. `git revert` safe.

## 12. Doctrine conformance table

Filled at cert. R15, R19, R20, P1, P2, O2, O6.

## 13. Cleanup report

- Files deleted: none.
- Paths reconciled: transcript header references clones path; extractor writes to live; documented in evidence.
- Stubs/TODOs: none.
- Sandbox/Scratch dirs: not used.
- Known residual: **4 of 5 Router runtime artifacts not recovered** (WKFL/PRMPT/SPEC/TEST). Router is the smallest recovery of the AGEN four. Operator-actionable per MA rows.
- Operator note: the Router agent CANNOT be deployed from this phase alone — only the migration SCRPT is restored. A future phase will need to recover or draft WKFL/PRMPT/SPEC/TEST before Router runtime use.
