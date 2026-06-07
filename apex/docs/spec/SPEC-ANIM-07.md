# SPEC-ANIM-07 — Scale Character-Build agent across remaining Jesse-Adventures cast

**Phase:** ANIM-07 of `APEX-ANIM-MB-WO-00001`
**Parent subproject:** SP-ANIM
**Depends-on:** ANIM-03 (Character-Build agent + Galinda + Emma bibles), ANIM-06 (first visible deliverable, Grog MP4)
**Blocks:** None (parallel with AGEN core-five recovery)
**Issued:** 2026-06-07
**Branch:** `phase/ANIM-07` (branched from `phase/ANIM-06@e09ccc0`)
**Reference patterns followed (PLAN_CRITERIA §11):** `apex/registry/muscle_character_build_agent.py` (APEX-MB-PY-00112, ANIM-03), `apex/docs/spec/SPEC-ANIM-03.md`, doctrine R15 (silent-twice), R19 (research stance, satisfied by ANIM-01 capability map).

---

## 1. Objective

Scale the Character-Build agent (APEX-MB-PY-00112) from the two ANIM-03 subjects (galinda + emma) across the remaining canon cast on the operator's QNAP NAS share `X:/Automations/apex/projects/jesse_animate/characters/`: **jesse, kevin, amy, laura, lirian, ann, grog**. Per WO §6: "Roll across remaining characters/brands."

This is a pure scaling phase. It does not regenerate art, does not invoke ComfyUI, does not edit canon. It reads, classifies, and registers what is already on disk.

## 2. Pre-flight findings (informs scope)

A render-set census run during pre-flight (`find -name "*.png"`) shows the cast is unevenly populated:

| Character | PNG count | Render layout on disk | Buildable today? |
|---|---|---|---|
| jesse | 0 | empty dir | No — log F-ANIM07-01 (NO_RENDERS) |
| kevin | 0 | empty dir | No — log F-ANIM07-01 (NO_RENDERS) |
| laura | 0 | empty dir | No — log F-ANIM07-01 (NO_RENDERS) |
| ann | 0 | empty dir | No — log F-ANIM07-01 (NO_RENDERS) |
| amy | 52 | `midjourney_refs/` only (raw, non-canonical names) | No — log F-ANIM07-02 (MIDJOURNEY_RAW_ONLY) |
| lirian | 18 | `kontext_sheets/` (expr_*, pose_*, turnaround_seed*) + 3 root candidates | Yes (after agent extension) |
| grog | 46 | `primary_ref.png` + `kontext_sheets/` + `midjourney_refs/` + `video_frames/` | Yes (after agent extension) |

The ANIM-03 agent's `discover_render_set` only crawls `angles/`, `expressions/`, `poses/`, `closeups/`, `outfits/`, `source_refs/`. The grog/lirian render trees use the `kontext_sheets/` convention (with `turnaround_seed*.png`, `expr_<name>.png`, `pose_<name>.png` files) which ANIM-03 didn't account for because galinda used the older layout. The agent must be extended (not the canon).

Both grog and lirian also satisfy `PROJECT_SPEC §1.8 Character Canon (Confirmed)` rows, so `project_spec_canon_row()` will resolve them — and neither has a `status.json` on disk, identical to emma in ANIM-03.

## 3. Scope (in / out)

In scope:
- Extend `apex/registry/muscle_character_build_agent.py` (APEX-MB-PY-00112):
  - Add `kontext_sheets/` to `discover_render_set` so `expr_*.png`, `pose_*.png`, and `turnaround_seed*.png` are picked up.
  - Add three new role needles (`turnaround_seed`, `pose_walking`/`pose_running`/etc., expression alternates) so `kontext_sheets`-layout characters can hit `PACK_MIN=4`.
  - Preserve all prior behaviour for galinda + emma (re-running the agent for them must continue to produce `WILL_OVERWRITE_REFUSED` without `--force`).
