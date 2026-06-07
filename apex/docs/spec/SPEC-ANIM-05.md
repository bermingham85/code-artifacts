# SPEC-ANIM-05 — Video agent (S6 image-to-video, tiered routing + clip catalog)

## Identity
- Phase ID: `ANIM-05`
- Title: Video agent that routes shots to Wan 2.2 / LTX / Hunyuan / fal.ai tiers; catalogs existing rendered clips.
- Parent subproject: `ANIM` (WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator (Claude Opus 4.7)
- Depends-on: `ANIM-03` (character reference packs), `ANIM-04` (scene-pack manifest), ANIM-02 (HunyuanVideo nodes installed).
- Blocks: `ANIM-06` (assembly consumes the clip-pack manifest produced here).
- Reference patterns: `apex/registry/muscle_character_build_agent.py` (sibling shape), `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/muscle_music_video.py` (the actual wrapped pipeline — modes `keyframes / animate / stitch / full`).
- Branch: `phase/ANIM-05`
- Cert tag: `cert/ANIM-05@<sha>`

## Context window budget
- ≤8 files committed; ≤500 LOC across them.
- Files in scope:
  1. `apex/docs/spec/SPEC-ANIM-05.md` (this)
  2. `apex/docs/DOCUMENT_REGISTER.md` (+1 row APEX-MB-PY-00114)
  3. `apex/registry/muscle_video_agent.py` (the agent)
  4. `apex/docs/anim/ANIM-05-tier-config.json` (tier metadata: model, vram, speed, cost)
  5. `apex/docs/anim/ANIM-05-clip-pack-manifest.json` (output: cataloged clips per scene/character)
  6. `apex/docs/anim/ANIM-05-evidence.json`
  7. `apex/audit/anim-05/` (audit JSONs)
- Out of scope: live rendering of new clips (heavy — minutes per clip, multi-GB VRAM); fal.ai network call (G9 — key-resolution route TBD).

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-05` | RW | env_sync GitHub PAT |
| Existing Grog clips | `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/clips/` | R | local |
| Real wrapper script | `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/muscle_music_video.py` (APEX-MB-PY-00106) | R (path only — not invoked in this phase) | local |
| ANIM-03 manifest | `apex/docs/anim/ANIM-03-reference-pack-manifest.json` | R | local |
| ANIM-04 manifest | `apex/docs/anim/ANIM-04-scene-pack-manifest.json` | R | local |
| Codex | gpt-5.5 | invoke | local |
| HF_TOKEN | `X:/env_sync/user_portable.json` (for HunyuanVideo weight pull — operator-gated) | R | env_sync |
| fal.ai key | TBD (G9) | R | env_sync (resolution route to be wired in ANIM-05 follow-on) |

## Inputs
- ANIM-03 / ANIM-04 manifests on disk.
- 38 existing clips at `clips/` (per `ls` 2026-06-07). PHASE_STATE.json `session_2026_04_01_mv.shots` quote: *"20/20 complete — 19 Wan2.2 i2v two-stage MoE + 1 skip (existing). Zero errors."* — first 20 of the 38 are the final shipped Wan 2.2 i2v set; the remaining 18 are tests or alt takes that the agent will note as `extras`.
- `shot_list.json` for Grog at `X:/.../grog_playground/shot_list.json` (provides per-shot Kontext prompt + Wan motion + camera per the 38-shot original plan).

## Outputs
- **Agent** at `apex/registry/muscle_video_agent.py` (APEX-MB-PY-00114). Modes:
  - `--catalog <scene-slug>`: scans existing clips under the brand's known clip roots, emits a clip-pack manifest entry with sha256+size and durations (via simple file-size + filename inference, no external probes).
  - `--plan-tier <Wan22|LTX|Hunyuan|FalCloud>` `--shot <id>`: dry-run plan that prints the proposed render call (no execution); the live render is delegated to `muscle_music_video.py --mode animate` for Wan22/LTX/Hunyuan or to a placeholder fal.ai HTTP shim (operator-gated G9).
  - `--list-tiers`: prints the tier-config JSON.
- **Tier config** at `apex/docs/anim/ANIM-05-tier-config.json`: per-tier `{model, vram_gb, speed_minutes_per_clip, cost, best_for, status}`.
- **Clip-pack manifest** at `apex/docs/anim/ANIM-05-clip-pack-manifest.json`: per-character/per-scene/per-shot clip entries with sha256+size+source.
- **Evidence** at `apex/docs/anim/ANIM-05-evidence.json`.
- **Audit**: `apex/audit/anim-05/<scope>-<ts>.json`.

## Definition of Done
- Tier config records all 4 tiers with model names + status.
- Catalog mode produces a manifest entry with ≥1 clip and full sha256+size per entry.
- Agent enforces slug + scene-slug regex bounds (same shape as ANIM-04).
- Codex silent-twice under R15.
- PR opened; cert + handover written; certs/index.json appended.

## Codex commands
Same gpt-5.5 inline-stdin pattern; persist to `apex_governance/codex_runs/ANIM-05/`.

## Test plan
- `--list-tiers` → prints all 4 tiers.
- `--catalog MagicalRealmPlayground` → catalogs ≥20 clips (the first 20 are the production set per PHASE_STATE; the rest noted as extras).
- `--catalog '../etc'` → INVALID_SLUG exit 6.
- Idempotency: second `--catalog MagicalRealmPlayground` without `--force` returns WILL_OVERWRITE_REFUSED exit 5.

## Pass criteria
- [ ] Tier config covers Wan 2.2 / LTX / Hunyuan / fal.ai with explicit status.
- [ ] Clip-pack manifest contains the MagicalRealmPlayground entry with ≥20 clips.
- [ ] Agent path/regex-bounded; rerun-guarded.
- [ ] Codex silent-twice.
- [ ] PR + cert + handover.

## Rollback plan
- `git restore` the 8 files; no live filesystem mutation outside `apex/audit/anim-05/`.
- Notification: `apex_governance/findings/ANIM-05.findings.md`.

## Doctrine
- P3/R15/R16/O2/O6/O9 — same pattern.

## Lifecycle modes
| Mode | Evidence | Status |
|---|---|---|
| Plan | this spec | DONE |
| Build | agent + tier config + clip manifest + evidence | DONE |
| Use | ANIM-06 reads clip-pack manifest | DEFERRED |
| Maintain | new shots added via `--catalog` + tier overrides | DEFERRED |
