# SPEC-ANIM-14 — character_markers schema extension on ANIM-03 reference-pack manifest

## Identity
- Phase ID: `ANIM-14`
- Title: Hoist `character_markers` + provenance from ANIM-13 project bindings into the per-character entry of the ANIM-03 reference-pack manifest, so future storyboard projects do not re-state markers.
- Parent subproject: `ANIM` (WO `APEX-ANIM-MB-WO-00001` §6 — "roll across remaining characters/brands").
- Owner agent: APEX orchestrator (Claude Opus 4.7).
- Depends-on: ANIM-03 (reference-pack manifest), ANIM-13 (Shot/Storyboard agent, marker provenance pattern).
- Blocks: ANIM-15 (Lirian MV project binding will use the new lookup), ANIM-16 (tier-plan integration relies on storyboard outputs being self-contained).
- Reference patterns: ANIM-13 provenance triple (`*_provenance_source_path` + `*_provenance_field` + `*_provenance_sha256` + verbatim-equality check), implemented in `apex/registry/muscle_shot_storyboard_agent.py` build_storyboard().
- Branch: `phase/ANIM-14-marker-schema` (stacked on `phase/ANIM-13-shot-storyboard`).
- Cert tag: `cert/ANIM-14@<sha>`.

## Why ANIM-14

ANIM-13 demonstrated that character identifier markers (the prompt-relevant short descriptor) must be sourced from an authoritative on-disk file and verified at runtime. For the Grog MV the canonical source is `shot_list.json:grog_identifiers`. The marker text + provenance is currently carried in `apex/docs/anim/ANIM-13-projects.json:projects.grog_playground`. That works for one project, but every future song/MV for the same character would have to re-declare the same marker string + provenance, duplicating data and adding drift surface.

ANIM-14 lifts `character_markers` (plus provenance) up to the per-character entry of the certed ANIM-03 reference-pack manifest. The Shot/Storyboard agent gains an ANIM-03 lookup path: if a project binding does not carry `character_markers`, the agent reads them from ANIM-03's per-character entry and applies the same provenance verification before emission.

## Context window budget
- ≤8 files committed; ≤300 LOC delta across them.
- Files in scope:
  1. `apex/docs/spec/SPEC-ANIM-14.md` (this).
  2. `apex/docs/anim/ANIM-03-reference-pack-manifest.json` — schema_version bump 1→2; add optional marker block to `characters.<slug>`; backfill grog.
  3. `apex/registry/muscle_shot_storyboard_agent.py` — ANIM-03 marker lookup + verification; cross-check if both project + ANIM-03 declare markers; preserved exit codes; doctrine notes updated in-line.
  4. `apex/docs/anim/ANIM-13-projects.json` — remove redundant `character_markers*` fields from `grog_playground` (forces the lookup path to be exercised); add doctrine_note pointing at ANIM-14.
  5. `apex/docs/anim/ANIM-13-storyboard-grog_playground.json` — regenerated under the new lookup path (must be byte-equivalent in marker fields).
  6. `apex/docs/anim/ANIM-14-evidence.json` — phase evidence (command output, regen diff, validation rerun).
  7. `apex/audit/anim-14/` (audit JSONs from runs).