- Run the extended agent against `grog` and `lirian` (the only two buildable cast members). Bibles, manifest entries, and audit JSONs land at the same paths as ANIM-03 (manifest is `apex/docs/anim/ANIM-03-reference-pack-manifest.json` — additive update under new character keys).
- Log a single follow-on findings file at `apex/docs/anim/ANIM-07-cast-coverage.json` enumerating every cast member's buildability state for the operator. Empty-dir characters (jesse/kevin/laura/ann) and midjourney-raw-only characters (amy) become operator-actionable items (renders or canon-named refs needed).
- Append two `MISSING_ARTIFACTS` queue entries (`MA-ANIM-07-RENDERS-EMPTY`, `MA-ANIM-07-MIDJOURNEY-RAW`) so the queue surfaces them at the next `apex_status` run.

Out of scope:
- Regenerating any character art (ComfyUI work belongs to a follow-on phase once operator provides direction on which characters to prioritize).
- Renaming midjourney refs to canonical filenames (operator-owned art-direction call).
- Editing character canon, `PROJECT_SPEC.md`, or `status.json` files.
- AGEN core-five recovery (declared deleted; separate workstream per `handover_apex_anim_wo_2026-06-07.md` §6 and `project_agen_five_agent_state_2026-06-07.md`).
- Extending scene descriptors (`ANIM-04-scene-descriptors.json` only has MagicalRealmPlayground; per ANIM-04 handover this is operator-extended, not agent-extended).

## 4. Access matrix (per PLAN_CRITERIA §8)

