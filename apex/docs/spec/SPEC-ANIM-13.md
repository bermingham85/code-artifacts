# SPEC-ANIM-13 — Shot/Storyboard agent (S5 deterministic shot-skeleton from lyrics)

## Identity
- Phase ID: `ANIM-13`
- Title: Shot/Storyboard agent — deterministic shot-skeleton generation from time-aligned lyrics + character bible + scene bible.
- Parent subproject: `ANIM` (WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator (Claude Opus 4.7)
- Depends-on: `ANIM-03` (reference-pack manifest with character bible paths + identifier strings), `ANIM-04` (scene-pack manifest with brand_tokens + style_anchor), Whisper-style `lyrics_timestamped.json` for the song.
- Blocks: future ANIM-1X passes that wire the storyboard into ANIM-05 video-agent tier-plans for new songs (e.g. Lirian bibles + future MV).
- Reference patterns: `apex/registry/muscle_video_agent.py` (sibling agent shape, slug regex bounds, manifest+audit format), `apex/registry/muscle_environment_agent.py` (catalog mode), `apex/registry/muscle_assembly_agent.py` (lyrics_timestamped.json reader).
- Branch: `phase/ANIM-13-shot-storyboard` (stacked on `phase/ANIM-12-AGEN-router`)
- Cert tag: `cert/ANIM-13@<sha>`

## Why ANIM-13 (WO §3 gap)

The WO §3 explicitly lists six agents APEX must build. By ANIM-12 we have built:

| WO §3 agent | Stage | Built where |
|---|---|---|
| Character-Build | S1-S3 | ANIM-03 (extended in ANIM-07) |
| Environment/Imagery | S4 | ANIM-04 |
| **Shot/Storyboard** | **S5** | **NOT BUILT (this phase)** |
| Video | S6 | ANIM-05 |
| Assembly/QC | S7-S8 | ANIM-06 |
| Core five (Spec/Verif/Arch/Build/Router) | governance | ANIM-08..12 |

ANIM-05 cataloged Grog's pre-existing 38-clip set; Grog had a hand-authored `shot_list.json` so the storyboard step was implicit. For any future song (e.g. a Lirian MV, a new Galinda song) there is no agent that takes lyrics + bibles and produces the structured shot list that the Video agent's `--plan-tier` consumes. ANIM-13 closes that gap.

## Context window budget
- ≤8 files committed; ≤500 LOC across them.
- Files in scope:
  1. `apex/docs/spec/SPEC-ANIM-13.md` (this)
  2. `apex/docs/DOCUMENT_REGISTER.md` (+1 row APEX-MB-PY-00117 — already added in prep commit)
  3. `apex/registry/muscle_shot_storyboard_agent.py` (the agent)
  4. `apex/docs/anim/ANIM-13-projects.json` (project→character/scene/lyrics binding)
  5. `apex/docs/anim/ANIM-13-storyboard-grog_playground.json` (deterministic skeleton for the Grog MV — committable proof of output)
  6. `apex/docs/anim/ANIM-13-validation-grog.json` (gold-reference validation report against Grog hand-authored `shot_list.json`)
  7. `apex/docs/anim/ANIM-13-evidence.json`
  8. `apex/audit/anim-13/` (audit JSONs from runs)
- Out of scope: live LLM call to fill `kontext_prompt` creative content (that is downstream / operator-gated — agent emits templates only); training new shot-segmentation models; any music-analysis (downbeat detection, etc.) — the agent reads the existing section table and lyric line timings only.

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-13-shot-storyboard` | RW | env_sync GitHub PAT |
| ANIM-03 reference pack manifest | `apex/docs/anim/ANIM-03-reference-pack-manifest.json` | R | local |
| ANIM-04 scene-pack manifest | `apex/docs/anim/ANIM-04-scene-pack-manifest.json` | R | local |
| Grog lyrics_timestamped | `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/lyrics_timestamped.json` | R | local |
| Grog gold shot_list (validation) | `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json` | R | local |
| Codex | gpt-5.5 | invoke | local |

## Inputs

A **project** is the smallest unit the agent operates on: one song MV bound to one character + one scene + one lyric-timing file. Project list lives at `apex/docs/anim/ANIM-13-projects.json` and binds:

```
{
  "projects": {
    "<slug>": {
      "brand": "<brand_name>",
      "character": "<character slug, must exist in ANIM-03 manifest>",
      "scene": "<scene slug, must exist in ANIM-04 manifest>",
      "song_title": "<human title>",
      "lyrics_timestamped_path": "<absolute path>",
      "gold_shot_list_path": "<absolute path or null>",
      "duration_seconds": <float>,
      "sections": [ {"name":"intro","start":0.0,"end":11.5,"energy":"LOW","mood":"..."}, ... ]
    }
  }
}
```

Section table is required (the same shape used in the Grog shot_list.json — `[{name,start,end,energy,mood}, ...]`).

## Outputs

`apex/registry/muscle_shot_storyboard_agent.py` (APEX-MB-PY-00117). Modes:

- `--list-projects`: prints the configured project bindings.
- `--storyboard <project> [--target-shot-seconds N] [--force]`: builds the deterministic storyboard JSON for the project and writes `apex/docs/anim/ANIM-13-storyboard-<project>.json`. Default shot length 5.5s.
- `--validate <project>`: requires `gold_shot_list_path` non-null; reads the gold shot_list.json, runs the same segmentation, and writes `apex/docs/anim/ANIM-13-validation-<project>.json` with overlap statistics (shot count agreement, mean section-boundary error, mean shot-boundary error).

### Storyboard JSON shape

```
{
  "phase": "ANIM-13",
  "schema_version": 1,
  "project": "<slug>",
  "song_title": "...",
  "character": "<slug>",
  "scene_slug": "<slug>",
  "brand": "...",
  "duration_seconds": ...,
  "target_shot_seconds": ...,
  "character_markers": "<from ANIM-03 bible identifier string>",
  "scene_markers": "<from ANIM-04 scene bible prompt>",
  "style_anchor": "<from ANIM-04 brand_tokens>",
  "prompt_rules": "<from ANIM-04 brand_tokens>",
  "shots": [
    {
      "id": 1,
      "section": "intro",
      "start": 0.0, "end": 5.5,
      "lyric": "<verbatim from lyrics_timestamped lines whose start in [shot.start, shot.end), or '' if instrumental>",
      "lyric_word_count": 0,
      "energy": "LOW",
      "mood": "...",
      "camera_preset": "<from energy→preset map>",
      "wan_motion_preset": "<from energy→motion map>",
      "kontext_prompt_template": "<deterministic skeleton joining markers + {action_placeholder} + style_anchor>",
      "needs_fill": ["action"]
    },
    ...
  ]
}
```

### Energy→preset map (deterministic)
- LOW → camera `"slow drift, golden tones, steady frame"`, motion `"slow ambient drift, subtle micro-motion, gentle environmental movement"`.
- MED → camera `"medium shot, soft push, character framing"`, motion `"focused character action, mid-tempo gestural movement, environment reacting"`.
- HIGH → camera `"dynamic angle, push-in or whip pan, bold framing"`, motion `"strong character action, impact beats, environment dramatically reacting"`.

These are the same vocabulary the hand-authored Grog `shot_list.json` uses (see `wan_motion` and `camera` fields).

### Segmentation algorithm (deterministic, no LLM)

For each section in the project's section table, with `target_shot_seconds = T` (default 5.5):
1. `section_duration = section.end - section.start`.
2. `n_shots = max(1, round(section_duration / T))`. **Sections of any length get ≥1 shot.**
3. `shot_duration = section_duration / n_shots`. Shots are equal-width slices of the section. This is the simplest possible deterministic mapping; it diverges from hand-authored shot lists in details but matches the **total shot count and section boundaries** which is what's needed downstream for tier-plan + assembly.
4. For each shot window `[start, end)`, gather lyric lines from `lyrics_timestamped.json` whose `start` falls inside, concatenate the `text` fields (verbatim, no edits), and count words for telemetry.
5. Energy + mood are inherited from the section. Camera + motion are looked up from the energy map.

## Definition of Done
- `apex/docs/anim/ANIM-13-projects.json` registers ≥1 project (`grog_playground`) with the actual lyrics + gold shot list paths.
- `--storyboard grog_playground` produces `apex/docs/anim/ANIM-13-storyboard-grog_playground.json` with N>0 shots covering the full song duration with no gaps.
- `--validate grog_playground` produces `apex/docs/anim/ANIM-13-validation-grog.json` with:
  - emitted shot count
  - gold shot count
  - section-boundary deltas (max + mean, seconds)
  - overall coverage ratio
- Agent enforces slug regex bounds and rerun-guards with WILL_OVERWRITE_REFUSED (sibling pattern).
- Codex silent-twice under R15.
- PR opened; cert + handover written; certs/index.json appended; tag `cert/ANIM-13@<sha>` on merge.

## Codex commands
Same gpt-5.5 inline-stdin pattern used since ANIM-01; persist transcripts to `apex_governance/codex_runs/ANIM-13/round<n>.txt`. `CODEX_MODEL=gpt-5.5 codex exec --model gpt-5.5 < bundle.txt > round<n>.txt`. Silent-twice = two consecutive rounds with no HIGH findings.

## Test plan
- `--list-projects` → prints registered project(s) with character + scene + brand.
- `--storyboard grog_playground` → emits the storyboard JSON; sanity-check: 30–60 shots over 238.9s with target_shot_seconds=5.5 puts the count around 43; first shot starts at 0.0; last shot ends at 238.9 within float tolerance.
- `--storyboard '../etc'` → INVALID_SLUG exit 6.
- `--storyboard grog_playground` again without `--force` → WILL_OVERWRITE_REFUSED exit 5.
- `--validate grog_playground` → produces validation JSON with both shot counts + section-boundary deltas; deltas should be 0 (the agent reads the same section table the gold was authored against).

## Pass criteria
- [ ] Storyboard emitted for grog_playground covering full duration, no gaps, ≥30 shots.
- [ ] Validation report compares emitted to gold (38 shots) with quantitative deltas.
- [ ] All paths/slugs regex-bound; idempotency guard fires.
- [ ] DOCUMENT_REGISTER row APEX-MB-PY-00117 present (added pre-write).
- [ ] Codex silent-twice on the diff bundle.
- [ ] PR + cert + handover + index entry.

## Rollback plan
- `git restore` the 8 files; no live filesystem mutation outside `apex/audit/anim-13/` and `apex/docs/anim/ANIM-13-*.json`.
- Notification: `apex_governance/findings/ANIM-13.findings.md`.

## Doctrine conformance
- **P3** (no invention): all creative content (the kontext_prompt body) stays as templated placeholders with explicit `needs_fill` markers. Agent only assembles structural skeletons from verifiable sources (lyrics file, character markers from ANIM-03 bible, scene markers from ANIM-04 bible).
- **R15** (silent-twice): codex_runs/ANIM-13/round1+round2 must be HIGH-empty.
- **R16** (loop cap): max 5 fix rounds; escalate on overage.
- **O2/O6/O9** (output controls): manifest schema_version; ISO8601 UTC `built_at`; audit JSON per run with status field.
- **R20** (preserve detail): lyric text copied verbatim from lyrics_timestamped.json `text` fields; no truncation or rephrasing.

## Lifecycle modes
| Mode | Evidence | Status |
|---|---|---|
| Plan | this spec | DONE |
| Build | agent + projects.json + storyboard + validation + evidence | DONE |
| Use | future MV phases will call `--storyboard <project>` then pass output to ANIM-05 video agent | DEFERRED |
| Maintain | add new projects via `apex/docs/anim/ANIM-13-projects.json`; update camera/motion presets if Pixar-style brand-token vocabulary changes | DEFERRED |
