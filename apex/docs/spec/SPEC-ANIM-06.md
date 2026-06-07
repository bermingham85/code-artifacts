# SPEC-ANIM-06 — Assembly agent + first-visible-deliverable cert (Grog MP4)

## Identity
- Phase ID: `ANIM-06`
- Title: Assembly/QC agent + cert registration of the Grog music video as the WO's first visible deliverable.
- Parent subproject: `ANIM` (WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator (Claude Opus 4.7)
- Depends-on: `ANIM-05` (clip-pack manifest).
- Blocks: ANIM-07+ scaling.
- Reference patterns: `apex/registry/muscle_video_agent.py` (sibling shape), `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/muscle_music_video.py` (`--mode stitch`) + `stitch_video.py` (registered APEX-MB-PY-00106/00108) — the real assembly route per ANIM-01 §0.1 (NOT the WO's aspirational `music_video_pipeline/assemble_video.py`).
- Branch: `phase/ANIM-06`
- Cert tag: `cert/ANIM-06@<sha>`

## Context window budget
- ≤8 files committed.
- Files in scope:
  1. `apex/docs/spec/SPEC-ANIM-06.md`
  2. `apex/docs/DOCUMENT_REGISTER.md` (+1 row APEX-MB-PY-00115)
  3. `apex/registry/muscle_assembly_agent.py`
  4. `apex/docs/anim/ANIM-06-assembly-manifest.json` (output)
  5. `apex/docs/anim/ANIM-06-evidence.json`
  6. `apex/audit/anim-06/` (audit JSONs)
- Out of scope: live ffmpeg re-stitch (already done — shipped MP4 exists); Supabase QC tracking (G10 operator-gated).

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` `phase/ANIM-06` | RW | env_sync GitHub PAT |
| Shipped MP4 | `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/grog_too_big_for_playground_mv.mp4` | R | local |
| Lyrics timestamps | `X:/.../grog_playground/lyrics_timestamped.json` | R | local |
| ANIM-05 manifest | `apex/docs/anim/ANIM-05-clip-pack-manifest.json` | R | local |
| Real stitch path | `X:/.../grog_playground/muscle_music_video.py --mode stitch` + `stitch_video.py` | R (path only) | local |

## Inputs
- The Grog MP4 (47,983,724 bytes; sha256 `dbd657f511f0bc46be6aa7ff9185fe6c23bef6c3939945a3fd8eaf85845ecdb8`).
- ANIM-05 clip-pack manifest with 38 clip entries + per-clip duration mapped to `shot_list.json` shot ids.
- `lyrics_timestamped.json` (per-shot lyric line + timing — confirmed present in clips dir listing 2026-06-07).
- PHASE_STATE.json quote: *"20/20 complete — 19 Wan2.2 i2v two-stage MoE + 1 skip (existing). Zero errors."*

## Outputs
- **Assembly agent** at `apex/registry/muscle_assembly_agent.py` (APEX-MB-PY-00115). Modes:
  - `--catalog-deliverable <slug>`: register the shipped MP4 for a scene as the deliverable; emits assembly manifest entry with sha256+size+duration_seconds+clip_count.
  - `--plan-concat <slug>`: dry-run that prints the ffmpeg concat list given the ANIM-05 clip-pack production set, ordered by clip index, using the canonical `stitch_video.py` wrapper invocation.
  - `--list-deliverables`: lists registered deliverables.
- **Assembly manifest** at `apex/docs/anim/ANIM-06-assembly-manifest.json`.
- **Evidence** at `apex/docs/anim/ANIM-06-evidence.json`.
- **Audit**: `apex/audit/anim-06/`.

## Definition of Done
- Assembly manifest registers Grog MP4 as the MagicalRealmPlayground deliverable.
- Concat plan reproduces the 20-clip production-set order from the ANIM-05 manifest.
- Agent path/regex-bounded + symlink-refusing + handle-bound hash (same safety pattern as ANIM-05).
- Codex silent-twice under R15.
- PR + cert + handover + certs/index.json appended.

## Test plan
- `--catalog-deliverable MagicalRealmPlayground` → registers MP4 with expected sha256 + size 47,983,724.
- `--plan-concat MagicalRealmPlayground` → emits a 20-line concat plan in clip index order.
- `--catalog-deliverable '../etc'` → INVALID_SLUG exit 6.
- Rerun guard: `--catalog-deliverable MagicalRealmPlayground` twice → WILL_OVERWRITE_REFUSED exit 5.

## Pass criteria
- [ ] Assembly manifest contains MRP entry with sha256, size, duration.
- [ ] Concat plan = 20 clip paths in shot_id order.
- [ ] Agent safety surface matches ANIM-05's pattern.
- [ ] Codex silent-twice.
- [ ] PR + cert.

## Doctrine
- P3/R15/R16/O2/O6/O9 — same.
- Inherits ANIM-05's QNAP NAS trust assumption verbatim (same operator-controlled deployment); residual TOCTOU is the same policy contribution.

## Lifecycle
| Mode | Evidence | Status |
|---|---|---|
| Plan | this spec | DONE |
| Build | agent + assembly manifest + evidence | DONE |
| Use | ANIM-07+ scales the agent across more brands; QC tracking still operator-gated | DEFERRED |
| Maintain | re-catalog when deliverables are re-mastered | DEFERRED |
