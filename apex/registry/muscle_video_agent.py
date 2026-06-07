#!/usr/bin/env python3
"""APEX-MB-PY-00114 muscle_video_agent.py

Video agent — S6 image-to-video routing + clip catalog.

Modes:
  --list-tiers
  --catalog <scene-slug> [--force]
  --plan-tier <Wan22|LTX|Hunyuan|FalCloud> --shot <id> [--scene <slug>]

The live render path is delegated to the existing wrapper
muscle_music_video.py for Wan22/LTX/Hunyuan, or to a fal.ai shim (operator-gated G9).
The agent itself does not invoke heavy renders; --plan-tier is a dry-run plan.
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
TIER_RE = re.compile(r"^(Wan22|LTX|Hunyuan|FalCloud)$")
SHOT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")

REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
TIER_CONFIG_PATH = REPO_ROOT / "apex/docs/anim/ANIM-05-tier-config.json"
MANIFEST_PATH = REPO_ROOT / "apex/docs/anim/ANIM-05-clip-pack-manifest.json"
AUDIT_ROOT = REPO_ROOT / "apex/audit/anim-05"

# Per-scene clip roots (will grow as more scenes / brands are added).
CLIP_ROOTS = {
    "MagicalRealmPlayground": Path(r"X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/clips"),
}


def sha256_of(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_tier_config() -> dict:
    if not TIER_CONFIG_PATH.is_file():
        return {"tiers": {}}
    return json.loads(TIER_CONFIG_PATH.read_text(encoding="utf-8"))


def validate_slug(slug: str) -> dict | None:
    if not SLUG_RE.match(slug):
        return {"slug": slug, "status": "INVALID_SLUG",
                "expected_regex": SLUG_RE.pattern}
    return None


def discover_clips(scene_slug: str) -> list[Path]:
    root = CLIP_ROOTS.get(scene_slug)
    if not root or not root.is_dir():
        return []
    try:
        root_resolved = root.resolve(strict=True)
    except (FileNotFoundError, OSError):
        return []
    out: list[Path] = []
    for p in sorted(root.glob("*.mp4")):
        try:
            target = p.resolve(strict=True)
        except (FileNotFoundError, OSError):
            continue
        try:
            if Path(os.path.commonpath([str(target), str(root_resolved)])) != root_resolved:
                continue
        except ValueError:
            continue
        out.append(p)
    return out


def annotate_clip(p: Path, production_set_max: int, index: int) -> dict:
    return {
        "path": str(p).replace("\\", "/"),
        "sha256": sha256_of(p),
        "size": p.stat().st_size,
        "role": "production" if index < production_set_max else "extra",
        "index": index,
    }


def catalog_scene(scene_slug: str, force: bool) -> dict:
    bad = validate_slug(scene_slug)
    if bad:
        return bad
    if scene_slug not in CLIP_ROOTS:
        return {"slug": scene_slug, "status": "UNKNOWN_SCENE_ROOT",
                "known_scenes": sorted(CLIP_ROOTS.keys())}

    manifest = (json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
                if MANIFEST_PATH.is_file()
                else {"phase": "ANIM-05", "schema_version": 1, "scenes": {}})
    if scene_slug in manifest.get("scenes", {}) and not force:
        return {"slug": scene_slug, "status": "WILL_OVERWRITE_REFUSED",
                "existing_entry_paths": manifest["scenes"][scene_slug]["clip_root"]}

    clips = discover_clips(scene_slug)
    if not clips:
        return {"slug": scene_slug, "status": "CLIP_CATALOG_EMPTY",
                "clip_root": str(CLIP_ROOTS[scene_slug])}

    # PHASE_STATE: first 20 of the Grog clips are the production set.
    production_set_max = 20 if scene_slug == "MagicalRealmPlayground" else len(clips)
    entries = [annotate_clip(p, production_set_max, i) for i, p in enumerate(clips)]
    production_count = sum(1 for e in entries if e["role"] == "production")
    extras_count = sum(1 for e in entries if e["role"] == "extra")

    manifest.setdefault("scenes", {})[scene_slug] = {
        "clip_root": str(CLIP_ROOTS[scene_slug]).replace("\\", "/"),
        "total_clips": len(entries),
        "production_count": production_count,
        "extras_count": extras_count,
        "clips": entries,
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    audit_path = AUDIT_ROOT / f"catalog-{scene_slug.lower()}-{ts}.json"
    audit = {"scene_slug": scene_slug, "clip_root": str(CLIP_ROOTS[scene_slug]).replace("\\", "/"),
             "total_clips": len(entries), "production_count": production_count,
             "extras_count": extras_count, "timestamp": ts, "status": "OK"}
    audit_path.write_text(json.dumps(audit, indent=2))
    return audit


def plan_tier(tier: str, shot_id: str, scene_slug: str | None) -> dict:
    if not TIER_RE.match(tier):
        return {"status": "INVALID_TIER", "tier": tier,
                "expected_regex": TIER_RE.pattern}
    if not SHOT_ID_RE.match(shot_id):
        return {"status": "INVALID_SHOT_ID", "shot": shot_id,
                "expected_regex": SHOT_ID_RE.pattern}
    if scene_slug is not None and validate_slug(scene_slug):
        return {"status": "INVALID_SLUG", "scene_slug": scene_slug}
    cfg = load_tier_config().get("tiers", {}).get(tier)
    if not cfg:
        return {"status": "TIER_NOT_CONFIGURED", "tier": tier}
    if cfg.get("status") not in {"READY", "NODES_INSTALLED_WEIGHTS_DEFERRED"}:
        return {"status": "TIER_NOT_READY", "tier": tier,
                "tier_status": cfg.get("status"),
                "blocker": cfg.get("blocker")}
    return {"status": "PLAN",
            "tier": tier, "shot": shot_id, "scene": scene_slug,
            "wrapper_invocation": cfg.get("wrapper_invocation"),
            "approx_seconds_per_clip": cfg.get("approx_seconds_per_clip"),
            "vram_gb": cfg.get("vram_gb"),
            "best_for": cfg.get("best_for")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-tiers", action="store_true")
    ap.add_argument("--catalog")
    ap.add_argument("--plan-tier")
    ap.add_argument("--shot")
    ap.add_argument("--scene")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    if args.list_tiers:
        print(json.dumps(load_tier_config(), indent=2))
        return 0
    if args.catalog:
        result = catalog_scene(args.catalog, args.force)
        print(json.dumps(result, indent=2))
        code_for = {"OK": 0, "WILL_OVERWRITE_REFUSED": 5, "INVALID_SLUG": 6,
                    "UNKNOWN_SCENE_ROOT": 9, "CLIP_CATALOG_EMPTY": 8}
        return code_for.get(result.get("status", ""), 4)
    if args.plan_tier:
        if not args.shot:
            print(json.dumps({"status": "MISSING_SHOT"}, indent=2))
            return 6
        result = plan_tier(args.plan_tier, args.shot, args.scene)
        print(json.dumps(result, indent=2))
        code_for = {"PLAN": 0, "INVALID_TIER": 6, "INVALID_SHOT_ID": 6,
                    "INVALID_SLUG": 6, "TIER_NOT_CONFIGURED": 9,
                    "TIER_NOT_READY": 7}
        return code_for.get(result.get("status", ""), 4)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