- Out of scope: galinda / emma / lirian marker registration (no canonical source field exists for them yet — they require a separate intake step per character; logged as a follow-on in §Open follow-on); any ANIM-04 changes; the `kontext_prompt_template` body (still `{action}`-only); changes to the Video / Assembly / Environment agents.

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-14-marker-schema` | RW | env_sync GitHub PAT |
| ANIM-03 reference-pack manifest | `apex/docs/anim/ANIM-03-reference-pack-manifest.json` | RW | local |
| ANIM-13 project bindings | `apex/docs/anim/ANIM-13-projects.json` | RW | local |
| Storyboard agent | `apex/registry/muscle_shot_storyboard_agent.py` | RW | local (registered APEX-MB-PY-00117) |
| Grog marker source | `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json` | R | local NAS-mounted |
| Codex | gpt-5.5 ChatGPT-account auth | invoke | local |

## Inputs (with SHAs verified at spec time)
- Grog marker source: `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json` sha256 = `6414235bd985e2d90c4e5875846739a276da0f2c7388abff4a99377332f6a428`, field `grog_identifiers`, value: `"massive ogre with warm beige skin and rugged texture, smooth clean-shaven face, warm brown eyes, teal roughspun vest, fraying rope belt, patched fringe brown trousers"`. Cross-checked against ANIM-13-projects.json recorded value — identical.
- Prior storyboard: `apex/docs/anim/ANIM-13-storyboard-grog_playground.json` (43 shots, character_markers identical to above source value).

## Schema extension (ANIM-03 manifest)

`schema_version` bumps 1 → 2. Each entry under `characters.<slug>` MAY now carry an optional marker block:

```jsonc
"<slug>": {
  // ... existing fields ...
  "character_markers": "<prompt-relevant identifier string verbatim from the source file>",
  "character_markers_provenance_source_path": "<absolute path to the source file>",
  "character_markers_provenance_field": "<top-level JSON field name within the source file>",
  "character_markers_provenance_sha256": "<sha256 of the source file bytes at registration time>"
}
```

All four fields are required together or all absent (no partial declarations). Manifest writer should validate this at registration time; the agent re-validates this at runtime UNCONDITIONALLY — a partial manifest marker block for any bound character surfaces `CHARACTER_MARKERS_MANIFEST_PARTIAL` (exit 13) before the project path is even evaluated, forcing the registry inconsistency to be fixed before any project using that character can run. This is stricter than tolerating partials when projects.json supplies a full override, but it is the only reading consistent with treating ANIM-03 as a certed manifest under doctrine "no claim without sha" / R20.

Backfill in this phase: grog only. Galinda / emma / lirian carry no marker block in ANIM-14 (no canonical source field exists for them yet). The agent surfaces a clear error (`CHARACTER_MARKERS_NOT_FOUND`) if a future project binding for those characters omits markers in the project config and the manifest also lacks them.

## Storyboard agent change (muscle_shot_storyboard_agent.py)

Resolution order for `character_markers` inside `build_storyboard()`:

1. If `projects.json[<slug>]` carries all three project-level provenance fields (`character_markers_provenance_source_path` + `character_markers_provenance_field` + `character_markers_provenance_sha256`) AND `character_markers`, the existing per-project verification path runs (UNCHANGED — preserves backward compatibility).
2. Else, fall back to ANIM-03 lookup:
   - Read `ref_pack["characters"][cfg["character"]]`. If the marker block is absent → exit `CHARACTER_MARKERS_NOT_FOUND` (new code 13).
   - If marker block is partial (mixed presence) → exit `CHARACTER_MARKERS_MANIFEST_PARTIAL` (new code 13).
   - Hash the named source file; require sha256 equality with recorded value → drift → `CHARACTER_MARKERS_PROVENANCE_DRIFT` (existing code 11).
   - Read field; require value equality with recorded `character_markers` → mismatch → `CHARACTER_MARKERS_VALUE_MISMATCH` (existing code 11).
   - On success, the agent emits the storyboard with `"character_markers_source"` annotation set to `"ANIM-03 manifest (sha-verified against <source_path>)"`.
3. If BOTH projects.json AND ANIM-03 declare marker blocks, the agent additionally cross-checks the two recorded `character_markers` strings are byte-equal. Mismatch → `CHARACTER_MARKERS_SOURCE_CONFLICT` (new code 13).

New exit codes:
- 13 / `CHARACTER_MARKERS_NOT_FOUND` — no marker info anywhere.
- 13 / `CHARACTER_MARKERS_MANIFEST_PARTIAL` — partial marker block in ANIM-03.
- 13 / `CHARACTER_MARKERS_SOURCE_CONFLICT` — projects.json + ANIM-03 disagree.

The existing 11-codes (PROVENANCE_MISSING, SOURCE_MISSING, PROVENANCE_DRIFT, SOURCE_UNPARSEABLE, FIELD_MISSING, VALUE_MISMATCH) remain as the verification surface and are re-used by both paths.

`schema_version` of emitted storyboard bumps 2 → 3 to flag that markers may now come from ANIM-03.

## Definition of Done
- ANIM-03 manifest has marker block for grog with provenance sha matching live source bytes.
- ANIM-13-projects.json `grog_playground` no longer carries `character_markers*` fields (forces ANIM-03 lookup path).
- `--storyboard grog_playground --force` succeeds with `character_markers` byte-equal to prior storyboard's marker (proves backward-compat at the wire).
- `--validate grog_playground` succeeds with section deltas unchanged from ANIM-13 baseline (9/9 sections aligned, max delta 0.000s).
- Both new error paths (`CHARACTER_MARKERS_NOT_FOUND`, `CHARACTER_MARKERS_SOURCE_CONFLICT`) exercised via constructed test inputs and recorded in evidence.
- Codex adversarial-review silent-twice on the diff bundle (gpt-5.5).
- Cert + handover + PR.

## Codex commands
Same gpt-5.5 inline-stdin pattern: `CODEX_MODEL=gpt-5.5 codex exec --model gpt-5.5 --skip-git-repo-check --cd /c/Users/Owner/Repos/code-artifacts < bundle.txt > round<n>.txt`. Persist transcripts to `apex_governance/codex_runs/ANIM-14/round<n>.txt`. Silent-twice = two consecutive rounds with no HIGH findings.

## Test plan
1. `python apex/registry/muscle_shot_storyboard_agent.py --storyboard grog_playground --force` (after the projects.json marker removal) → ANIM-03 lookup path; OK; storyboard regenerated with same marker text as ANIM-13 baseline.
2. `--validate grog_playground` → section deltas all 0.000s (unchanged from baseline).
3. Negative-path constructions captured in evidence:
   a. Temp-clone ANIM-03 manifest with marker block deleted; agent reports `CHARACTER_MARKERS_NOT_FOUND`.
   b. Temp-clone with marker block partial (drop sha256); agent reports `CHARACTER_MARKERS_MANIFEST_PARTIAL`.
   c. Temp-clone with marker block whose `character_markers` differs from the source field value; agent reports `CHARACTER_MARKERS_VALUE_MISMATCH`.
   d. Re-add the project-level marker block in projects.json with a different `character_markers` string; agent reports `CHARACTER_MARKERS_SOURCE_CONFLICT`.
4. Diff `ANIM-13-storyboard-grog_playground.json` before/after: `character_markers_source` annotation changes from `"projects.json (sha-verified...)"` to `"ANIM-03 manifest (sha-verified...)"`; everything else equal.

## Pass criteria
- [ ] ANIM-03 schema_version=2; grog marker block present + sha-verified at registration.
- [ ] Storyboard agent lookup-order code matches §Storyboard agent change exactly.
- [ ] grog_playground re-emit + re-validate succeed under the new path with identical wire output.
- [ ] All four negative-path tests exercised; evidence persisted.
- [ ] Codex silent-twice.
- [ ] PR + cert + handover + index entry.

## Open follow-on (not blocking ANIM-14)
- ANIM-15 (Lirian MV binding): a Lirian-specific identifier source (e.g. a `lirian_identifiers` field in a future shot_list.json or a per-character status.json) will be sourced from the operator. Until then, registering Lirian markers in ANIM-03 is operator-gated → logged at `apex_governance/MISSING_ARTIFACTS.queue.json` as `MA-ANIM-14-MARKERS-LIRIAN`.
- Same for galinda + emma (`MA-ANIM-14-MARKERS-GALINDA`, `MA-ANIM-14-MARKERS-EMMA`).

## Rollback plan
- `git restore` the changed files. The storyboard agent's existing project-level path is preserved verbatim — restoring `apex/docs/anim/ANIM-13-projects.json` to its prior content (with marker fields) immediately reverts to the ANIM-13 behaviour even without restoring the agent file. The ANIM-03 marker block addition is additive (schema_version=2 manifests are still readable by ANIM-13 code paths since extra fields are ignored), so partial rollback is safe.

## Doctrine conformance
- **P3** (no invention): markers are sourced verbatim from a named on-disk source; both registration and runtime re-hash + value-match against that source; agent never composes marker text.
- **R20** (preserve detail): backfill copies value byte-for-byte from `shot_list.json:grog_identifiers`; the storyboard's emitted `character_markers` byte-equals prior storyboard's value.
- **O2/O6/O9**: manifest schema_version bump; ISO8601 UTC timestamp on the manifest mtime; audit JSON per run.
- **R15** (silent-twice): codex_runs/ANIM-14/round{n}+round{n+1} HIGH-empty.
- **R16** (loop cap): max 5 fix rounds.

## Lifecycle modes
| Mode | Evidence | Status |
|---|---|---|
| Plan | this spec | DONE |
| Build | manifest extension + agent code + projects.json migration + storyboard regen + evidence | DONE on phase close |
| Use | future MV phases registering a new character marker block once; project bindings drop marker fields | DEFERRED |
| Maintain | marker block updated when canonical source file is renamed or marker string is revised; sha + value re-recorded at the same time | DEFERRED |
