# SPEC-ANIM-04 — Environment/Imagery agent (S4 backgrounds)

## Identity
- Phase ID: `ANIM-04`
- Title: Environment agent that catalogs existing scene refs and emits scene-bibles + scene-pack manifest from brand tokens + scene descriptors.
- Parent subproject: `ANIM` (WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator (Claude Opus 4.7)
- Depends-on: `ANIM-03` (CERT-ANIM-03.json silent-twice rounds 3+4); reuses the Character-Build agent's bible/manifest pattern.
- Blocks: `ANIM-05` (Video agent consumes the scene-pack manifest for first-shot backgrounds).
- Reference patterns: `apex/registry/muscle_character_build_agent.py` (sibling pattern). Brand tokens come from `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json` (`style_anchor` + `prompt_rules`) and `PROJECT_SPEC.md` "style bible" section.
- Branch: `phase/ANIM-04`
- Cert tag at completion: `cert/ANIM-04@<sha>`

## Context window budget
- Files in scope (≤8):
  1. `apex/docs/spec/SPEC-ANIM-04.md` (this file)
  2. `apex/docs/DOCUMENT_REGISTER.md` (+1 row APEX-MB-PY-00113)
  3. `apex/registry/muscle_environment_agent.py` (the agent)
  4. `apex/docs/anim/scenes/ANIM_Jesse-Adventures_MagicalRealmPlayground_bg_v1.md` (scene bible — the Grog scene already shipped as MP4)
  5. `apex/docs/anim/ANIM-04-scene-descriptors.json` (operator-editable scene catalog input)
  6. `apex/docs/anim/ANIM-04-scene-pack-manifest.json` (output)
  7. `apex/docs/anim/ANIM-04-evidence.json`
  8. `apex/audit/anim-04/` (audit JSONs)
- Out of scope: live ComfyUI re-rendering of backgrounds (deferred to ANIM-05 video-shot pipeline; backgrounds are referenced, not re-generated, in ANIM-04); Supabase QC schema migration (G10 from ANIM-01 — operator-gated).

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-04` | RW | env_sync GitHub PAT |
| Scene refs | `X:/Automations/apex/projects/jesse_animate/characters/_source_refs/scenes/` | R | local |
| Brand tokens (style anchor + prompt rules) | `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json` | R | local |
| Style bible section | `X:/Automations/apex/projects/jesse_animate/PROJECT_SPEC.md` | R | local |
| Codex CLI | gpt-5.5 / ChatGPT-account auth | invoke | local |

Unresolved rows: none.

## Inputs
- ANIM-03 cert + handover.
- `style_anchor` (verbatim from shot_list.json): `"Pixar 3D animated feature film, vibrant warm colours, smooth stylized CGI, expressive character design"`.
- `prompt_rules` (verbatim from shot_list.json): `"Subject in first 15 words. 30-80 words per kontext_prompt. No quality tags. No negation. Lighting described as interaction. Texture inline with subject. Style anchor once at end. Character identified by key visual markers not 'the same character'."`.
- Existing scene refs: 9 magical-realm-playground PNGs at `X:/.../characters/_source_refs/scenes/` (file naming `a_magical_realm_playground_in_the_evening_red_and_orange_summ_<uuid>_<index>.png`).
- ANIM-04-scene-descriptors.json — committed in this phase with seed entry for `MagicalRealmPlayground`; future scenes added by operator and the agent rerun.

## Outputs
- **Agent**: `apex/registry/muscle_environment_agent.py` (APEX-MB-PY-00113).
- **Scene descriptor seed**: `apex/docs/anim/ANIM-04-scene-descriptors.json` with the MagicalRealmPlayground entry (prompt-prefix + brand + style overrides).
- **Scene bible**: `apex/docs/anim/scenes/ANIM_Jesse-Adventures_MagicalRealmPlayground_bg_v1.md` — sections: brand tokens cited verbatim, scene prompt, existing asset catalog with sha256+size, do/don't, copyright/differentiation.
- **Scene-pack manifest**: `apex/docs/anim/ANIM-04-scene-pack-manifest.json` — per-scene `{descriptor, brand_tokens, assets[], findings}` block.
- **Audit**: `apex/audit/anim-04/<scene>-build-<ts>.json`.
- Cert: `apex_governance/certs/CERT-ANIM-04.json`.
- Handover: `apex_governance/handovers/ANIM-04.handover.md`.

## Definition of Done
- **Brand tokens**: agent reads `style_anchor` + `prompt_rules` directly from shot_list.json; quoted verbatim in every scene bible.
- **Scene descriptor schema**: `{slug, brand, prompt, source_path_substr?}` where `slug` matches regex `^[A-Z][A-Za-z0-9]{0,31}$`, brand must match an allow-list (initially just `Jesse-Adventures`), prompt is required. Source path substring narrows the asset catalog to a subset of scene refs.
- **Catalog mode** (default): scans `_source_refs/scenes/` for filenames matching `source_path_substr` (case-insensitive), records full sha256 + size per asset, picks up to 7 as the scene pack.
- **Bible output**: contains brand tokens verbatim + scene descriptor + cataloged assets + findings.
- **Idempotency**: rerun without `--force` returns `WILL_OVERWRITE_REFUSED` exit 5 (same pattern as ANIM-03 agent).
- **Path validation**: slug regex-bounded + resolved-path checks for traversal defense (same as ANIM-03).
- **Codex silent-twice** under R15.
- **PR**: opened via `gh pr create`.
- **Cert + handover**: minted, appended to `certs/index.json`.

## Codex commands required
| Stage | Command | Background | Expected |
|---|---|---|---|
| Spec + diff | `CODEX_MODEL=gpt-5.5 codex exec --skip-git-repo-check ...` | no | silent-twice |

## Governance hooks
- Naming: scene bible matches `ANIM_<Brand>_<Scene>_bg_v<n>.md` per WO §5.
- DOCUMENT_REGISTER row reserved (APEX-MB-PY-00113) before agent write.

## Test plan
- Unit: `--slug MagicalRealmPlayground --dry-run` → exit 0, catalog preview.
- Live: `--slug MagicalRealmPlayground` → bible + manifest entry + audit JSON.
- Sanitization: `--slug "../etc"` → exit 6.
- Catalog correctness: discovered asset count for the magical-realm prefix = 9 (matches `ls _source_refs/scenes/`).
- Rerun guard: second `--slug MagicalRealmPlayground` → exit 5.

## Pass criteria
- [ ] Brand tokens verbatim in bible.
- [ ] ≥1 scene bible written.
- [ ] Scene-pack manifest contains the scene with sha256+size per asset.
- [ ] Agent path-safe + sanitized + idempotent.
- [ ] Codex silent-twice.
- [ ] PR opened, cert + handover written.

## Rollback plan
- `git restore` the 8 files; no live filesystem mutation outside `apex/audit/anim-04/` and the descriptors JSON (which is committed input).
- Notification: append to `apex_governance/findings/ANIM-04.findings.md`.

## Doctrine conformance
- P3 / R15 / R16 / O2 / O6 / O9 — same pattern as ANIM-03.
- R19: internal-research = local shot_list.json + PROJECT_SPEC reads.

## Lifecycle modes
| Mode | Evidence | Status |
|---|---|---|
| Plan | SPEC-ANIM-04.md | DONE |
| Build | agent + descriptor seed + scene bible + manifest + evidence | DONE |
| Use | ANIM-05 reads scene-pack manifest for background asset paths | DEFERRED |
| Maintain | operator extends descriptor JSON + reruns agent | DEFERRED |

## Cleanup report (cert time)
- Files deleted: none. Files renamed: none. Sandbox dir empty: N/A.
