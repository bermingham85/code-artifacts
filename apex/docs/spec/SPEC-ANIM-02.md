# SPEC-ANIM-02 — Install/verify missing models + governance plumbing

## Identity
- Phase ID: `ANIM-02`
- Title: Install HunyuanVideo + kohya_ss; dedupe duplicate LoRAs; register music-video muscles; add SP-ANIM to subprojects; correct WO R20 mislabel.
- Parent subproject: `ANIM` (per WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator (Claude Opus 4.7)
- Depends-on: `ANIM-01` (capability map, handover at `apex_governance/handovers/ANIM-01.handover.md`)
- Blocks: `ANIM-03` (Character-Build agent uses kohya_ss for per-character LoRA training — optional path; FLUX Kontext path is independent), `ANIM-05` (HunyuanVideo for physics-heavy shots — optional path; Wan 2.2 i2v is independent).
- Reference patterns followed (PLAN_CRITERIA §11): `apex/PROJECT_APEX_v2.2.md`; ANIM-01 capability-map handover §5–§7.
- Branch: `phase/ANIM-02`
- Cert tag at completion: `cert/ANIM-02@<sha>`

## Context window budget
- Token budget: documentation + small install scripts; spec ≤300 LOC; ≤8 files committed.
- Files in scope (≤8):
  1. `apex/docs/spec/SPEC-ANIM-02.md` (this file)
  2. `apex/docs/DOCUMENT_REGISTER.md` (append 3 rows for music-video muscles)
  3. `apex_governance/SUBPROJECTS.md` (append SP-ANIM section)
  4. `apex/registry/muscle_install_hunyuanvideo.py` (install script; idempotent; logs to `apex/audit/anim-02/`)
  5. `apex/registry/muscle_install_kohya_ss.py` (install script; idempotent)
  6. `apex/registry/muscle_lora_dedup.py` (dedup by SHA256; quarantines duplicates to `C:/ComfyUI/models/loras/_quarantine/ANIM-02/`)
  7. `apex/docs/anim/ANIM-02-install-evidence.json` (machine-readable proof for verification)
  8. `apex/docs/anim/ANIM-02-WO-corrections.md` (records F6 R20 mislabel correction; does NOT edit operator-owned WO file directly)
- Files explicitly out of scope: live model file downloads to `C:/ComfyUI/models/` (operator-gated for bandwidth), edits to `C:/Users/Owner/Documents/Claude/Projects/breaking down complex tasks/APEX-ANIM-Production-System.md` (operator-owned).
- External documents loaded: `apex/docs/capability/ANIM-01-capability-map.md`, `apex_governance/handovers/ANIM-01.handover.md`, `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.rules.json`.

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-02` | RW | env_sync GitHub PAT |
| APEX root | `C:\Users\Owner\Repos\code-artifacts\apex\` | RW | local |
| Governance | `C:\Users\Owner\apex_governance\` | RW | local |
| ComfyUI custom_nodes | `C:\ComfyUI\custom_nodes\` | RW | local |
| ComfyUI models | `C:\ComfyUI\models\` | RW (LoRA quarantine only) | local |
| kohya_ss install root | `C:\Users\Owner\Tools\kohya_ss\` | RW | local |
| HunyuanVideo nodes | `C:\ComfyUI\custom_nodes\ComfyUI-HunyuanVideoWrapper\` (or equivalent) | RW | local |
| Codex CLI | `codex-cli 0.135.0` with `CODEX_MODEL=gpt-5.5` | invoke | local |
| Secrets | `X:\env_sync\*.json` | R | local |
| HF token | `HF_TOKEN` from `X:\env_sync\user_portable.json` (for gated HunyuanVideo weights if needed) | R | env_sync |

Unresolved rows: HF_TOKEN — to be resolved from env_sync at install time; if missing, install script writes to `MISSING_SECRETS.queue.json` and the model-download step defers without blocking the LoRA dedup + governance plumbing.

## Inputs
- ANIM-01 cert (Codex silent-twice rounds 11+12): `C:/Users/Owner/apex_governance/certs/CERT-ANIM-01.json`.
- ANIM-01 handover: `C:/Users/Owner/apex_governance/handovers/ANIM-01.handover.md`.
- LoRA candidate-duplicates (4 files, all SHA256 prefix `ef5b51ba69f72dce`, size 343,806,384 bytes — confirmed identical 2026-06-07T04:57Z by `hashlib.sha256` + `os.path.getsize`):
  - `C:/ComfyUI/models/loras/kontext-turnaround-sheet-v1.safetensors` (canonical, KEEP)
  - `C:/ComfyUI/models/loras/kontext-turnaround-sheet-v1 (1).safetensors` (QUARANTINE)
  - `C:/ComfyUI/models/loras/kontext-turnaround-sheet-v1 (2).safetensors` (QUARANTINE)
  - `C:/ComfyUI/models/loras/kontext-turnaround-sheet-v1 (3).safetensors` (QUARANTINE)
- DOCUMENT_REGISTER.md last refcode = `APEX-MB-PY-00105` (2026-06-06). Next 3: `APEX-MB-PY-00106`, `..00107`, `..00108`.

## Outputs
- Code paths: 3 new `apex/registry/muscle_*.py` install/dedup scripts (each ≤80 LOC, pure stdlib + `subprocess` only).
- Doc paths: `SPEC-ANIM-02.md`, `DOCUMENT_REGISTER.md` (3-row append), `SUBPROJECTS.md` (SP-ANIM section append), `apex/docs/anim/ANIM-02-install-evidence.json`, `apex/docs/anim/ANIM-02-WO-corrections.md`.
- Cert path: `C:/Users/Owner/apex_governance/certs/CERT-ANIM-02.json`.
- Handover path: `C:/Users/Owner/apex_governance/handovers/ANIM-02.handover.md`.
- QA evidence: install-evidence JSON anchors every install claim to a verifiable file path (custom_nodes dir exists, kohya CLI returns version, etc.).

## Definition of Done (objective)
- **Governance plumbing**:
  - DOCUMENT_REGISTER.md contains 3 new rows: APEX-MB-PY-00106 `muscle_music_video.py`, APEX-MB-PY-00107 `muscle_mv_regenerate.py`, APEX-MB-PY-00108 `stitch_video.py`, all status ACTIVE, all path `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/`.
  - SUBPROJECTS.md contains a `## SP-ANIM. Animation production system` section with ANIM-01..ANIM-07+ enumerated and the same lifecycle wording as SP-A..SP-J.
  - `ANIM-02-WO-corrections.md` records F6 (R20 mislabel in WO §0): the WO says "R20 (no guessing / preserve detail)" but `CLAUDE_CODEX_DOCTRINE.rules.json` defines R20 as "Stuck-loop re-research". The WO's intent matches `R-future` policy intent; correction is filed as a finding awaiting operator merge of the WO document (operator-owned file; not edited by APEX).
- **LoRA dedup (G1)**:
  - `muscle_lora_dedup.py --dry-run` reports the 3 duplicate files and their identical SHA256 + size.
  - Live run quarantines (moves, does not delete) the 3 duplicates to `C:/ComfyUI/models/loras/_quarantine/ANIM-02/` preserving original filenames; quarantine manifest written to `apex/audit/anim-02/lora-dedup.json` with source path, sha256, size, timestamp per file.
- **HunyuanVideo + kohya_ss install scripts (G4, G5)**:
  - `muscle_install_kohya_ss.py` clones `https://github.com/bmaltais/kohya_ss` to `C:/Users/Owner/Tools/kohya_ss/`, runs its setup batch, verifies via `python kohya_ss/sd-scripts/sdxl_train_network.py --help` returning exit 0. Idempotent: if dir exists, runs `git pull` then re-verifies.
  - `muscle_install_hunyuanvideo.py` clones `https://github.com/kijai/ComfyUI-HunyuanVideoWrapper` to `C:/ComfyUI/custom_nodes/ComfyUI-HunyuanVideoWrapper/`, runs its `pip install -r requirements.txt` against the ComfyUI venv, and lists the required weight files with HuggingFace download commands gated behind an explicit `--download-weights` flag (operator gate on the multi-GB pull; verification of nodes-only install does not require weights).
  - Both scripts log to `apex/audit/anim-02/install-<tool>-<ts>.json` with command, exit code, stdout/stderr tail, verification step.
- **Codex adversarial-review** to silent-twice on the spec + diff bundle (`CODEX_MODEL=gpt-5.5`, transcripts to `apex_governance/codex_runs/ANIM-02/`).
- **Work gate**: WARN or PASS allowed (work_gate audit captured).
- **PR**: opened via `_make_pr_api.py`; merge_status `OPEN_FOR_OPERATOR_MERGE` (same constraint as ANIM-01 per branch protection MA-ANIM-001).
- **Cert + handover**: minted, appended to `certs/index.json` (created if absent per MA-AGEN-003).

## Codex commands required
| Stage | Command | Background | Expected |
|---|---|---|---|
| Spec | `CODEX_MODEL=gpt-5.5 codex exec --send-stdin --include-paths apex/docs/spec/SPEC-ANIM-02.md --prompt "adversarial-review for spec defects only; severity CRITICAL/HIGH only"` | no (small) | silent-twice |
| Diff | same, paths = the 8 files | no | silent-twice |

Persist every transcript to `apex_governance/codex_runs/ANIM-02/round<n>.txt`.

## Governance hooks
- WO drop: not used in ANIM-* chain (WO is the operator's `APEX-ANIM-MB-WO-00001`).
- Naming gate: all 3 new files match `apex/registry/muscle_*.py` pattern; conforms to APEX-MB-DOC-00001 NAMING_CONVENTION v1.1.
- Doc control: DOCUMENT_REGISTER rows reserved before any `apex/registry/*.py` write to satisfy `apex_governance_enforcer.py` PreToolUse hook (MEMORY.md note: `[[reference_apex_dual_register_drift]]`).
- Pipeline-governance audit: not run in ANIM-02 (script size <100 LOC; pipeline-governance is for end-to-end pipelines).

## Test plan
- Unit (`muscle_lora_dedup.py`): `--dry-run` against the 4 LoRA paths returns 3 duplicates of canonical, exit 0.
- Integration (HunyuanVideo): after install, list `ls C:/ComfyUI/custom_nodes/ComfyUI-HunyuanVideoWrapper/` non-empty; presence of `__init__.py` and `nodes.py` (or equivalent); pip freeze contains the dependency lines from requirements.txt.
- Integration (kohya): `python -c "import sys; sys.path.insert(0,'C:/Users/Owner/Tools/kohya_ss/sd-scripts'); import library.train_util" returns exit 0.
- Smoke: `git status -s` clean on `phase/ANIM-02` after all writes, work-gate audit JSON written.

## Pass criteria (binary)
- [ ] DOCUMENT_REGISTER.md has 3 new rows.
- [ ] SUBPROJECTS.md has SP-ANIM section.
- [ ] ANIM-02-WO-corrections.md records F6.
- [ ] 3 duplicate LoRAs moved to quarantine; manifest written.
- [ ] Both install scripts run idempotently and verify.
- [ ] Codex silent-twice rounds archived.
- [ ] PR opened.
- [ ] Cert written; certs/index.json appended.
- [ ] Handover written; ANIM-03 pre-flight able to cite it.

## Rollback plan
- Trigger: install script verification fails OR Codex silent-twice unreachable after 8 rounds (R16 cap).
- Procedure: `git restore apex/docs/spec/SPEC-ANIM-02.md apex/docs/DOCUMENT_REGISTER.md`, revert `apex_governance/SUBPROJECTS.md` append, restore LoRA quarantine to original locations from manifest.
- Data restore: LoRA quarantine manifest contains original paths; `muscle_lora_dedup.py --restore <manifest>` moves them back.
- Notification: append to `apex_governance/findings/ANIM-02.findings.md`.

## Doctrine conformance (cited at cert time)
- P3 (silent-twice loop): rounds and transcripts in cert.
- O2 (model deliberate): every Codex call uses `CODEX_MODEL=gpt-5.5` per MA-AGEN-004 known issue.
- O6 (persist transcripts): `apex_governance/codex_runs/ANIM-02/round<n>.txt`.
- O9 (no ship without clean review): adversarial silent-twice + PR review request.
- A4 (no Claude self-review): not invoked.

## Lifecycle modes
| Mode | Evidence file | Status |
|---|---|---|
| Plan | SPEC-ANIM-02.md | DONE on commit |
| Build | install scripts + DOCUMENT_REGISTER + SUBPROJECTS appends | DONE on commit |
| Use | install scripts invoked from ANIM-03 / ANIM-05 pre-flights | DEFERRED |
| Maintain | scripts idempotent; ANIM-07 follow-on for periodic version-drift check | DEFERRED_TO_ANIM_07 |

## Cleanup report (filled at cert time)
- Files deleted: none planned.
- Files renamed: none planned.
- Paths reconciled: none planned.
- Sandbox dir empty: N/A (no sandbox use).
- Scratch dir empty: N/A.
