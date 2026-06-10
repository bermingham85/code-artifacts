# SPEC-ANIM-16 — storyboard → tier-plan integration

## Identity
- Phase ID: `ANIM-16`
- Title: Wire ANIM-13 deterministic storyboard JSON into ANIM-05 video agent so a single CLI run produces a full per-shot tier-plan, optionally per-energy tier-routed.
- Parent subproject: `ANIM` (WO `APEX-ANIM-MB-WO-00001` §6).
- Owner agent: APEX orchestrator (Claude Opus 4.7).
- Depends-on: ANIM-13 (storyboard JSON shape, schema_version >=2), ANIM-05 (`plan_tier()` returns per-shot plan; ANIM-17 added env-key resolution to that path).
- Blocks: future ANIM-18 (cloud shim) would benefit from a bulk-plan that includes FalCloud tier where it makes sense.
- Reference patterns: ANIM-13 deterministic-emission shape; ANIM-17 fingerprint-only exposure.
- Branch: `phase/ANIM-16-storyboard-tier-plan` (stacked on `phase/ANIM-17-fal-key`).
- Cert tag: `cert/ANIM-16@<sha>`.

## Why ANIM-16

ANIM-13 emits a deterministic shot skeleton (43 shots for the Grog MV). ANIM-05's `--plan-tier` only handles one shot at a time. To produce the inputs needed by a future bulk-render pipeline, the operator currently has to invoke `--plan-tier` 43 times manually. ANIM-16 wraps that loop and adds per-energy tier routing so HIGH-energy shots default to Wan22 (cinematic) and LOW-energy shots can default to LTX (fast preview), matching the WO §S6 tier-routing intent.

## Context window budget
- ≤6 files committed; ≤300 LOC delta.
- Files in scope:
  1. `apex/docs/spec/SPEC-ANIM-16.md` (this).
  2. `apex/registry/muscle_video_agent.py` (modify, no new muscle).
  3. `apex/docs/anim/ANIM-16-evidence.json`.
  4. `apex/docs/anim/ANIM-16-tier-plan-grog_playground.json` (evidence: full 43-shot tier-plan for grog_playground).
  5. `apex/audit/anim-16/` (per-run audit JSONs + probe harness).
