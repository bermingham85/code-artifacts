# SPEC-ANIM-11 — AGEN-Architecture agent: verbatim recovery from codex transcript

**Phase:** ANIM-11 of `APEX-ANIM-MB-WO-00001`
**Parent subproject:** SP-ANIM
**Depends-on:** ANIM-08 (extractor APEX-MB-PY-00116)
**Issued:** 2026-06-07
**Branch:** `phase/ANIM-11-AGEN-architecture` (branched from `phase/ANIM-10-AGEN-specification@97bc6f5`)
**Reference patterns followed:** R15 silent-twice, R19 REUSE, R20 verbatim, ANIM-08/09/10 precedent (and the ANIM-09 round-1 fix pattern for in-repo MA mirror).

---

## 1. Objective

Restore 4 of 5 AGEN-Architecture agent artifacts to `AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/` byte-for-byte from the latest 2026-05-24 post-migration Codex review transcript at `apex_governance/codex_runs/AGEN-architecture-agent-post-migration/AGEN-architecture-agent-post-migration-review-20260524T203145Z-3e4d1dcd.txt`. The 5th artifact (SPEC integration doc) is not inline in any architecture transcript; logged as `MA-AGEN-001-ARCH-SPEC` with tracked in-repo mirror per the ANIM-09 round-1 pattern.

## 2. Pre-flight findings

- Live path `AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/` had only `HANDOVER.md` + `PROJECT_INSTRUCTIONS.md` before this phase (mtime 2026-04-19).
- **Important shared-memory correction:** [[project_agen_five_agent_state_2026-06-07]] says "Architecture: only migration SCRPT inline". This is **incomplete**. Inventory across all architecture codex_runs subdirectories shows:
  - `apex_governance/codex_runs/AGEN-architecture-agent/`: 8 review transcripts, each inlines only `HANDOVER.md` + `PROJECT_INSTRUCTIONS.md` (live-path docs); no AGEN-* runtime artifacts.
  - `apex_governance/codex_runs/AGEN-architecture-agent-build-2026-05-24/`: 11 review transcripts, inline WKFL + PRMPT only (no SCRPT/TEST/SPEC).
  - `apex_governance/codex_runs/AGEN-architecture-agent-post-migration/`: 5 review transcripts, inline **4 of 5** AGEN artifacts (WKFL, PRMPT, TEST, SCRPT) plus CERT-APEX-AUTONOMOUS-DELIVERY.json + DOCUMENT_REGISTER.md + HANDOVER + PROJECT_INSTRUCTIONS. **This dir is the source-of-record.**
  - `apex_governance/codex_runs/AGEN-architecture-prompt-v1-{,retry-}20260524/`: 2 advisory transcripts, inline PRMPT only.
  - `apex_governance/codex_runs/AGEN-architecture-workflow-v1-{,retry-}20260524/`: 2 advisory transcripts, inline WKFL only.
- Latest post-migration transcript (`3e4d1dcd`, 2026-05-24T20:31:45Z) has the final reviewer-iterated bytes for all 4 inline AGEN artifacts.
- SPEC (`AGEN-SPEC-architecture-integration-v1.md`) is not inline in ANY architecture transcript across all 6 subdirectories — same situation as Builder.

## 3. Scope (in / out)

In scope:
- Extract 4 artifacts byte-for-byte from `3e4d1dcd`:
  - `AGEN-WKFL-architecture-agent-v1.json` (58,973 B, 40 nodes)
  - `AGEN-PRMPT-architecture-system-prompt-v1.md` (11,591 B)
  - `AGEN-TEST-architecture-test-plan-v1.md` (4,162 B)
  - `AGEN-SCRPT-architecture-supabase-migration-v1.sql` (26,908 B, 581 SQL lines)
- Write `apex/docs/agen/ANIM-11-recovery-evidence.json` with provenance.
- Restore + idempotency-rerun audits.
- In-repo `apex/audit/anim-11/missing-artifacts-queue-row.json` mirroring the appended MA-AGEN-001-ARCH-SPEC row.
- Append MA-AGEN-001-ARCH-SPEC to the external `apex_governance/MISSING_SECRETS.queue.json`.

Out of scope:
- `HANDOVER.md` and `PROJECT_INSTRUCTIONS.md` at live path: already present, untouched.
- `CERT-APEX-AUTONOMOUS-DELIVERY.json` and `DOCUMENT_REGISTER.md` inlined in the transcript: not target-agent artifacts; not extracted.
- Re-running the AGEN-Architecture codex review loop (silent-twice rearm).
- ANIM-12 (Router).
- Extractor modifications.

## 4. Access matrix

| Resource | Path | RW |
|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-11-AGEN-architecture` | RW |
| Live AGEN dir | `C:/Users/Owner/Repos/code-artifacts/AGENT_BUILD_SYSTEM/05_ARCHITECTURE_AGENT/` | RW |
| Codex transcript | `…/AGEN-architecture-agent-post-migration-review-20260524T203145Z-3e4d1dcd.txt` (sha256 `a2de5faa…`, 188,414 B) | R |
| Codex CLI | `codex` (gpt-5.5) | RW |

## 5. Inputs (with SHAs)

- Transcript: 188,414 B, sha256 `a2de5faaea9a97f8e9e9430137f824e327b7a4abf3b15faa1f3268b438b8edf0`. Marker balance: 8/8 (4 AGEN + CERT + DOCUMENT_REGISTER + HANDOVER + PROJECT_INSTRUCTIONS).
- Extractor: unchanged.

## 6. Outputs

- 4 restored files + recovery-evidence + restore audit + idempotency rerun audit + in-repo MA mirror + spec + handover + cert + codex_runs/ANIM-11/*.

## 7. Definition of Done

- 4 byte-exact restores; WKFL parses.
- Evidence + audits + MA mirror committed.
- MA-AGEN-001-ARCH-SPEC durably tracked in-repo AND external queue.
- Silent-twice + ship-gate clean.
- Cert + handover + PR.

## 8. Codex commands

`CODEX_MODEL=gpt-5.5 codex exec --model gpt-5.5 < bundle.txt > round<n>.txt`.

## 9. Test plan

- 4-of-4 byte-exact size match.
- WKFL parses, node_count ≥ 30.
- Idempotency rerun = 4/4 no_op.
- Path-escape closure inherited.

## 10. Pass criteria

- [ ] 4 files restored at byte-exact size.
- [ ] WKFL parses; nodes reported.
- [ ] Evidence cites transcript SHA.
- [ ] Idempotency rerun all-no_op.
- [ ] MA-AGEN-001-ARCH-SPEC row in repo + external queue.
- [ ] Silent-twice + ship-gate clean.
- [ ] Cert + handover + PR.

## 11. Rollback plan

Additive only. `git revert <commit>` safe.

## 12. Doctrine conformance table

Filled at cert. R15, R19, R20, P1, P2, O2 (gpt-5.5), O6.

## 13. Cleanup report

- Files deleted: none.
- Files renamed: none.
- Paths reconciled: transcript headers reference `apex/registry/clones/...`; extractor writes to live path; documented in evidence.
- Stubs/TODOs: none introduced.
- Sandbox/Scratch dirs: not used.
- Shared-memory correction logged: original "only migration SCRPT inline" claim was inaccurate; the post-migration transcript subdirectory has WKFL/PRMPT/TEST/SCRPT (4 of 5). This correction is captured here and in the handover; not propagated to the shared-memory file in this phase (operator-touchable).
- Known residual: SPEC missing → MA-AGEN-001-ARCH-SPEC.
