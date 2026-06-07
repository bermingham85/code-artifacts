#!/usr/bin/env python3
"""APEX-MB-PY-00115 muscle_assembly_agent.py

Assembly/QC agent — wraps S7 (cut clips to lyrics) + S8 (QC tracking) of the ANIM pipeline.

Modes:
  --list-deliverables
  --catalog-deliverable <SceneSlug> [--force]
  --plan-concat <SceneSlug>

Wraps the real on-disk assembly route (per ANIM-01 §0.1):
  X:/.../grog_playground/muscle_music_video.py --mode stitch
  X:/.../grog_playground/stitch_video.py

Inherits ANIM-05's trust boundary (operator-owned QNAP NAS share, no untrusted writers).
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

SLUG_RE = re.compile(r"^[A-Z][A-Za-z0-9]{0,31}$")
REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
ASSEMBLY_MANIFEST_PATH = REPO_ROOT / "apex/docs/anim/ANIM-06-assembly-manifest.json"
ANIM05_MANIFEST_PATH = REPO_ROOT / "apex/docs/anim/ANIM-05-clip-pack-manifest.json"
AUDIT_ROOT = REPO_ROOT / "apex/audit/anim-06"

# Per-scene shipped-deliverable + stitch-wrapper bindings.
SCENE_DELIVERABLES = {
    "MagicalRealmPlayground": {
        "deliverable_mp4": Path(r"X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/grog_too_big_for_playground_mv.mp4"),
        "lyrics_json": Path(r"X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/lyrics_timestamped.json"),
        "stitch_wrapper": "X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/muscle_music_video.py --mode stitch --shot-list <shot_list.json>",
        "stitch_sibling": "X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/stitch_video.py",
        "character": "grog",
        "brand": "Jesse-Adventures",
        "song": "Grog Too Big For Playground (music video)",
    },
}


def validate_slug(slug: str) -> dict | None:
    if not SLUG_RE.match(slug):
        return {"slug": slug, "status": "INVALID_SLUG", "expected_regex": SLUG_RE.pattern}
    return None


def hash_file_handle_bound(p: Path, root_resolved: Path) -> tuple[str, int, Path] | None:
    """Same TOCTOU defense as ANIM-05 muscle_video_agent.annotate_clip()."""
    try:
        if p.is_symlink():
            return None
        target_pre = p.resolve(strict=True)
        if Path(os.path.commonpath([str(target_pre), str(root_resolved)])) != root_resolved:
            return None
        fd = os.open(str(target_pre), os.O_RDONLY | getattr(os, "O_BINARY", 0))
        try:
            st = os.fstat(fd)
            size = st.st_size
            h = hashlib.sha256()
            while True:
                b = os.read(fd, 1 << 20)
                if not b:
                    break
                h.update(b)
            digest = h.hexdigest()
        finally:
            os.close(fd)
        target_post = p.resolve(strict=True)
        if target_post != target_pre:
            return None
        if Path(os.path.commonpath([str(target_post), str(root_resolved)])) != root_resolved:
            return None
        return digest, size, target_post
    except (FileNotFoundError, OSError, ValueError):
        return None


def total_duration_from_lyrics(lyrics_path: Path) -> float | None:
    """Read lyrics_timestamped.json and return the largest .end timestamp across rows.

    Tolerates two shapes: list-of-line-dicts (flat) and {lines:[]}/{lyrics:[]} wrappers.
    """
    if not lyrics_path.is_file():
        return None
    try:
        data = json.loads(lyrics_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(data, list):
        lines = data
    elif isinstance(data, dict):
        lines = data.get("lines") or data.get("lyrics") or []
    else:
        return None
    if not lines:
        return None
    max_end = None
    for row in lines:
        if not isinstance(row, dict):
            continue
        end = row.get("end")
        if isinstance(end, (int, float)):
            if max_end is None or end > max_end:
                max_end = float(end)
    return max_end


def catalog_deliverable(slug: str, force: bool) -> dict:
    bad = validate_slug(slug)
    if bad:
        return bad
    if slug not in SCENE_DELIVERABLES:
        return {"slug": slug, "status": "UNKNOWN_SCENE",
                "known": sorted(SCENE_DELIVERABLES.keys())}
    binding = SCENE_DELIVERABLES[slug]
    mp4 = binding["deliverable_mp4"]
    if not mp4.is_file():
        return {"slug": slug, "status": "DELIVERABLE_MISSING",
                "expected_path": str(mp4)}

    manifest = (json.loads(ASSEMBLY_MANIFEST_PATH.read_text(encoding="utf-8"))
                if ASSEMBLY_MANIFEST_PATH.is_file()
                else {"phase": "ANIM-06", "schema_version": 1, "scenes": {}})
    if slug in manifest.get("scenes", {}) and not force:
        return {"slug": slug, "status": "WILL_OVERWRITE_REFUSED",
                "existing_entry_path": manifest["scenes"][slug].get("deliverable_mp4")}

    try:
        root_resolved = mp4.parent.resolve(strict=True)
    except (FileNotFoundError, OSError):
        return {"slug": slug, "status": "DELIVERABLE_PARENT_MISSING"}
    h = hash_file_handle_bound(mp4, root_resolved)
    if h is None:
        return {"slug": slug, "status": "DELIVERABLE_VALIDATION_FAILED",
                "path": str(mp4)}
    digest, size, resolved = h

    # Count production clips for this scene from the ANIM-05 manifest.
    clip_count = 0
    if ANIM05_MANIFEST_PATH.is_file():
        anim05 = json.loads(ANIM05_MANIFEST_PATH.read_text(encoding="utf-8"))
        scene_block = anim05.get("scenes", {}).get(slug, {})
        clip_count = scene_block.get("production_count", 0)

    lyrics_duration = total_duration_from_lyrics(binding["lyrics_json"])

    entry = {
        "scene_slug": slug,
        "brand": binding["brand"],
        "character": binding["character"],
        "song": binding["song"],
        "deliverable_mp4": str(mp4).replace("\\", "/"),
        "resolved_path": str(resolved).replace("\\", "/"),
        "sha256": digest,
        "size_bytes": size,
        "production_clip_count_from_anim05": clip_count,
        "lyrics_json": str(binding["lyrics_json"]).replace("\\", "/"),
        "lyrics_total_duration_seconds": lyrics_duration,
        "stitch_wrapper_invocation": binding["stitch_wrapper"],
        "stitch_sibling": binding["stitch_sibling"],
        "phase_state_anchor": "session_2026_04_01_mv.shots = '20/20 complete — 19 Wan2.2 i2v two-stage MoE + 1 skip'",
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    manifest.setdefault("scenes", {})[slug] = entry
    ASSEMBLY_MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    ASSEMBLY_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    (AUDIT_ROOT / f"deliverable-{slug.lower()}-{ts}.json").write_text(json.dumps({
        "slug": slug, "sha256": digest, "size": size, "timestamp": ts, "status": "OK"
    }, indent=2))
    return {**entry, "status": "OK"}


def plan_concat(slug: str) -> dict:
    bad = validate_slug(slug)
    if bad:
        return bad
    if not ANIM05_MANIFEST_PATH.is_file():
        return {"slug": slug, "status": "ANIM05_MANIFEST_MISSING"}
    anim05 = json.loads(ANIM05_MANIFEST_PATH.read_text(encoding="utf-8"))
    scene = anim05.get("scenes", {}).get(slug)
    if not scene:
        return {"slug": slug, "status": "SCENE_NOT_IN_ANIM05_MANIFEST",
                "known": sorted(anim05.get("scenes", {}).keys())}
    production_clips = [c for c in scene.get("clips", []) if c.get("role") == "production"]
    # Sort by shot_id (numeric where possible) to enforce playback order.
    def _key(c):
        sid = c.get("shot_id")
        try:
            return (0, int(sid))
        except (TypeError, ValueError):
            return (1, str(sid))
    production_clips.sort(key=_key)
    if slug not in SCENE_DELIVERABLES:
        return {"slug": slug, "status": "UNKNOWN_SCENE"}
    binding = SCENE_DELIVERABLES[slug]
    return {
        "slug": slug,
        "status": "PLAN",
        "wrapper_invocation": binding["stitch_wrapper"],
        "concat_lines": [
            f"file '{c['path']}'  # shot {c.get('shot_id')} duration {c.get('duration_seconds')}s"
            for c in production_clips
        ],
        "production_count": len(production_clips),
        "lyrics_json": str(binding["lyrics_json"]).replace("\\", "/"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-deliverables", action="store_true")
    ap.add_argument("--catalog-deliverable")
    ap.add_argument("--plan-concat")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if args.list_deliverables:
        manifest = (json.loads(ASSEMBLY_MANIFEST_PATH.read_text(encoding="utf-8"))
                    if ASSEMBLY_MANIFEST_PATH.is_file()
                    else {"scenes": {}})
        print(json.dumps(manifest, indent=2))
        return 0
    if args.catalog_deliverable:
        result = catalog_deliverable(args.catalog_deliverable, args.force)
        print(json.dumps(result, indent=2))
        code_for = {"OK": 0, "WILL_OVERWRITE_REFUSED": 5, "INVALID_SLUG": 6,
                    "UNKNOWN_SCENE": 9, "DELIVERABLE_MISSING": 8,
                    "DELIVERABLE_PARENT_MISSING": 8,
                    "DELIVERABLE_VALIDATION_FAILED": 8}
        return code_for.get(result.get("status", ""), 4)
    if args.plan_concat:
        result = plan_concat(args.plan_concat)
        print(json.dumps(result, indent=2))
        code_for = {"PLAN": 0, "INVALID_SLUG": 6, "ANIM05_MANIFEST_MISSING": 9,
                    "SCENE_NOT_IN_ANIM05_MANIFEST": 9, "UNKNOWN_SCENE": 9}
        return code_for.get(result.get("status", ""), 4)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
