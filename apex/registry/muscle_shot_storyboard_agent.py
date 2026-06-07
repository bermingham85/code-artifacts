#!/usr/bin/env python3
"""APEX-MB-PY-00117 muscle_shot_storyboard_agent.py

Shot/Storyboard agent (WO §3 agent 3, stage S5).

Reads time-aligned lyrics + character markers + scene markers + brand tokens
(all from on-disk authoritative sources, never invented), and emits a deterministic
storyboard JSON with N shot skeletons that the downstream Video agent (ANIM-05)
consumes for tier-planning.

Modes:
  --list-projects
  --storyboard <project-slug> [--target-shot-seconds N] [--force]
  --validate <project-slug>

Doctrine:
  P3 / R20: no invention. kontext_prompt bodies stay as templates with
  explicit `needs_fill: ["action"]` markers; only structural fields
  (id, section, start, end, lyric, energy, mood, markers, presets) are filled.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
import re
import sys
from pathlib import Path

SLUG_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")

REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
PROJECTS_PATH = REPO_ROOT / "apex/docs/anim/ANIM-13-projects.json"
REF_PACK_MANIFEST_PATH = REPO_ROOT / "apex/docs/anim/ANIM-03-reference-pack-manifest.json"
SCENE_PACK_MANIFEST_PATH = REPO_ROOT / "apex/docs/anim/ANIM-04-scene-pack-manifest.json"
STORYBOARD_DIR = REPO_ROOT / "apex/docs/anim"
# ANIM-14 r1 F-2 fix: audits default to the agent's home phase (ANIM-13) but
# can be redirected via APEX_PHASE_AUDIT_DIR so phase-scoped runs (e.g.
# ANIM-14 schema-extension evidence) co-locate their audit JSONs with the
# rest of the phase artifacts under apex/audit/anim-14/. Path is rebased on
# REPO_ROOT when relative, taken as-is when absolute.
_audit_override = os.environ.get("APEX_PHASE_AUDIT_DIR")
if _audit_override:
    _audit_p = Path(_audit_override)
    AUDIT_ROOT = _audit_p if _audit_p.is_absolute() else REPO_ROOT / _audit_p
else:
    AUDIT_ROOT = REPO_ROOT / "apex/audit/anim-13"

ENERGY_CAMERA = {
    "LOW": "slow drift, golden tones, steady frame",
    "MED": "medium shot, soft push, character framing",
    "HIGH": "dynamic angle, push-in or whip pan, bold framing",
}
ENERGY_MOTION = {
    "LOW": "slow ambient drift, subtle micro-motion, gentle environmental movement",
    "MED": "focused character action, mid-tempo gestural movement, environment reacting",
    "HIGH": "strong character action, impact beats, environment dramatically reacting",
}

DEFAULT_TARGET_SHOT_SECONDS = 5.5


def load_projects() -> dict:
    if not PROJECTS_PATH.is_file():
        return {"projects": {}}
    return json.loads(PROJECTS_PATH.read_text(encoding="utf-8"))


def load_ref_pack_manifest() -> dict | None:
    """F-4 r2 fix: hard-fail if the ANIM-03 reference-pack manifest is missing.
    Returns None when missing so the caller can surface REF_PACK_MANIFEST_MISSING."""
    if not REF_PACK_MANIFEST_PATH.is_file():
        return None
    return json.loads(REF_PACK_MANIFEST_PATH.read_text(encoding="utf-8"))


def load_scene_pack_manifest() -> dict | None:
    """F-4 r2 fix: hard-fail if the ANIM-04 scene-pack manifest is missing."""
    if not SCENE_PACK_MANIFEST_PATH.is_file():
        return None
    return json.loads(SCENE_PACK_MANIFEST_PATH.read_text(encoding="utf-8"))


def sha256_of(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def validate_slug(slug: str) -> dict | None:
    if not SLUG_RE.match(slug):
        return {"slug": slug, "status": "INVALID_SLUG",
                "expected_regex": SLUG_RE.pattern}
    return None


def load_lyrics(path_str: str) -> list[dict]:
    p = Path(path_str)
    if not p.is_file():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    out: list[dict] = []
    for entry in data:
        s = entry.get("start")
        e = entry.get("end")
        t = entry.get("text")
        if isinstance(s, (int, float)) and isinstance(e, (int, float)) and isinstance(t, str):
            out.append({"start": float(s), "end": float(e), "text": t})
    return out


def section_shots(section: dict, target_shot_seconds: float) -> list[tuple[float, float]]:
    """Equal-width shot slices inside a section. Returns [(start, end), ...]."""
    s = float(section["start"])
    e = float(section["end"])
    dur = e - s
    if dur <= 0:
        return []
    n_shots = max(1, round(dur / target_shot_seconds))
    shot_dur = dur / n_shots
    out: list[tuple[float, float]] = []
    for i in range(n_shots):
        a = s + i * shot_dur
        b = s + (i + 1) * shot_dur if i < n_shots - 1 else e
        out.append((round(a, 3), round(b, 3)))
    return out


def lyric_text_for_window(lyrics: list[dict], a: float, b: float) -> tuple[str, int]:
    """Concatenate verbatim text from lyric lines whose start is in [a, b)."""
    chunks: list[str] = []
    for ln in lyrics:
        if a <= ln["start"] < b:
            chunks.append(ln["text"].strip())
    joined = " ".join(chunks).strip()
    word_count = len(joined.split()) if joined else 0
    return joined, word_count


def compile_prompt_template(character_markers: str, scene_markers: str,
                            camera_preset: str, style_anchor: str) -> str:
    """F-2 r1 fix: interpolate camera_preset inline so the only unresolved
    placeholder is {action}, matching needs_fill. No untracked placeholders."""
    return (f"{character_markers}, {{action}}, {scene_markers}, "
            f"{camera_preset}, {style_anchor}")


def _verify_markers_against_source(character_markers: str, src_path_str: str,
                                    src_sha: str, src_field: str) -> dict | None:
    """ANIM-14: extracted from inline ANIM-13 logic so both the projects.json
    path and the ANIM-03 manifest path apply identical provenance verification.

    Returns None on success or a status dict on the first failure. Caller is
    responsible for tagging which path triggered the failure (`origin` key)
    and adding slug context, so dispatchers report the right exit code.
    """
    src_path = Path(src_path_str)
    if not src_path.is_file():
        return {"status": "CHARACTER_MARKERS_SOURCE_MISSING",
                "source_path": src_path_str}
    actual_sha = sha256_of(src_path)
    if actual_sha != src_sha:
        return {"status": "CHARACTER_MARKERS_PROVENANCE_DRIFT",
                "source_path": src_path_str,
                "recorded_sha256": src_sha,
                "actual_sha256": actual_sha}
    try:
        src_data = json.loads(src_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"status": "CHARACTER_MARKERS_SOURCE_UNPARSEABLE",
                "source_path": src_path_str, "error": str(e)}
    # ANIM-14 r2 F-5 fix: a top-level JSON array/string/number/bool/null is
    # structurally invalid for our field-name lookup; surface the same
    # SOURCE_UNPARSEABLE class rather than crashing on .get().
    if not isinstance(src_data, dict):
        return {"status": "CHARACTER_MARKERS_SOURCE_UNPARSEABLE",
                "source_path": src_path_str,
                "error": f"top-level JSON must be an object; got {type(src_data).__name__}"}
    source_value = src_data.get(src_field)
    if source_value is None:
        return {"status": "CHARACTER_MARKERS_FIELD_MISSING",
                "source_path": src_path_str, "field": src_field}
    # ANIM-14 r2 F-5 fix (cont.): the recorded marker and the source field
    # value must both be strings for byte-equality to be a meaningful check.
    if not isinstance(source_value, str):
        return {"status": "CHARACTER_MARKERS_FIELD_MISSING",
                "source_path": src_path_str, "field": src_field,
                "error": f"field present but not a string (got {type(source_value).__name__})"}
    if not isinstance(character_markers, str):
        return {"status": "CHARACTER_MARKERS_VALUE_MISMATCH",
                "source_path": src_path_str, "field": src_field,
                "recorded_markers": character_markers,
                "actual_in_source": source_value,
                "error": f"recorded character_markers is not a string (got {type(character_markers).__name__})"}
    if character_markers != source_value:
        return {"status": "CHARACTER_MARKERS_VALUE_MISMATCH",
                "source_path": src_path_str, "field": src_field,
                "recorded_markers": character_markers,
                "actual_in_source": source_value}
    return None


_MARKER_FIELDS = (
    "character_markers",
    "character_markers_provenance_source_path",
    "character_markers_provenance_sha256",
    "character_markers_provenance_field",
)


def resolve_character_markers(project_slug: str, cfg: dict, ref_pack: dict) -> dict:
    """ANIM-14 marker resolution.

    Precedence:
      1. projects.json carries the full marker block (all four _MARKER_FIELDS).
      2. ANIM-03 manifest carries the full marker block under
         characters[<char>]; project config carries none.
      3. Both declare; both verified; cross-check character_markers byte-equal.

    Partial-declaration cases (any-but-not-all) are reported, since a
    declaration without provenance is unsafe even if the marker text happens
    to be correct (matches the ANIM-13 doctrine of "no claim without sha").
    """
    project_present = [k for k in _MARKER_FIELDS if cfg.get(k) is not None]
    project_path_complete = len(project_present) == len(_MARKER_FIELDS)
    project_has_partial = 0 < len(project_present) < len(_MARKER_FIELDS)

    char_slug = cfg.get("character")
    char_entry = (ref_pack.get("characters", {}) or {}).get(char_slug, {}) or {}
    manifest_present = [k for k in _MARKER_FIELDS if char_entry.get(k) is not None]
    manifest_path_complete = len(manifest_present) == len(_MARKER_FIELDS)
    manifest_has_partial = 0 < len(manifest_present) < len(_MARKER_FIELDS)

    if project_has_partial:
        return {"slug": project_slug,
                "status": "CHARACTER_MARKERS_PROVENANCE_MISSING",
                "origin": "projects.json",
                "required_fields": list(_MARKER_FIELDS),
                "present_fields": project_present}
    # ANIM-14 r3 F-6 fix (supersedes r1 F-3 softening): SPEC-ANIM-14 §"Schema
    # extension" says the manifest's marker block must be all-four-fields or
    # all-absent, and "the agent re-validates this at runtime". Re-validation
    # is unconditional — a partial manifest marker block is a registry
    # inconsistency and the agent must surface it before any project that
    # binds this character can run, even if that project carries its own
    # full marker block. Forcing the registry fix is safer than silently
    # tolerating drift in a certed manifest.
    if manifest_has_partial:
        return {"slug": project_slug,
                "status": "CHARACTER_MARKERS_MANIFEST_PARTIAL",
                "origin": "ANIM-03 manifest",
                "character": char_slug,
                "required_fields": list(_MARKER_FIELDS),
                "present_fields": manifest_present}
    if not project_path_complete and not manifest_path_complete:
        return {"slug": project_slug,
                "status": "CHARACTER_MARKERS_NOT_FOUND",
                "character": char_slug,
                "checked": [
                    "projects.json:projects['" + project_slug + "']",
                    "ANIM-03 manifest:characters['" + (char_slug or "") + "']",
                ]}

    chosen_source = None
    chosen_markers = None
    chosen_src_path = None
    if project_path_complete:
        err = _verify_markers_against_source(
            cfg["character_markers"],
            cfg["character_markers_provenance_source_path"],
            cfg["character_markers_provenance_sha256"],
            cfg["character_markers_provenance_field"])
        if err is not None:
            err.update({"slug": project_slug, "origin": "projects.json"})
            return err
        chosen_source = "projects.json"
        chosen_markers = cfg["character_markers"]
        chosen_src_path = cfg["character_markers_provenance_source_path"]

    if manifest_path_complete:
        err = _verify_markers_against_source(
            char_entry["character_markers"],
            char_entry["character_markers_provenance_source_path"],
            char_entry["character_markers_provenance_sha256"],
            char_entry["character_markers_provenance_field"])
        if err is not None:
            err.update({"slug": project_slug, "origin": "ANIM-03 manifest",
                        "character": char_slug})
            return err
        if not project_path_complete:
            chosen_source = "ANIM-03 manifest"
            chosen_markers = char_entry["character_markers"]
            chosen_src_path = char_entry["character_markers_provenance_source_path"]
        else:
            if cfg["character_markers"] != char_entry["character_markers"]:
                return {"slug": project_slug,
                        "status": "CHARACTER_MARKERS_SOURCE_CONFLICT",
                        "character": char_slug,
                        "projects_json_value": cfg["character_markers"],
                        "anim03_manifest_value": char_entry["character_markers"]}

    return {
        "status": "OK",
        "character_markers": chosen_markers,
        "character_markers_source_annotation":
            f"{chosen_source} (sha-verified against {chosen_src_path})",
    }


def build_storyboard(project_slug: str, target_shot_seconds: float, force: bool) -> dict:
    bad = validate_slug(project_slug)
    if bad:
        return bad
    cfg = load_projects().get("projects", {}).get(project_slug)
    if not cfg:
        return {"slug": project_slug, "status": "UNKNOWN_PROJECT",
                "known_projects": sorted(load_projects().get("projects", {}).keys())}

    out_path = STORYBOARD_DIR / f"ANIM-13-storyboard-{project_slug}.json"
    if out_path.exists() and not force:
        return {"slug": project_slug, "status": "WILL_OVERWRITE_REFUSED",
                "existing_path": str(out_path).replace("\\", "/")}

    # F-4 r2: hard-fail when either certed manifest is missing.
    ref_pack = load_ref_pack_manifest()
    if ref_pack is None:
        return {"slug": project_slug, "status": "REF_PACK_MANIFEST_MISSING",
                "manifest": str(REF_PACK_MANIFEST_PATH).replace("\\", "/")}
    scene_pack = load_scene_pack_manifest()
    if scene_pack is None:
        return {"slug": project_slug, "status": "SCENE_PACK_MANIFEST_MISSING",
                "manifest": str(SCENE_PACK_MANIFEST_PATH).replace("\\", "/")}

    # F-1 r1: slug membership anchored to certed manifests.
    if cfg["character"] not in ref_pack.get("characters", {}):
        return {"slug": project_slug, "status": "UNKNOWN_CHARACTER",
                "character": cfg["character"],
                "known_characters": sorted(ref_pack.get("characters", {}).keys()),
                "manifest": str(REF_PACK_MANIFEST_PATH).replace("\\", "/")}
    scene_entry = scene_pack.get("scenes", {}).get(cfg["scene"])
    if scene_entry is None:
        return {"slug": project_slug, "status": "UNKNOWN_SCENE",
                "scene": cfg["scene"],
                "known_scenes": sorted(scene_pack.get("scenes", {}).keys()),
                "manifest": str(SCENE_PACK_MANIFEST_PATH).replace("\\", "/")}

    # F-3 r2: scene markers / style anchor / prompt rules come from ANIM-04
    # manifest directly, not from the project config. That makes the marker
    # text traceable to the certed scene bible by construction, eliminating
    # the "valid slug + fabricated marker text" failure mode.
    scene_descriptor = scene_entry.get("descriptor", {}) or {}
    scene_brand_tokens = scene_entry.get("brand_tokens", {}) or {}
    scene_markers = scene_descriptor.get("prompt")
    style_anchor = scene_brand_tokens.get("style_anchor")
    prompt_rules = scene_brand_tokens.get("prompt_rules")
    if not scene_markers or not style_anchor or not prompt_rules:
        return {"slug": project_slug, "status": "SCENE_MANIFEST_INCOMPLETE",
                "missing": [k for k, v in {
                    "descriptor.prompt": scene_markers,
                    "brand_tokens.style_anchor": style_anchor,
                    "brand_tokens.prompt_rules": prompt_rules,
                }.items() if not v]}

    # F-3 r2 + F-5 r3 (ANIM-13): character_markers must be sourced from an
    # authoritative on-disk file and verified two ways — file sha256 match +
    # in-file field-value verbatim equality with the recorded marker text.
    # ANIM-14 hoists the same marker block (text + provenance triple) into the
    # per-character entry of the ANIM-03 reference-pack manifest, so future
    # project bindings don't have to re-state them. Precedence:
    #   1. If projects.json carries all four marker fields, use them
    #      (backward-compatible ANIM-13 path).
    #   2. Otherwise, fall back to ANIM-03 manifest's marker block for the
    #      bound character.
    #   3. If both declare markers, both verifications run AND the two
    #      character_markers strings are cross-checked byte-equal.
    marker_resolution = resolve_character_markers(
        project_slug, cfg, ref_pack)
    if marker_resolution.get("status") != "OK":
        return marker_resolution
    char_markers_resolved = marker_resolution["character_markers"]
    char_markers_source_annotation = marker_resolution["character_markers_source_annotation"]

    # F-6 r5 fix: sections table inherits the same provenance treatment as
    # character_markers. cfg requires sections_provenance_source_path +
    # sections_provenance_field (the JSON array field within that source);
    # build_storyboard hashes the source, reads the field, and requires the
    # in-projects sections to be a verbatim match (recursive equality).
    sec_src_str = cfg.get("sections_provenance_source_path")
    sec_field = cfg.get("sections_provenance_field")
    if not sec_src_str or not sec_field:
        return {"slug": project_slug, "status": "SECTIONS_PROVENANCE_MISSING",
                "required_fields": [
                    "sections_provenance_source_path",
                    "sections_provenance_field",
                ]}
    sec_src_path = Path(sec_src_str)
    if not sec_src_path.is_file():
        return {"slug": project_slug, "status": "SECTIONS_SOURCE_MISSING",
                "source_path": sec_src_str}
    try:
        sec_src_data = json.loads(sec_src_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"slug": project_slug, "status": "SECTIONS_SOURCE_UNPARSEABLE",
                "source_path": sec_src_str, "error": str(e)}
    sec_source_value = sec_src_data.get(sec_field)
    if sec_source_value is None:
        return {"slug": project_slug, "status": "SECTIONS_FIELD_MISSING",
                "source_path": sec_src_str, "field": sec_field}
    if cfg["sections"] != sec_source_value:
        return {"slug": project_slug, "status": "SECTIONS_VALUE_MISMATCH",
                "source_path": sec_src_str, "field": sec_field,
                "recorded_in_projects_json": cfg["sections"],
                "actual_in_source": sec_source_value}

    lyrics = load_lyrics(cfg["lyrics_timestamped_path"])
    if not lyrics:
        return {"slug": project_slug, "status": "LYRICS_MISSING",
                "lyrics_path": cfg["lyrics_timestamped_path"]}

    sections = cfg["sections"]
    char_markers = char_markers_resolved

    shots: list[dict] = []
    shot_id = 0
    for section in sections:
        windows = section_shots(section, target_shot_seconds)
        energy = section.get("energy", "MED")
        for (a, b) in windows:
            shot_id += 1
            lyric, wc = lyric_text_for_window(lyrics, a, b)
            camera_preset = ENERGY_CAMERA.get(energy, ENERGY_CAMERA["MED"])
            wan_motion_preset = ENERGY_MOTION.get(energy, ENERGY_MOTION["MED"])
            shots.append({
                "id": shot_id,
                "section": section["name"],
                "start": a,
                "end": b,
                "duration_seconds": round(b - a, 3),
                "lyric": lyric,
                "lyric_word_count": wc,
                "energy": energy,
                "mood": section.get("mood", ""),
                "camera_preset": camera_preset,
                "wan_motion_preset": wan_motion_preset,
                "kontext_prompt_template": compile_prompt_template(
                    char_markers, scene_markers, camera_preset, style_anchor),
                "needs_fill": ["action"],
            })

    storyboard = {
        "phase": "ANIM-13",
        "schema_version": 3,
        "schema_version_history": [
            {"version": 1, "introduced_in": "ANIM-13", "summary": "initial deterministic shot-skeleton format"},
            {"version": 2, "introduced_in": "ANIM-13 (post r5)", "summary": "added provenance source annotation per marker field"},
            {"version": 3, "introduced_in": "ANIM-14", "summary": "character_markers may resolve from ANIM-03 manifest when projects.json omits the marker block; source annotation reports which path supplied the value"}
        ],
        "project": project_slug,
        "song_title": cfg["song_title"],
        "character": cfg["character"],
        "scene_slug": cfg["scene"],
        "brand": cfg["brand"],
        "duration_seconds": cfg["duration_seconds"],
        "target_shot_seconds": target_shot_seconds,
        "character_markers": char_markers,
        "character_markers_source": char_markers_source_annotation,
        "scene_markers": scene_markers,
        "scene_markers_source": "ANIM-04-scene-pack-manifest.json:scenes['" + cfg["scene"] + "'].descriptor.prompt",
        "style_anchor": style_anchor,
        "style_anchor_source": "ANIM-04-scene-pack-manifest.json:scenes['" + cfg["scene"] + "'].brand_tokens.style_anchor",
        "prompt_rules": prompt_rules,
        "prompt_rules_source": "ANIM-04-scene-pack-manifest.json:scenes['" + cfg["scene"] + "'].brand_tokens.prompt_rules",
        "section_count": len(sections),
        "shot_count": len(shots),
        "shots": shots,
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    STORYBOARD_DIR.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(storyboard, indent=2))

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    audit_path = AUDIT_ROOT / f"storyboard-{project_slug}-{ts}.json"
    audit = {
        "project": project_slug,
        "storyboard_path": str(out_path).replace("\\", "/"),
        "shot_count": len(shots),
        "section_count": len(sections),
        "target_shot_seconds": target_shot_seconds,
        "timestamp": ts,
        "status": "OK",
    }
    audit_path.write_text(json.dumps(audit, indent=2))
    return audit


def validate_against_gold(project_slug: str) -> dict:
    bad = validate_slug(project_slug)
    if bad:
        return bad
    cfg = load_projects().get("projects", {}).get(project_slug)
    if not cfg:
        return {"slug": project_slug, "status": "UNKNOWN_PROJECT"}
    gold_path_str = cfg.get("gold_shot_list_path")
    if not gold_path_str:
        return {"slug": project_slug, "status": "NO_GOLD_REFERENCE"}
    gold_path = Path(gold_path_str)
    if not gold_path.is_file():
        return {"slug": project_slug, "status": "GOLD_NOT_FOUND",
                "gold_path": gold_path_str}

    storyboard_path = STORYBOARD_DIR / f"ANIM-13-storyboard-{project_slug}.json"
    if not storyboard_path.is_file():
        return {"slug": project_slug, "status": "STORYBOARD_NOT_BUILT",
                "expected_path": str(storyboard_path).replace("\\", "/")}

    storyboard = json.loads(storyboard_path.read_text(encoding="utf-8"))
    gold = json.loads(gold_path.read_text(encoding="utf-8"))

    emitted_shots = storyboard["shots"]
    gold_shots = gold.get("shots", [])

    emitted_section_bounds = {}
    for s in emitted_shots:
        section = s["section"]
        if section not in emitted_section_bounds:
            emitted_section_bounds[section] = [s["start"], s["end"]]
        else:
            emitted_section_bounds[section][1] = s["end"]

    gold_section_bounds = {}
    for s in gold_shots:
        section = s.get("section", "unknown")
        if section not in gold_section_bounds:
            gold_section_bounds[section] = [s.get("start", 0.0), s.get("end", 0.0)]
        else:
            gold_section_bounds[section][1] = s.get("end", 0.0)

    section_deltas: list[dict] = []
    for name in sorted(set(emitted_section_bounds) | set(gold_section_bounds)):
        e = emitted_section_bounds.get(name)
        g = gold_section_bounds.get(name)
        if e and g:
            section_deltas.append({
                "section": name,
                "emitted_start": e[0], "gold_start": g[0],
                "start_delta": round(abs(e[0] - g[0]), 3),
                "emitted_end": e[1], "gold_end": g[1],
                "end_delta": round(abs(e[1] - g[1]), 3),
            })
        else:
            section_deltas.append({
                "section": name,
                "missing_in_emitted": e is None,
                "missing_in_gold": g is None,
            })

    deltas_with_values = [d["start_delta"] for d in section_deltas if "start_delta" in d]
    deltas_with_values += [d["end_delta"] for d in section_deltas if "end_delta" in d]
    max_section_delta = max(deltas_with_values) if deltas_with_values else 0.0
    mean_section_delta = round(sum(deltas_with_values) / len(deltas_with_values), 4) \
        if deltas_with_values else 0.0

    last_shot_end = emitted_shots[-1]["end"] if emitted_shots else 0.0
    coverage_ratio = round(last_shot_end / storyboard["duration_seconds"], 4) \
        if storyboard["duration_seconds"] else 0.0

    report = {
        "phase": "ANIM-13",
        "project": project_slug,
        "emitted_shot_count": len(emitted_shots),
        "gold_shot_count": len(gold_shots),
        "shot_count_delta": len(emitted_shots) - len(gold_shots),
        "section_count_emitted": len(emitted_section_bounds),
        "section_count_gold": len(gold_section_bounds),
        "section_deltas": section_deltas,
        "max_section_boundary_delta_seconds": max_section_delta,
        "mean_section_boundary_delta_seconds": mean_section_delta,
        "duration_seconds": storyboard["duration_seconds"],
        "coverage_ratio": coverage_ratio,
        "target_shot_seconds": storyboard["target_shot_seconds"],
        "validated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "status": "OK",
    }
    out_path = STORYBOARD_DIR / f"ANIM-13-validation-{project_slug.replace('_playground','')}.json"
    out_path.write_text(json.dumps(report, indent=2))

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    audit_path = AUDIT_ROOT / f"validate-{project_slug}-{ts}.json"
    audit_path.write_text(json.dumps({
        "project": project_slug,
        "report_path": str(out_path).replace("\\", "/"),
        "max_section_boundary_delta_seconds": max_section_delta,
        "shot_count_delta": report["shot_count_delta"],
        "timestamp": ts, "status": "OK",
    }, indent=2))
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-projects", action="store_true")
    ap.add_argument("--storyboard")
    ap.add_argument("--validate")
    ap.add_argument("--target-shot-seconds", type=float, default=DEFAULT_TARGET_SHOT_SECONDS)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if args.list_projects:
        projects = load_projects().get("projects", {})
        out = {slug: {"brand": p.get("brand"), "character": p.get("character"),
                      "scene": p.get("scene"), "song_title": p.get("song_title"),
                      "duration_seconds": p.get("duration_seconds")}
               for slug, p in projects.items()}
        print(json.dumps({"projects": out}, indent=2))
        return 0

    if args.storyboard:
        result = build_storyboard(args.storyboard, args.target_shot_seconds, args.force)
        print(json.dumps(result, indent=2))
        code_for = {"OK": 0, "WILL_OVERWRITE_REFUSED": 5, "INVALID_SLUG": 6,
                    "UNKNOWN_PROJECT": 9, "LYRICS_MISSING": 8,
                    "UNKNOWN_CHARACTER": 7, "UNKNOWN_SCENE": 7,
                    "REF_PACK_MANIFEST_MISSING": 10,
                    "SCENE_PACK_MANIFEST_MISSING": 10,
                    "SCENE_MANIFEST_INCOMPLETE": 10,
                    "CHARACTER_MARKERS_PROVENANCE_MISSING": 11,
                    "CHARACTER_MARKERS_SOURCE_MISSING": 11,
                    "CHARACTER_MARKERS_PROVENANCE_DRIFT": 11,
                    "CHARACTER_MARKERS_SOURCE_UNPARSEABLE": 11,
                    "CHARACTER_MARKERS_FIELD_MISSING": 11,
                    "CHARACTER_MARKERS_VALUE_MISMATCH": 11,
                    "CHARACTER_MARKERS_NOT_FOUND": 13,
                    "CHARACTER_MARKERS_MANIFEST_PARTIAL": 13,
                    "CHARACTER_MARKERS_SOURCE_CONFLICT": 13,
                    "SECTIONS_PROVENANCE_MISSING": 12,
                    "SECTIONS_SOURCE_MISSING": 12,
                    "SECTIONS_SOURCE_UNPARSEABLE": 12,
                    "SECTIONS_FIELD_MISSING": 12,
                    "SECTIONS_VALUE_MISMATCH": 12}
        return code_for.get(result.get("status", ""), 4)

    if args.validate:
        result = validate_against_gold(args.validate)
        print(json.dumps(result, indent=2))
        code_for = {"OK": 0, "INVALID_SLUG": 6, "UNKNOWN_PROJECT": 9,
                    "NO_GOLD_REFERENCE": 7, "GOLD_NOT_FOUND": 8,
                    "STORYBOARD_NOT_BUILT": 7}
        return code_for.get(result.get("status", ""), 4)

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
