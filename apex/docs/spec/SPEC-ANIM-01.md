# SPEC-ANIM-01 — Capability Map (animation production system)

## Identity
- Phase ID: `ANIM-01`
- Title: Capability map of existing animation pipeline, models, agents, assets
- Parent subproject: `ANIM` (per WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator (Claude Opus 4.7)
- Depends-on: none (first phase of ANIM)
- Blocks: `ANIM-02` (model install/verify), `ANIM-03` (Character-Build agent)
- Reference patterns followed (PLAN_CRITERIA §11): `apex/PROJECT_APEX_v2.2.md`, `apex/registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/GOVERNANCE.md`, `apex/registry/clones/code-artifacts/AGENT_BUILD_SYSTEM/MASTER_HANDOVER.md`. WO authority: `apex_governance/PLAN_CRITERIA.md` §0 hierarchy; `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.md` R20 (no guessing / preserve detail).
- Branch: `phase/ANIM-01`
- Cert tag at completion: `cert/ANIM-01@<sha>`

## Context window budget
- Token budget: bounded to map deliverable only; spec ≤300 LOC text, ≤8 files committed.
- Files in scope:
  - `apex/docs/spec/SPEC-ANIM-01.md` (this file)
  - `apex/docs/capability/ANIM-01-capability-map.md` (deliverable)
  - `apex/docs/capability/ANIM-01-evidence.json` (machine-readable inventory)
- Files explicitly out of scope: model installs (ANIM-02), agent code (ANIM-03+), pipeline edits.
- External documents loaded: `APEX-ANIM-Production-System.md` (WO), `X:/Automations/apex/projects/jesse_animate/PHASE_STATE.json`, `X:/Automations/apex/projects/jesse_animate/PHASES.md`, `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json`.

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-01` | RW | env_sync GitHub PAT |
| APEX root | `C:\Users\Owner\Repos\code-artifacts\apex\` | RW | local |
| Governance | `C:\Users\Owner\apex_governance\` | RW | local |
| ComfyUI models | `C:\ComfyUI\models\` | R | local |
| jesse_animate | `X:\Automations\apex\projects\jesse_animate\` | R | local |
| Character source | `X:\characters\` | R | local |
| Codex CLI | `codex-cli 0.135.0` (`CODEX_MODEL=gpt-5.5`, ChatGPT-account auth) | invoke | local |
| Secrets | `X:\env_sync\*.json` | R | local |

Unresolved rows: none.

## Inputs
- WO: `C:\Users\Owner\Documents\Claude\Projects\breaking down complex tasks\APEX-ANIM-Production-System.md` (issued 2026-06-07).
- jesse_animate phase state: `X:\Automations\apex\projects\jesse_animate\PHASE_STATE.json`.
- jesse_animate phases doc: `X:\Automations\apex\projects\jesse_animate\PHASES.md`.
- grog_playground manifest: `X:\Automations\apex\projects\jesse_animate\music_video\grog_playground\shot_list.json`.

## Outputs
- Capability map (human): `apex/docs/capability/ANIM-01-capability-map.md`.
- Capability map (machine): `apex/docs/capability/ANIM-01-evidence.json`.
- Cert: `C:\Users\Owner\apex_governance\certs\CERT-ANIM-01.json`.
- Handover: `C:\Users\Owner\apex_governance\handovers\ANIM-01.handover.md`.
- Codex review transcripts: `C:\Users\Owner\apex_governance\codex_runs\ANIM-01\`.

## Definition of Done (objective and measurable)
- Pre-flight DoD: every pipeline / agent / model / asset named in the WO §2-§4 has either an evidence row (path + status) or is logged as a verified gap.
- Spec + ADR DoD: this SPEC plus the map document; Codex adversarial-review on the map returns silent-twice (two consecutive empty-finding runs). No ADR needed (pure inventory, no design choice).
- Build DoD: deliverables committed to `phase/ANIM-01`; no edits to other files.
- Test DoD: every claim in the map is backed by a concrete file path that exists at audit time (path-presence check).
- Cert DoD: `CERT-ANIM-01.json` minted with doctrine rule IDs (R20, P, O, A) populated.
- Handover DoD: `ANIM-01.handover.md` enumerates the gap list that ANIM-02..ANIM-07+ must consume.

## Codex commands required
| Stage | Command | Background | Expected |
|---|---|---|---|
| Map review | `codex exec --model gpt-5.5 "adversarial-review of ANIM-01-capability-map.md"` | no | silent-twice |
| Ship gate | `codex exec --model gpt-5.5 "review diff phase/ANIM-01"` | no | clean |

Transcripts persisted to `apex_governance/codex_runs/ANIM-01/<job-id>.txt`.

## Governance hooks
- WO drop: `APEX-ANIM-MB-WO-00001` already exists at the operator's planning path; no new drop needed for ANIM-01 itself.
- Naming gate: `name_enforcer.py` skipped for inventory-only docs (not registry artifacts); commits flagged for register reconciliation in ANIM-02.
- Prompt registry: no new prompts.
- Pipeline-governance audit: not applicable (no pipeline code touched).
- Watchdog: no new long-running component.

## Test plan
- Path-presence check: every path cited in `ANIM-01-evidence.json` resolves via `os.path.exists` or `git cat-file`.
- Codex adversarial-review on the map document until silent-twice.

## Pass criteria
- [x] Spec written, this file.
- [ ] Map document complete (real paths, sized inventory, gap list).
- [ ] Evidence JSON parseable, every path resolves.
- [ ] Codex review silent-twice.
- [ ] Cert minted + appended to `apex_governance/certs/index.json`.
- [ ] PR opened via `_make_pr_api.py`.
- [ ] Handover delivered.

## Handover document spec
See `apex_governance/handovers/ANIM-01.handover.md` — enumerates ANIM-02 inputs (LoRA de-dupe target list, missing-model install list, model-path confirmations) and warns ANIM-03+ about the WO's name-mismatch (scene-director / animation-agent / music_video_pipeline are aspirational labels — real names are `muscle_music_video.py`, `stitch_video.py`, `muscle_comfyui_runner`).

## Rollback plan
- Trigger: cert revoked, or capability map proven materially wrong.
- Revert: `git revert <ANIM-01 merge commit>`; remove cert from `certs/index.json`; reopen task #1.
- Data restoration: none — phase only adds documentation.
- Notification: append to `apex_governance/findings/ANIM-01.findings.md`.

## Doctrine conformance table
| Rule | Evidence |
|---|---|
| R20 (no guessing / preserve detail) | Every map row carries a real path; WO assumptions corrected against on-disk evidence (FLUX Kontext + Wan 2.2 already operational). |
| P (plan-before-build) | This SPEC precedes the map; no build code in ANIM-01. |
| O (one-source-of-truth) | Map is the single canonical inventory; jesse_animate PHASE_STATE.json is cited as the upstream of record. |
| A (audit trail) | Work-gate audit at `apex/audit/work_gate/2026-06-07T03-57-46Z-APEX.json`; cert + Codex transcripts persisted. |

## Lifecycle modes matrix
| Mode | Doctrine rules | Evidence | Status |
|---|---|---|---|
| Plan | P, R20 | this SPEC | DONE |
| Build | O | `ANIM-01-capability-map.md` + `ANIM-01-evidence.json` | IN-PROGRESS |
| Use | A | downstream phases (ANIM-02..07+) cite the map in their pre-flight | DEFERRED-to-next-phase |
| Maintain | A | map re-validated on every ANIM phase merge (path-presence check in CI follow-on WO) | DEFERRED-to-ANIM-07 |

## Cleanup report
- Files deleted: none (inventory phase).
- Files renamed: none.
- Paths reconciled: none.
- Stub/TODO/FIXME: none added.
- Sandbox dir: not used.
- Scratch dir: not used.
