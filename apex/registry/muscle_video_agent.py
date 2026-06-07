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

# Per-scene clip-source bindings: clip root + shot list + character + brand.
SCENE_BINDINGS = {
    "MagicalRealmPlayground": {
        "clip_root": Path(r"X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/clips"),
        "shot_list_json": Path(r"X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json"),
        "character": "grog",
        "brand": "Jesse-Adventures",
        "source": "Wan2.2 i2v two-stage MoE (per PHASE_STATE session_2026_04_01_mv)",
    },
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
    """Discover MP4 clips under the scene's clip root. F-4 r1 fix: reject symlinks
    outright (lstat().is_symlink()) so the resolved-target window between check and
    hash cannot be exploited; non-symlink files are hashed on the regular path."""
    binding = SCENE_BINDINGS.get(scene_slug)
    if not binding:
        return []
    root = binding["clip_root"]
    if not root.is_dir():
        return []
    try:
        root_resolved = root.resolve(strict=True)
    except (FileNotFoundError, OSError):
        return []
    out: list[Path] = []
    for p in sorted(root.glob("*.mp4")):
        try:
            if p.is_symlink():
                continue  # F-4 r1: refuse symlinks outright; no TOCTOU window
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


def load_shot_metadata(scene_slug: str) -> dict:
    """Read shot_list.json and return {id_str: {start, end, duration}} per shot."""
    binding = SCENE_BINDINGS.get(scene_slug)
    if not binding:
        return {}
    sp = binding["shot_list_json"]
    if not sp.is_file():
        return {}
    data = json.loads(sp.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for s in data.get("shots", []):
        sid = str(s.get("id"))
        start = s.get("start")
        end = s.get("end")
        if start is not None and end is not None:
            out[sid] = {"start": start, "end": end, "duration_seconds": round(end - start, 3)}
    return out


_CLIP_INDEX_RE = re.compile(r"clip_(\d+)\.mp4$", re.IGNORECASE)


def annotate_clip(p: Path, production_set_max: int, index: int,
                  scene_binding: dict, shot_meta: dict,
                  root_resolved: Path) -> dict | None:
    """Hash and stat the clip via a single open file handle (bytes-to-fd binding) and
    re-validate the path's containment AFTER the read so a swap mid-hash is detected.

    F-6 r2 + F-1 r4 TOCTOU fixes:
      1. lstat to refuse pre-resolve symlink.
      2. Resolve target + commonpath check (pre-hash).
      3. os.open + fstat for size (handle is bound to one inode for the lifetime of read).
      4. Read+hash from the open fd (no path re-traversal during read).
      5. After close: re-resolve + re-commonpath. If the path moved or its target no
         longer resolves under root_resolved, drop the entry (recorded bytes are then
         not asserted to be under the trusted root).

    On Windows, Python lacks O_NOFOLLOW / openat for fully atomic close, but the
    handle-bound read + pre-and-post resolve checks shrink the TOCTOU window to the
    open() call only, with the post-check detecting swaps.
    """
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
        # Post-read re-validation: target path and its containment must still hold.
        target_post = p.resolve(strict=True)
        if target_post != target_pre:
            return None
        if Path(os.path.commonpath([str(target_post), str(root_resolved)])) != root_resolved:
            return None
        target = target_post
    except (FileNotFoundError, OSError, ValueError):
        return None
    name = p.name
    m = _CLIP_INDEX_RE.search(name)
    shot_id = None
    duration = None
    if m:
        clip_num = int(m.group(1))
        shot_id = str(clip_num)
        if shot_id in shot_meta:
            duration = shot_meta[shot_id]["duration_seconds"]
    return {
        "path": str(p).replace("\\", "/"),
        "resolved_path": str(target).replace("\\", "/"),
        "sha256": digest,
        "size": size,
        "role": "production" if index < production_set_max else "extra",
        "index": index,
        "shot_id": shot_id,
        "character": scene_binding.get("character"),
        "scene_slug": scene_binding.get("scene_slug_self"),
        "brand": scene_binding.get("brand"),
        "source": scene_binding.get("source"),
        "duration_seconds": duration,
        "duration_source": (
            f"{scene_binding['shot_list_json'].name}:shots[id={shot_id}]"
            if duration is not None else "unmapped"
        ),
    }


def catalog_scene(scene_slug: str, force: bool) -> dict:
    bad = validate_slug(scene_slug)
    if bad:
        return bad
    if scene_slug not in SCENE_BINDINGS:
        return {"slug": scene_slug, "status": "UNKNOWN_SCENE_ROOT",
                "known_scenes": sorted(SCENE_BINDINGS.keys())}

    manifest = (json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
                if MANIFEST_PATH.is_file()
                else {"phase": "ANIM-05", "schema_version": 2, "scenes": {}})
    if scene_slug in manifest.get("scenes", {}) and not force:
        return {"slug": scene_slug, "status": "WILL_OVERWRITE_REFUSED",
                "existing_entry": str(SCENE_BINDINGS[scene_slug]["clip_root"])}

    clips = discover_clips(scene_slug)
    if not clips:
        return {"slug": scene_slug, "status": "CLIP_CATALOG_EMPTY",
                "clip_root": str(SCENE_BINDINGS[scene_slug]["clip_root"])}

    binding = dict(SCENE_BINDINGS[scene_slug])
    binding["scene_slug_self"] = scene_slug
    shot_meta = load_shot_metadata(scene_slug)
    # PHASE_STATE: first 20 of the Grog clips are the production set.
    production_set_max = 20 if scene_slug == "MagicalRealmPlayground" else len(clips)
    try:
        root_resolved = binding["clip_root"].resolve(strict=True)
    except (FileNotFoundError, OSError):
        return {"slug": scene_slug, "status": "CLIP_CATALOG_EMPTY",
                "clip_root": str(binding["clip_root"])}
    raw_entries = [annotate_clip(p, production_set_max, i, binding, shot_meta, root_resolved)
                   for i, p in enumerate(clips)]
    entries = [e for e in raw_entries if e is not None]
    rejected = len(raw_entries) - len(entries)
    production_count = sum(1 for e in entries if e["role"] == "production")
    extras_count = sum(1 for e in entries if e["role"] == "extra")

    manifest.setdefault("scenes", {})[scene_slug] = {
        "clip_root": str(binding["clip_root"]).replace("\\", "/"),
        "shot_list_json": str(binding["shot_list_json"]).replace("\\", "/"),
        "character": binding["character"],
        "brand": binding["brand"],
        "source": binding["source"],
        "total_clips": len(entries),
        "production_count": production_count,
        "extras_count": extras_count,
        "rejected_at_hash": rejected,
        "mapped_durations": sum(1 for e in entries if e["duration_seconds"] is not None),
        "clips": entries,
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    audit_path = AUDIT_ROOT / f"catalog-{scene_slug.lower()}-{ts}.json"
    audit = {"scene_slug": scene_slug, "clip_root": str(binding["clip_root"]).replace("\\", "/"),
             "total_clips": len(entries), "production_count": production_count,
             "extras_count": extras_count, "mapped_durations": manifest["scenes"][scene_slug]["mapped_durations"],
             "timestamp": ts, "status": "OK"}
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
    # F-1 r1 fix: only READY tiers can return PLAN. NODES_INSTALLED_WEIGHTS_DEFERRED
    # is treated as not-ready since the render would fail at weight load.
    if cfg.get("status") != "READY":
        return {"status": "TIER_NOT_READY", "tier": tier,
                "tier_status": cfg.get("status"),
                "blocker": cfg.get("blocker"),
                "hint": cfg.get("weights_install_command")}
    # F-2 r1 fix: refuse PLAN if wrapper_invocation is missing/empty for a runnable tier.
    wrapper = cfg.get("wrapper_invocation")
    if not isinstance(wrapper, str) or not wrapper.strip():
        return {"status": "TIER_NOT_CONFIGURED", "tier": tier,
                "missing": "wrapper_invocation"}
    return {"status": "PLAN",
            "tier": tier, "shot": shot_id, "scene": scene_slug,
            "wrapper_invocation": wrapper,
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