- Out of scope: live render invocation; LLM-fill of `{action}` placeholders; changes to the storyboard schema.

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-16-storyboard-tier-plan` | RW | env_sync GitHub PAT |
| Video agent | `apex/registry/muscle_video_agent.py` | RW | local (APEX-MB-PY-00114) |
| Storyboard | `apex/docs/anim/ANIM-13-storyboard-<project>.json` | R | local |
| Tier config | `apex/docs/anim/ANIM-05-tier-config.json` | R | local |
| Codex | gpt-5.5 | invoke | local |

## Inputs

ANIM-13 storyboard JSON (schema_version ≥ 2). Required top-level fields:
- `phase` == `"ANIM-13"`
- `shots[]` with each shot carrying `id`, `section`, `energy`, `duration_seconds`, `lyric`, `lyric_word_count`, `mood`, `camera_preset`, `wan_motion_preset`, `kontext_prompt_template`, `needs_fill[]`.
- `scene_slug` (matches `SLUG_RE` from ANIM-05).
- `character_markers` + `character_markers_source` annotation (passed through into per-shot tier-plan record for downstream traceability).

The storyboard's `schema_version_history` MAY be empty (for ANIM-13 schema_version=2 outputs). schema_version 3 includes the ANIM-14 character_markers_source annotation.

## Outputs

New muscle function `plan_from_storyboard(storyboard_path, tier_or_routing, force) -> dict`. Modes for `tier_or_routing`:

- A literal tier name (`"Wan22"`, `"LTX"`, `"Hunyuan"`, `"FalCloud"`) → all shots use that tier.
- The string `"energy"` (routing mode) → per-shot tier = `LOW → LTX`, `MED → Wan22`, `HIGH → Wan22` (current default map; explicit constant in source).

New CLI flags:

```
--plan-from-storyboard <storyboard-path>
--tier <Wan22|LTX|Hunyuan|FalCloud|energy>     # required with --plan-from-storyboard
--output <path>                                # optional; defaults to apex/docs/anim/ANIM-16-tier-plan-<project>.json
--force                                        # overwrite an existing output file
```

`--tier energy` is the new routing mode. The agent rejects any `--tier` value that's neither a known tier nor the `"energy"` keyword.

### Tier-plan JSON shape

```jsonc
{
  "phase": "ANIM-16",
  "schema_version": 1,
  "source_storyboard_path": "apex/docs/anim/ANIM-13-storyboard-grog_playground.json",
  "source_storyboard_sha256": "<64 hex>",
  "source_phase": "ANIM-13",
  "source_storyboard_schema_version": 3,
  "tier_routing_mode": "fixed" | "energy",
  "tier_routing_choice": "Wan22" | "LTX" | "Hunyuan" | "FalCloud" | "ENERGY_MAP",
  "energy_to_tier_map": {"LOW": "LTX", "MED": "Wan22", "HIGH": "Wan22"},
  "project": "grog_playground",
  "character": "grog",
  "scene_slug": "MagicalRealmPlayground",
  "brand": "Jesse-Adventures",
  "duration_seconds": 238.9,
  "shot_count": 43,
  "shots": [
    {
      "id": 1,
      "section": "intro",
      "start": 0.0, "end": 5.75, "duration_seconds": 5.75,
      "energy": "LOW", "mood": "...",
      "lyric": "...", "lyric_word_count": 0,
      "camera_preset": "...",
      "wan_motion_preset": "...",
      "kontext_prompt_template": "...",
      "needs_fill": ["action"],
      "tier_chosen": "LTX",
      "tier_plan": {
        "status": "PLAN" | "TIER_NOT_READY" | "TIER_KEY_OK_SHIM_PENDING" | "TIER_NOT_CONFIGURED" | ...,
        "tier": "LTX",
        "shot": "1",
        "scene": "MagicalRealmPlayground",
        "wrapper_invocation": "...",   // when PLAN
        "approx_seconds_per_clip": 90, // when PLAN
        "vram_gb": 16,                 // when PLAN
        "best_for": "...",             // when PLAN
        "key_resolution": null | {"status": "OK", "fingerprint": "...", ...}
      }
    },
    ...
  ],
  "summary": {
    "total_shots": 43,
    "by_status": {"PLAN": <int>, "TIER_NOT_READY": <int>, "TIER_KEY_OK_SHIM_PENDING": <int>},
    "by_tier_chosen": {"Wan22": <int>, "LTX": <int>, ...},
    "total_estimated_render_seconds": <float>   // sum(approx_seconds_per_clip) over PLAN entries
  },
  "built_at": "..."
}
```

### Routing map (deterministic, no LLM)
```python
ENERGY_TO_TIER_MAP = {"LOW": "LTX", "MED": "Wan22", "HIGH": "Wan22"}
```
Rationale: LOW-energy shots are slow-drift / interstitial — LTX (90s/clip preview-grade) is sufficient. MED + HIGH carry the song's character work — Wan22 (180s/clip cinematic) is the choice. Hunyuan is reserved for explicit physics shots (water/cloth/fire) which the storyboard cannot detect from `energy` alone, so it is never auto-routed. FalCloud is shim-pending and never auto-routed.

## Definition of Done
- `--plan-from-storyboard apex/docs/anim/ANIM-13-storyboard-grog_playground.json --tier Wan22` produces a 43-shot tier-plan, all with status `PLAN`, all using Wan22. File lands at the default output path.
- `--plan-from-storyboard <...> --tier LTX` likewise, all using LTX.
- `--plan-from-storyboard <...> --tier energy` produces 43 entries with `tier_chosen` per the energy map (LOW→LTX, MED→Wan22, HIGH→Wan22). Summary `by_tier_chosen` shows {LTX: 6, Wan22: 37}.
- `--plan-from-storyboard <...> --tier Hunyuan` produces 43 entries all `TIER_NOT_READY` (Hunyuan weights deferred).
- `--plan-from-storyboard <...> --tier FalCloud` produces 43 entries all `TIER_KEY_OK_SHIM_PENDING` (shim pending) — exit code TBD but agent run continues.
- Storyboard file SHA recorded in output; drift between recorded SHA and file at re-run detected (operator must use `--force` to overwrite).
- Codex silent-twice on gpt-5.5.
- Cert + handover + PR.

## Codex commands
Same gpt-5.5 inline-stdin pattern; transcripts to `apex_governance/codex_runs/ANIM-16/`.

## Test plan
1. `--plan-from-storyboard <grog storyboard> --tier Wan22` → 43 PLAN entries; output file present.
2. `--plan-from-storyboard <grog storyboard> --tier LTX` → 43 PLAN entries.
3. `--plan-from-storyboard <grog storyboard> --tier energy` → 6 LTX + 37 Wan22 PLAN entries; total_estimated_render_seconds matches sum.
4. `--plan-from-storyboard <grog storyboard> --tier Hunyuan` → 43 TIER_NOT_READY entries.
5. `--plan-from-storyboard <grog storyboard> --tier FalCloud` → 43 TIER_KEY_OK_SHIM_PENDING entries with fingerprint `95de:0714` in every record.
6. `--plan-from-storyboard <grog storyboard> --tier energy` then re-run without `--force` → WILL_OVERWRITE_REFUSED exit 5.
7. `--plan-from-storyboard <missing>` → STORYBOARD_NOT_FOUND exit 10.
8. `--plan-from-storyboard <non-ANIM13>` (a JSON without `phase: ANIM-13`) → STORYBOARD_INVALID_PHASE exit 10.
9. `--plan-from-storyboard <grog storyboard> --tier BadTier` → INVALID_TIER exit 6.

## Pass criteria
- [ ] All 9 test paths pass.
- [ ] tier-plan JSON shape matches §Outputs.
- [ ] Codex silent-twice.
- [ ] PR + cert + handover + index.

## Rollback plan
- `git restore` the changed files; agent returns to per-shot `--plan-tier` only.

## Doctrine conformance
- **P3**: no invention — tier choices are deterministic (fixed tier OR explicit ENERGY_TO_TIER_MAP); shot data passed through verbatim from storyboard.
- **R15/R16**: silent-twice; max 5 fix rounds.
- **R19**: REUSE — extends APEX-MB-PY-00114; consumes ANIM-13 storyboard format unchanged.
- **R20**: preserves detail — every storyboard field carried into per-shot tier-plan record; nothing dropped.
- **O2/O6/O9**: tier_plan schema_version=1; storyboard SHA recorded; structured failure surface; audit JSONs per run.

## Lifecycle modes
| Mode | Evidence | Status |
|---|---|---|
| Plan | this spec | DONE |
| Build | agent + grog tier-plan JSON + evidence | DONE on phase close |
| Use | future MV phases call `--plan-from-storyboard` after the storyboard is emitted | DEFERRED |
| Maintain | extend ENERGY_TO_TIER_MAP when new tiers come online (e.g. Hunyuan READY) | DEFERRED |
