# SPEC-ANIM-03 — Character-Build agent (S1 bible + S2 turnaround manifest + S3 reference pack)

## Identity
- Phase ID: `ANIM-03`
- Title: Build the Character-Build agent and produce bibles + reference packs for Galinda + Emma.
- Parent subproject: `ANIM` (per WO `APEX-ANIM-MB-WO-00001`)
- Owner agent: APEX orchestrator (Claude Opus 4.7)
- Depends-on: `ANIM-02` (cert at `apex_governance/certs/CERT-ANIM-02.json`; kohya structural install, HunyuanVideo nodes, deduped LoRAs, register rows).
- Blocks: `ANIM-04` (Environment agent uses brand tokens that this phase's bibles cite), `ANIM-05` (Video agent consumes reference-pack manifests).
- Reference patterns followed (PLAN_CRITERIA §11): `apex/PROJECT_APEX_v2.2.md`, `X:/Automations/apex/projects/jesse_animate/characters/CHARACTER_TEMPLATE.md`, `apex/registry/muscle_character_designer.py` + `muscle_char_consistency.py` (existing pipeline; this phase wraps, does not replace).
- Branch: `phase/ANIM-03`
- Cert tag at completion: `cert/ANIM-03@<sha>`

## Context window budget
- Token budget: spec + agent script + 2 bibles + reference-pack manifest + evidence. Aim ≤8 files committed, ≤600 LOC across them.
- Files in scope (≤8):
  1. `apex/docs/spec/SPEC-ANIM-03.md` (this file)
  2. `apex/docs/DOCUMENT_REGISTER.md` (1 new row for the agent, APEX-MB-PY-00112)
  3. `apex/registry/muscle_character_build_agent.py` (the Character-Build agent — CLI muscle)
  4. `apex/docs/anim/bibles/ANIM_Jesse-Adventures_Galinda_bible_v1.md`
  5. `apex/docs/anim/bibles/ANIM_Jesse-Adventures_Emma_bible_v1.md`
  6. `apex/docs/anim/ANIM-03-reference-pack-manifest.json` (S3 deliverable for both characters)
  7. `apex/docs/anim/ANIM-03-evidence.json` (machine-readable evidence anchors)
  8. `apex/audit/anim-03/` directory with execution audit JSONs from the agent runs
- Files out of scope: model file regeneration (existing renders at `X:/Automations/apex/projects/jesse_animate/characters/{galinda,emma}/` are referenced, not re-rendered, in this phase), kohya LoRA training (deferred per WO §3 "optional"), Supabase QC tracking (operator-gated, ANIM-04 scope).
- External documents loaded: `X:/Automations/apex/projects/jesse_animate/PHASE_STATE.json` (galinda sign-off, Emma priority), `X:/Automations/apex/projects/jesse_animate/PROJECT_SPEC.md` (Emma canon row), `X:/Automations/apex/projects/jesse_animate/characters/galinda/{README.md,status.json}` (Galinda canon — note canon discrepancy F-ANIM03-01 below), `X:/Automations/apex/projects/jesse_animate/characters/CHARACTER_TEMPLATE.md` (structure template).

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-03` | RW | env_sync GitHub PAT |
| Character source assets | `X:/Automations/apex/projects/jesse_animate/characters/` | R | local |
| Character renders | `X:/Automations/apex/projects/jesse_animate/characters/{galinda,emma}/` | R | local |
| ComfyUI runtime | `http://127.0.0.1:8189` | invoke (optional, only if `--regenerate` flag passed) | local |
| ComfyUI models | `C:/ComfyUI/models/` (FLUX Kontext + IP-Adapter FaceID + kontext-turnaround-sheet LoRA) | R | local (per ANIM-01 capability map) |
| Codex CLI | `codex-cli 0.135.0` with `CODEX_MODEL=gpt-5.5` | invoke | local |
| Secrets | none required (offline pipeline) | — | — |

Unresolved rows: none.

## Inputs
- ANIM-02 cert + handover (`CERT-ANIM-02.json`, `ANIM-02.handover.md`).
- Galinda canon: `X:/Automations/apex/projects/jesse_animate/characters/galinda/status.json` (canonical), `.../galinda/README.md` (sibling — has age discrepancy, F-ANIM03-01).
- Emma canon: `X:/Automations/apex/projects/jesse_animate/PROJECT_SPEC.md` §1.8 character canon table.
- CHARACTER_TEMPLATE.md (structure).
- Existing render trees: `galinda/{angles,expressions,poses,...}` (post-PHASE-2.2 sign-off 2026-04-07); `emma/` flat render set (front/back/side/three_quarter/alt_form/core + expressions).

## Outputs
- **S1 Bibles**: `apex/docs/anim/bibles/ANIM_Jesse-Adventures_Galinda_bible_v1.md`, `ANIM_Jesse-Adventures_Emma_bible_v1.md`. Each follows a fixed sectioned template: visual identity (face / hair / outfit / palette), personality + behaviour cues, signature poses + expressions list, do/don't, source-of-canon citations, copyright/differentiation note.
- **S2 Turnaround manifest**: integrated into the reference-pack JSON for this phase (no re-rendering; existing angles referenced verbatim). Naming `ANIM_<Brand>_<Character>_turnaround_v<n>.png` applied at re-render time only when `--regenerate` is passed (out of scope for ANIM-03 cert).
- **S3 Reference pack**: `apex/docs/anim/ANIM-03-reference-pack-manifest.json` listing 4–7 chosen images per character with role tags (`primary_ref`, `face_front`, `expression_neutral`, etc.).
- **Agent**: `apex/registry/muscle_character_build_agent.py` — CLI muscle that takes a character name, reads canon sources, emits the bible markdown + reference-pack manifest, optionally invokes existing `muscle_character_designer.py` for re-renders (deferred).
- **Audit**: `apex/audit/anim-03/<character>-build-<ts>.json` per character.
- Cert: `apex_governance/certs/CERT-ANIM-03.json`.
- Handover: `apex_governance/handovers/ANIM-03.handover.md`.

## Definition of Done (objective)
- **F1 resolution (from ANIM-02 handover)**: documented in `ANIM-03-evidence.json` — PHASE_STATE.json `phase2_2_signoff` at 2026-04-07T10:32:00Z is authoritative; PHASES.md "⬜ PENDING" row is stale. Galinda IS production-ready.
- **Agent**: parses a `--character <name>` arg matching the regex `^[a-z][a-z0-9_]{0,31}$` (path-traversal safe; rejects with exit 6 otherwise), reads canon sources (status.json or PROJECT_SPEC canon table — first-cell exact match to avoid the Emma/Gemma F-1 bug), writes the bible markdown + reference-pack manifest entry. `--dry-run` prints what would be written. Idempotent: rerunning **refuses to overwrite an existing v1** and returns exit code 5; `--force` overwrites. (Earlier draft proposed `_v2` auto-appending — removed in round-1 alignment with the actual exit-5 guard.)
- **Galinda bible**: cites both status.json AND README.md, surfaces the age discrepancy as F-ANIM03-01, locks the canon for ANIM-04+ as the **status.json** "young adult woman (early 20s)" version because that matches the 2026-04-07 production-ready PHASE_STATE sign-off and the existing 15/15 renders in `galinda/angles/`.
- **Emma bible**: built from PROJECT_SPEC.md §1.8 row "Emma | Sarah | Dragon vessel, amethyst/emerald scales, blonde, long hair" plus existing emma render set (alt_form_00001 = dragon form). Notes ONE OPEN finding: Emma has no `status.json` or `README.md` (F-ANIM03-02), bible is built from PROJECT_SPEC + render-set inference only.
- **Reference pack**: 4–7 anchor images per character chosen from existing renders, with role tags + **full sha256** + size for each entry. Agent enforces the 4-minimum at write time (`PACK_TOO_SMALL` exit code 7 if unmet); 7-maximum enforced by picker slice.
- **Codex adversarial-review** to silent-twice per R15 on the spec + diff bundle. Transcripts to `apex_governance/codex_runs/ANIM-03/`.
- **PR**: opened via `gh pr create` (same pattern as ANIM-02 PR #8).
- **Cert + handover**: minted, appended to `certs/index.json`.

## Codex commands required
| Stage | Command | Background | Expected |
|---|---|---|---|
| Spec + diff | `CODEX_MODEL=gpt-5.5 codex exec --skip-git-repo-check -m gpt-5.5 --output-last-message <round-file> < inline_bundle` | no | silent-twice |

Persist every transcript to `apex_governance/codex_runs/ANIM-03/round<n>.txt`.

## Governance hooks
- WO drop: not used in ANIM-* chain.
- Naming gate: `ANIM_Jesse-Adventures_<Char>_bible_v1.md` matches WO §5 + APEX-MB-DOC-00001 NAMING_CONVENTION.
- Doc control: 1 new row reserved in `DOCUMENT_REGISTER.md` for the agent (APEX-MB-PY-00112) before any agent script write.
- No new external services touched.

## Test plan
- Unit (`muscle_character_build_agent.py --character galinda --dry-run`): exit 0, prints bible path + reference-pack entry plan.
- Live (`--character galinda`): writes both `bibles/ANIM_Jesse-Adventures_Galinda_bible_v1.md` and updates `ANIM-03-reference-pack-manifest.json` with the galinda block.
- Live (`--character emma`): same for Emma.
- Round-trip: rerun `--character galinda` without `--force` returns exit code 5 (will-overwrite-guard) and does not modify files.
- `--character galinda --force` overwrites and produces an audit JSON.

## Pass criteria (binary)
- [ ] Both bibles written with all sections populated and canon citations cross-anchored.
- [ ] Reference-pack manifest contains ≥4 entries per character, each with role + sha256 + size.
- [ ] Agent script idempotent (rerun guard) and emits audit JSON.
- [ ] Galinda canon discrepancy logged as F-ANIM03-01 in evidence JSON.
- [ ] Emma missing-README logged as F-ANIM03-02 in evidence JSON.
- [ ] Codex silent-twice rounds archived.
- [ ] PR opened, cert minted, handover written, certs/index.json appended.

## Rollback plan
- Trigger: codex cannot reach silent-twice within R16 cap; or canonical-source data conflicts irreconcilable without operator input.
- Procedure: `git restore` the 8 files; manifest is JSON so safe to overwrite. No live-filesystem mutation outside `apex/audit/anim-03/`.
- Notification: append to `apex_governance/findings/ANIM-03.findings.md`.

## Doctrine conformance (cited at cert time)
- P3 (silent-twice loop, R15 closure): rounds archived.
- O2 (model deliberate): `CODEX_MODEL=gpt-5.5`.
- O6 (transcripts persisted).
- O9 (no ship without clean review).
- R19 (mandatory pre-flight research): internal-research layer = file reads of canon sources logged in evidence; no external research needed (offline character canon is the only authority).

## Lifecycle modes
| Mode | Evidence | Status |
|---|---|---|
| Plan | SPEC-ANIM-03.md | DONE on commit |
| Build | agent script + 2 bibles + reference manifest + evidence JSON | DONE on commit |
| Use | ANIM-04 / ANIM-05 cite the bible files via stable repo paths | DEFERRED |
| Maintain | bible versioning (v1 → v2 if canon resolved); agent reads any v<n> | DEFERRED_TO_ANIM_07 |

## Cleanup report (filled at cert time)
- Files deleted: none planned.
- Files renamed: none planned.
- Paths reconciled: none planned.
- Sandbox dir empty: N/A.
- Scratch dir empty: N/A.