| Resource | Path | RW | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-07` | RW | env_sync GitHub PAT |
| APEX root | `C:/Users/Owner/Repos/code-artifacts/apex/` | RW | local |
| Governance | `C:/Users/Owner/apex_governance/` | RW | local |
| Char render tree | `X:/Automations/apex/projects/jesse_animate/characters/` | R | QNAP NAS share |
| PROJECT_SPEC | `X:/Automations/apex/projects/jesse_animate/PROJECT_SPEC.md` | R | QNAP NAS share |
| Codex CLI | `codex` (v0.135.0, gpt-5.5, ChatGPT auth) | RW | shell PATH |

Codex auth resolved via ChatGPT subscription; `CODEX_MODEL=gpt-5.5` per the env-key-conflict feedback memory (`feedback_codex_bridge_openai_key_conflict.md`).

## 5. Inputs (with SHAs)

Authoritative inputs read by this phase:
- ANIM-03 manifest: `apex/docs/anim/ANIM-03-reference-pack-manifest.json` (current HEAD blob).
- ANIM-03 agent: `apex/registry/muscle_character_build_agent.py` HEAD blob (extension target).
- PROJECT_SPEC §1.8 canon rows on the NAS share (read-only).
- Render trees under `X:/.../characters/{grog,lirian,jesse,kevin,amy,laura,ann}/`.

## 6. Outputs

- `apex/registry/muscle_character_build_agent.py` (edited — backward-compatible extension).
- `apex/docs/anim/ANIM-03-reference-pack-manifest.json` (additive: new `grog` and `lirian` entries).
- `apex/docs/anim/bibles/ANIM_Jesse-Adventures_Grog_bible_v1.md` (new).
- `apex/docs/anim/bibles/ANIM_Jesse-Adventures_Lirian_bible_v1.md` (new).
- `apex/docs/anim/ANIM-07-cast-coverage.json` (new — coverage report).
- `apex/audit/anim-03/grog-build-<ts>.json` + `lirian-build-<ts>.json` (per-run audits — written by the agent into its origin-phase audit dir, matching §3 "land at the same paths as ANIM-03"; the manifest follows the same rule).
- `apex/audit/anim-07/cast-census-<ts>.json` (pre-flight census evidence — this phase's own evidence, written separately from agent runs).
- `apex/docs/spec/SPEC-ANIM-07.md` (this file).
- `apex_governance/handovers/ANIM-07.handover.md` (cert handover).
- `apex_governance/certs/CERT-ANIM-07.json` (cert) + append to `certs/index.json`.
- `apex_governance/codex_runs/ANIM-07/round*.txt` (transcripts).

## 7. Definition of Done

- Extension committed; existing galinda + emma re-runs still return `WILL_OVERWRITE_REFUSED` exit 5 (no regression on prior subjects).
- `grog` and `lirian` builds succeed (exit 0, status `OK`, pack size ≥ `PACK_MIN`=4).
- Bibles, manifest entries, and audit JSONs present at output paths.
- `ANIM-07-cast-coverage.json` enumerates all 9 cast members with disposition (`BUILT-IN-ANIM-03`, `BUILT-IN-ANIM-07`, `NO_RENDERS`, `MIDJOURNEY_RAW_ONLY`).
- Two `MA-*` rows appended to `MISSING_ARTIFACTS.queue.json`.
- Codex adversarial-review silent-twice (R15: two consecutive passes, no fresh CRITICAL/HIGH); ship-gate `/codex:review` clean.
- Cert minted with full doctrine-conformance table; handover written; PR opened via `_make_pr_api.py` and branch protection acknowledged (operator merges).

## 8. Codex commands required

| Stage | Command | Persistence |
|---|---|---|
| Spec + diff | `CODEX_MODEL=gpt-5.5 codex exec` adversarial bundle (inline-stdin, per ANIM-01..06 pattern) | `apex_governance/codex_runs/ANIM-07/round<n>.txt` |
| Ship-gate | `CODEX_MODEL=gpt-5.5 codex exec` ship-gate review | same dir, `ship-gate.txt` |

Inline-stdin bundle is used because the Windows codex sandbox blocks shell file reads — same workaround as ANIM-01..06.

## 9. Test plan

- Unit: `--dry-run` against grog + lirian → pack preview shows ≥4 entries each, roles distinct, sha256s computed.
- Unit: `--dry-run` against jesse → render_count=0, pack_preview=[].
- Integration: full build of grog + lirian writes bible + manifest + audit; second run returns `WILL_OVERWRITE_REFUSED` exit 5.
- Regression: `emma --dry-run` returns pack composition unchanged from ANIM-03 (same six role/path pairs). `galinda --dry-run` shows two ADDITIVE picks (`turnaround_seed`, `expression_happy`) because the operator added 15 PNGs to galinda's `kontext_sheets/` since ANIM-03; her existing bible is not regenerated without `--force` (verified by re-running the agent without `--force` and confirming exit 5 `WILL_OVERWRITE_REFUSED`), so the on-disk manifest entry remains the ANIM-03 5-entry pack until operator opts to refresh.
- Anti-leakage: `amy --dry-run` returns pack_size=0 (down from 1 in an interim test) because `/midjourney_refs/` UUID filenames are now anti-matched in `pick_pack`. amy still exits PACK_TOO_SMALL on full build.
- Golden: `ANIM-07-cast-coverage.json` schema matches a stable shape (validated by Codex review).

## 10. Pass criteria (binary)

- [ ] Agent extension backward-compatible (galinda + emma unchanged).
- [ ] grog + lirian bibles exist with PACK_MIN+ entries and sha256-anchored references.
- [ ] Cast coverage report enumerates all 9 members.
- [ ] `MA-ANIM-07-RENDERS-EMPTY` and `MA-ANIM-07-MIDJOURNEY-RAW` in MISSING_ARTIFACTS queue.
- [ ] Codex silent-twice + clean ship-gate.
- [ ] Cert minted + index updated + handover written + PR opened.

## 11. Rollback plan

- Trigger: any post-build assertion (regression on galinda/emma re-run, sha256 drift, schema violation) fires.
- Revert: `git revert <commit>` on `phase/ANIM-07`; manifest add-only entries dropped via revert; bible files removed in revert commit.
- Data restore: no data destruction — manifest is additive-only; bibles are new files.

## 12. Doctrine conformance table

Filled in at cert time. R15 (silent-twice), R16 (loop caps), R19 (research — satisfied by ANIM-01 capability map; this is an EXTEND of an existing muscle), P1/P2 (Codex audits, Claude builds), O2 (model logged: `gpt-5.5`), O6 (transcripts persisted), C1–C4 + C8 (cert evidence rows).

## 13. Cleanup report (PLAN_CRITERIA §12)

- Files deleted: none expected (additive phase).
- Files renamed: none.
- Paths reconciled: none (no `bermi` paths touched).
- Stubs/TODOs: none introduced.
- Sandbox dir: not used.
- Scratch dir: not used.
- Carry-over stash: a prior-session `git stash` was recorded at branch creation containing `muscle_capability_report.py` (APEX-MB-PY-00102) + work_gate station-alias improvement + tool-menu updates + audit telemetry. Out of scope for ANIM-07. Operator action recommended: reconcile in a separate governance phase.
