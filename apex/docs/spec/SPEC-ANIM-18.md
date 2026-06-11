# SPEC-ANIM-18 — fal.ai animation-agent wrapper shim (FalCloud tier write side)

## Identity

- Phase ID: `ANIM-18`
- Title: fal.ai animation-agent wrapper shim — closes WO §1.4 FalCloud write side after ANIM-17 closed the read side
- Parent subproject: SP-ANIM (WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator-engineer
- Depends-on: ANIM-17 (FalCloud key resolution wired), ANIM-16 (tier-plan emission)
- Blocks: actual cloud render bursts on FalCloud tier
- Reference patterns followed: `apex/registry/muscle_video_agent.py:resolve_env_key_from_env_sync` (R20 — no new key resolver per ANIM-17 handover §"NOT redo")
- Branch: `phase/ANIM-18-fal-shim`
- Cert tag at completion: `cert/ANIM-18@<sha>`

## Context window budget

- Token budget: ~25k for build + review (small phase, one new file + one config edit)
- Files in scope (≤8):
  1. `apex/registry/muscle_fal_shim.py` (new, ≤300 LOC)
  2. `apex/docs/anim/ANIM-05-tier-config.json` (edit: flip FalCloud.shim_status READY, set wrapper_invocation)
  3. `apex/docs/spec/SPEC-ANIM-18.md` (this file)
  4. `apex/docs/anim/ANIM-18-evidence.json` (run evidence + payload schema + leak check)
  5. `apex/audit/anim-18/probe_negatives.py` (negative-path probes mirroring ANIM-17 pattern)
  6. `apex/docs/DOCUMENT_REGISTER.md` (00118 row, registered up-front)
- Files explicitly out of scope:
  - `muscle_video_agent.py` — no edits; shim is a sibling, not a method on the agent
  - `muscle_music_video.py` — local Wan/LTX/Hunyuan path unchanged
  - Any new env-key resolver — explicitly forbidden by ANIM-17 handover ("Do not introduce a new env-key resolution helper")

## Access matrix

| Resource | Path or endpoint | Read/Write | Resolution source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-18-fal-shim` | RW | env_sync GitHub PAT |
| APEX root | `C:\Users\Owner\Repos\code-artifacts\apex\` | RW | local |
| Governance | `C:\Users\Owner\apex_governance\` | RW | local |
| `FAL_AI_API_KEY` | `X:/env_sync/user_portable.json:FAL_AI_API_KEY` | R (process memory only) | env_sync via ANIM-17 helper |
| fal.ai queue endpoint | `https://queue.fal.run/fal-ai/animation-agent` | RW (only under `--live`) | HTTPS |
| Codex CLI | `CODEX_MODEL=gpt-5.5 codex exec` | RW | ChatGPT-account auth |

No unresolved rows — `FAL_AI_API_KEY` confirmed in env_sync at ANIM-17 cert time. No new secret introduced.

## Inputs

- ANIM-17 handover (resolved-key fingerprint, no raw key handling).
- ANIM-16 tier-plan output shape (`apex/docs/anim/ANIM-16-tier-plan-<project>.json`) — shim consumes per-shot records where `tier_chosen == "FalCloud"`.
- fal.ai animation-agent docs surface (HTTPS POST `queue.fal.run/<model-id>`, `Authorization: Key <KEY>` header, JSON body with input fields, returns `{request_id, status_url, response_url}`). Documented in payload schema, not invented at runtime.
- Existing `resolve_env_key_from_env_sync()` and `_key_fingerprint()` in `muscle_video_agent.py`.

## Outputs

- `apex/registry/muscle_fal_shim.py` — shim file.
- `apex/docs/anim/ANIM-05-tier-config.json` v3 — `FalCloud.shim_status = "READY"`, `wrapper_invocation = "python apex/registry/muscle_fal_shim.py --submit --shot-id <id> --tier-plan <path> --live"`.
- `apex/docs/anim/ANIM-18-evidence.json` — schema; happy-path dry-run record; negative-path probe results; leak-check; codex round ledger.
- `apex/audit/anim-18/probe_negatives.py` — 6-probe negative harness (missing tier-plan, wrong tier-plan shape, FalCloud tier-not-chosen for shot, key missing, key empty, fal endpoint unreachable).
- `apex_governance/codex_runs/ANIM-18/round{1..N}.txt` — transcripts.
- `apex_governance/certs/CERT-ANIM-18.json` — cert.
- `apex_governance/handovers/ANIM-18.handover.md` — handover.
- `apex/docs/qa/QA-ANIM-18.md` — test report.

## Definition of Done

- Shim is callable via `python apex/registry/muscle_fal_shim.py --help` and lists 4 modes (`--probe`, `--build-payload`, `--submit`, `--poll`).
- `--build-payload` is deterministic from `(shot record, tier_plan path)` — same input → same JSON bytes.
- Default of `--submit` is dry-run; **`--live` is REQUIRED** to actually call fal.ai. The phrase "DRY-RUN — no HTTP call made" appears in dry-run output.
- Fingerprint exposure rule (R20 + ANIM-17): every payload and log shows `key_fingerprint` (first4:last4 + sha256[:12] + key_length), **never** the raw key.
- Evidence file contains a runtime leak check confirming the raw key bytes do not appear in any persisted artifact (repo files, evidence, audit JSONs, codex transcripts).
- `FalCloud` tier resolves to `effective_status == READY` and `--plan-tier FalCloud` returns regular `PLAN` (no longer `TIER_KEY_OK_SHIM_PENDING`) after the tier-config flip.
- Negative-path probes pass (6/6 structured failures with stable status enums).
- Two consecutive empty `/codex:adversarial-review` runs at silent-twice (model `gpt-5.5`).
- Cert minted with all doctrine rule IDs (P/S/D/PT/O/E/A/C) populated.
- PR opened against `bermingham85/code-artifacts:main`, stacked on PR #22 (ANIM-16) — operator-merge gated per branch protection.

## Codex commands required

| Stage | Command | Expected outcome |
|---|---|---|
| Diff | `CODEX_MODEL=gpt-5.5 codex exec --model gpt-5.5 --skip-git-repo-check --cd /c/Users/Owner/Repos/code-artifacts < bundle.txt > round<n>.txt` | silent-twice (≤5 fix rounds per R16 cap) |
| Ship gate | Single clean `codex exec` run on final diff | clean |

Transcripts persisted to `apex_governance/codex_runs/ANIM-18/round<n>.txt`.

## Governance hooks

- WO drop: covered by parent `APEX-ANIM-MB-WO-00001`.
- Naming gate: `muscle_fal_shim.py` matches existing `muscle_*` prefix; `APEX-MB-PY-00118` registered in DOCUMENT_REGISTER.md at pre-flight (this commit).
- Pipeline-governance audit: 12/12 required at post-phase.
- Watchdog: shim is short-lived (one HTTP call per shot), no long-running registration required.

## Test plan

- Unit (in-line in shim): payload-build determinism — assemble two payloads for the same shot, assert byte equality.
- Negative probes: 6 structured-failure paths produce stable status enums + non-zero exit codes; no key bytes leak.
- Live-mode safety: default `--submit` without `--live` performs zero HTTP call (probe harness asserts `urllib.request.urlopen` was not invoked under default flag).
- Smoke: `--probe` against the test fal endpoint returns the auth-shape result (or `FAL_ENDPOINT_UNREACHABLE` cleanly if offline); fingerprint matches ANIM-17 fingerprint (`95de:0714`).
- Integration: ANIM-16 bulk-plan + ANIM-18 `--build-payload` for one Grog shot produces a payload JSON that round-trips through `json.loads()` and contains every expected field (`prompt`, `image_url`, `aspect_ratio`, `duration`, `key_fingerprint`).

## Pass criteria

- [ ] Shim builds and `--help` shows 4 modes.
- [ ] Payload-build determinism test passes.
- [ ] 6 negative-path probes pass with stable status enums.
- [ ] Default `--submit` (no `--live`) issues zero HTTP calls.
- [ ] Leak check: grep for `FAL_AI_API_KEY` bytes returns zero hits in any persisted artifact.
- [ ] Tier-config flip leaves FalCloud at `effective_status == READY`.
- [ ] Silent-twice on `/codex:adversarial-review` (≤5 fix rounds).
- [ ] Cert + tag + handover + PR opened.

## Handover spec

- New paths: `apex/registry/muscle_fal_shim.py`, `apex/docs/anim/ANIM-18-evidence.json`, `apex/audit/anim-18/probe_negatives.py`, `apex/docs/spec/SPEC-ANIM-18.md`, `apex/docs/qa/QA-ANIM-18.md`.
- New env vars / secrets: none (reuses ANIM-17 `FAL_AI_API_KEY` in env_sync).
- New muscles: APEX-MB-PY-00118 `muscle_fal_shim.py`.
- New scheduled tasks: none (shim is invoked on-demand from the tier-config wrapper_invocation).
- Anything next phase should NOT redo: do not introduce a second env-key helper; do not extend `muscle_video_agent.py`; do not change the FalCloud static `status` (let runtime drive it via shim_status + wrapper_invocation).
- Risks: live API spend if operator forgets dry-run safety (gated behind explicit `--live` flag); fal.ai API shape changes (covered by 6-probe negative harness — failure surfaces as stable status, not crash).
- Pointer: CERT-ANIM-18 at issue.

## Rollback plan

- Trigger: shim breaks live render burst; or fal.ai changes API surface in a way the shim misclassifies.
- Revert: `git revert <ANIM-18-merge-commit>` — flips tier-config FalCloud back to `shim_status: PENDING` + `wrapper_invocation: null`; FalCloud falls back to `TIER_KEY_OK_SHIM_PENDING` (the ANIM-17 state).
- Data restoration: none (no persistent data introduced; no DB rows).
- Notification: handover updated; cert revoked from `certs/index.json`.

## Doctrine conformance table

| Rule | Evidence |
|---|---|
| P (Plan) | This SPEC; `apex/docs/anim/ANIM-18-evidence.json` payload schema |
| S (Spec) | This file (full sections); SPEC-ANIM-17.md inheritance |
| D (Doctrine) | `CLAUDE_CODEX_DOCTRINE` reviewer-of-record Codex CLI under ChatGPT-account auth `CODEX_MODEL=gpt-5.5` |
| PT (Pre-Test) | `apex/audit/anim-18/probe_negatives.py` written before shim build |
| O (Output) | Outputs section enumerated above |
| E (Evidence) | `ANIM-18-evidence.json` + transcripts |
| A (Audit) | `apex/audit/anim-18/` JSONs |
| C (Cert) | `apex_governance/certs/CERT-ANIM-18.json` populated post silent-twice |

## Lifecycle modes matrix

| Mode | Rules | Evidence | Status |
|---|---|---|---|
| Plan | P, S | SPEC-ANIM-18.md | DONE at this writing |
| Build | S, D | shim + tier-config edit | TO BE COMPLETED in build stage |
| Use | O, E | dry-run + (operator-gated) live HTTP probe | DONE at this writing for dry-run; live path operator-gated |
| Maintain | A, C | cert + handover + 6-probe harness re-runnable | DONE at cert mint |

## Cleanup

- No sandbox dir created.
- No scratch dir created.
- Evidence file holds all transient leak-check artifacts.
- No legacy paths touched.
