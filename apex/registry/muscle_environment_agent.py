#!/usr/bin/env python3
"""APEX-MB-PY-00113 muscle_environment_agent.py

Environment/Imagery agent — wraps S4 of the ANIM pipeline (WO §3.2):
  - Reads brand tokens (style_anchor + prompt_rules) from shot_list.json.
  - Reads a scene descriptor from ANIM-04-scene-descriptors.json by slug.
  - Catalogs existing scene-reference PNGs under
    X:/.../characters/_source_refs/scenes/ matching the descriptor's
    source_path_substr.
  - Emits a sectioned scene-bible markdown plus a scene-pack manifest entry,
    each asset annotated with full sha256 + size.

Idempotency: rerun without --force returns WILL_OVERWRITE_REFUSED exit 5.
Path safety: slug regex-bounded; resolved-path checked against output roots.
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
# F-2 fix: brand restricted to filename-safe pattern. F-1 fix: code-level immutable allowlist.
BRAND_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,31}$")
CODE_LEVEL_BRAND_ALLOWLIST = frozenset({"Jesse-Adventures"})
SUBSTR_MIN_LEN = 5
PACK_MAX = 7
PACK_MIN = 1  # one scene-ref is sufficient for a S4 catalog deliverable

REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
SCENE_BIBLE_ROOT = REPO_ROOT / "apex/docs/anim/scenes"
MANIFEST_PATH = REPO_ROOT / "apex/docs/anim/ANIM-04-scene-pack-manifest.json"
DESCRIPTORS_PATH = REPO_ROOT / "apex/docs/anim/ANIM-04-scene-descriptors.json"
AUDIT_ROOT = REPO_ROOT / "apex/audit/anim-04"

SCENES_REF_ROOT = Path(r"X:/Automations/apex/projects/jesse_animate/characters/_source_refs/scenes")
SHOT_LIST_JSON = Path(r"X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json")


def sha256_of(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load_brand_tokens() -> dict:
    if not SHOT_LIST_JSON.is_file():
        return {"style_anchor": None, "prompt_rules": None,
                "source": str(SHOT_LIST_JSON), "missing": True}
    data = json.loads(SHOT_LIST_JSON.read_text(encoding="utf-8"))
    return {"style_anchor": data.get("style_anchor"),
            "prompt_rules": data.get("prompt_rules"),
            "source": str(SHOT_LIST_JSON).replace("\\", "/"), "missing": False}


def load_descriptors() -> dict:
    if not DESCRIPTORS_PATH.is_file():
        return {"schema_version": 1, "brand_allowlist": [], "scenes": {}}
    return json.loads(DESCRIPTORS_PATH.read_text(encoding="utf-8"))


_WORD_TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


def discover_scene_refs(substr: str) -> list[Path]:
    """Catalog PNGs under SCENES_REF_ROOT whose filename contains the substr as a
    word-boundary token sequence (not a free substring).

    F-3 fix: substr is treated as a sequence of `_`-separated tokens that must appear
    contiguously and at token-boundaries in the filename (preceded by start-of-name OR `_`,
    followed by `_` OR `.`). This blocks both single-char "a" smuggling AND mid-token
    overlap (e.g. "magical" alone does NOT match "magicalreal" if such a file existed).
    Substr must be a valid lowercase token sequence (^[a-z0-9][a-z0-9_]*$) and at least
    SUBSTR_MIN_LEN chars.
    """
    if not SCENES_REF_ROOT.is_dir():
        return []
    s = (substr or "").lower().strip()
    if len(s) < SUBSTR_MIN_LEN or not _WORD_TOKEN_RE.match(s):
        return []
    # Build a regex with token-boundary anchors. (?:^|_) before, (?:_|\.) after.
    pat = re.compile(r"(?:^|_)" + re.escape(s) + r"(?:_|\.)")
    return sorted([p for p in SCENES_REF_ROOT.glob("*.png") if pat.search(p.name.lower())])


def validate_slug(slug: str) -> dict | None:
    if not SLUG_RE.match(slug):
        return {"slug": slug, "status": "INVALID_SLUG",
                "expected_regex": SLUG_RE.pattern,
                "hint": "PascalCase letters and digits, must start with A-Z, max 32 chars"}
    return None


def render_scene_bible(slug: str, descriptor: dict, brand_tokens: dict, assets: list[dict], findings: list[str]) -> str:
    brand = descriptor["brand"]
    lines: list[str] = []
    lines.append(f"# Scene Bible — {slug}")
    lines.append("")
    lines.append(f"**File:** `ANIM_{brand}_{slug}_bg_v1.md`")
    lines.append(f"**Authored:** {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"**Brand:** {brand}")
    lines.append(f"**Phase:** ANIM-04 (WO `APEX-ANIM-MB-WO-00001`)")
    lines.append("")
    lines.append("## 1. Brand tokens (verbatim from shot_list.json)")
    if brand_tokens.get("style_anchor"):
        lines.append(f"- **style_anchor** (`{brand_tokens['source']}:style_anchor`):")
        lines.append(f"  > {brand_tokens['style_anchor']}")
    if brand_tokens.get("prompt_rules"):
        lines.append(f"- **prompt_rules** (`{brand_tokens['source']}:prompt_rules`):")
        lines.append(f"  > {brand_tokens['prompt_rules']}")
    if brand_tokens.get("missing"):
        lines.append("- WARNING: brand-token source file not found at " + brand_tokens["source"])
    lines.append("")
    lines.append("## 2. Scene descriptor")
    lines.append(f"- **slug:** `{slug}`")
    lines.append(f"- **prompt:** {descriptor['prompt']}")
    if descriptor.get("source_path_substr"):
        lines.append(f"- **source_path_substr:** `{descriptor['source_path_substr']}` (catalog filter)")
    if descriptor.get("notes"):
        lines.append(f"- **notes:** {descriptor['notes']}")
    lines.append("")
    lines.append("## 3. Asset catalog (existing scene refs)")
    if not assets:
        lines.append("- No matching assets located. Re-run after rendering or adjust `source_path_substr`.")
    else:
        for a in assets:
            line = f"- `{a['path']}`"
            if a.get("sha256"):
                line += f" (sha256={a['sha256']}, {a.get('size', '?')} B)"
            lines.append(line)
    lines.append("")
    lines.append("## 4. Do / Don't")
    lines.append("- **Do**: append the style_anchor once at prompt tail (per prompt_rules).")
    lines.append("- **Don't**: include character identity in scene prompts — character keys live in the character bibles (ANIM-03).")
    lines.append("- **Don't**: re-generate from this catalog without an ADR; existing assets are the anchor set for ANIM-05.")
    lines.append("")
    lines.append("## 5. Findings logged for follow-up")
    if findings:
        for f in findings:
            lines.append(f"- {f}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## 6. Copyright / differentiation")
    lines.append("- Source refs were Midjourney generations licensed under operator's MJ account; output is original art under that licence.")
    lines.append("- Differentiation: Pixar-style anchor and original prompt prevent likeness to any single source franchise.")
    return "\n".join(lines) + "\n"


def build_scene(slug: str, force: bool) -> dict:
    bad = validate_slug(slug)
    if bad:
        return bad

    descriptors = load_descriptors()
    scenes = descriptors.get("scenes", {})
    descriptor = scenes.get(slug)
    if not descriptor:
        return {"slug": slug, "status": "DESCRIPTOR_NOT_FOUND",
                "descriptors_path": str(DESCRIPTORS_PATH),
                "available_slugs": list(scenes.keys())}

    brand = descriptor.get("brand")
    # F-2 fix: brand must match filename-safe regex.
    if not isinstance(brand, str) or not BRAND_RE.match(brand):
        return {"slug": slug, "status": "INVALID_BRAND",
                "brand": brand, "expected_regex": BRAND_RE.pattern}
    # F-1 fix: fail-closed via code-level allowlist; the descriptors-JSON allowlist is
    # an additional optional gate but cannot loosen the code-level set.
    if brand not in CODE_LEVEL_BRAND_ALLOWLIST:
        return {"slug": slug, "status": "BRAND_NOT_ALLOWED",
                "brand": brand,
                "code_level_allowlist": sorted(CODE_LEVEL_BRAND_ALLOWLIST)}
    descriptor_allowlist = descriptors.get("brand_allowlist") or []
    if descriptor_allowlist and brand not in descriptor_allowlist:
        return {"slug": slug, "status": "BRAND_NOT_ALLOWED",
                "brand": brand, "descriptor_allowlist": descriptor_allowlist}

    SCENE_BIBLE_ROOT.mkdir(parents=True, exist_ok=True)
    bible_path = SCENE_BIBLE_ROOT / f"ANIM_{brand}_{slug}_bg_v1.md"
    # F-2 follow-up: even after regex validation, verify the resolved path stays inside
    # the bible root (defense in depth against edge cases the regex might miss).
    try:
        resolved = bible_path.resolve(strict=False)
        root_resolved = SCENE_BIBLE_ROOT.resolve(strict=False)
        if Path(os.path.commonpath([str(resolved), str(root_resolved)])) != root_resolved:
            return {"slug": slug, "status": "PATH_ESCAPE_REJECTED",
                    "resolved": str(resolved)}
    except ValueError:
        return {"slug": slug, "status": "PATH_ESCAPE_REJECTED"}
    if bible_path.exists() and not force:
        return {"slug": slug, "status": "WILL_OVERWRITE_REFUSED",
                "existing_bible": str(bible_path),
                "hint": "rerun with --force to overwrite"}

    brand_tokens = load_brand_tokens()
    # F-1 r2 fix: fail closed when shot_list.json is missing or either required brand-token
    # field is null/empty — bibles MUST cite both verbatim per the WO §2.S4 "style-locked" rule.
    if (brand_tokens.get("missing")
            or not isinstance(brand_tokens.get("style_anchor"), str)
            or not brand_tokens["style_anchor"].strip()
            or not isinstance(brand_tokens.get("prompt_rules"), str)
            or not brand_tokens["prompt_rules"].strip()):
        return {"slug": slug, "status": "BRAND_TOKENS_MISSING",
                "source": brand_tokens.get("source"),
                "style_anchor": brand_tokens.get("style_anchor"),
                "prompt_rules_present": bool(brand_tokens.get("prompt_rules"))}
    substr = descriptor.get("source_path_substr") or slug.lower()
    # F-3 fix: enforce minimum prefix length AND a valid lowercase token-sequence so
    # path fragments / special chars can never reach the catalog query.
    if (not isinstance(substr, str)
            or len(substr.strip()) < SUBSTR_MIN_LEN
            or not _WORD_TOKEN_RE.match(substr.strip().lower())):
        return {"slug": slug, "status": "SUBSTR_INVALID",
                "source_path_substr": substr,
                "min_len": SUBSTR_MIN_LEN,
                "expected_regex": _WORD_TOKEN_RE.pattern}
    raw_assets = discover_scene_refs(substr)[:PACK_MAX]
    assets: list[dict] = []
    for p in raw_assets:
        assets.append({"path": str(p).replace("\\", "/"),
                       "sha256": sha256_of(p),
                       "size": p.stat().st_size})
    findings: list[str] = []
    if brand_tokens.get("missing"):
        findings.append(f"F-ANIM04-01: brand-token source {brand_tokens['source']} missing; bible records null style_anchor + prompt_rules.")
    if len(assets) < PACK_MIN:
        return {"slug": slug, "status": "ASSET_CATALOG_EMPTY",
                "scenes_ref_root": str(SCENES_REF_ROOT),
                "matched_substr": substr,
                "hint": "lower source_path_substr or re-render scene refs first"}

    bible_md = render_scene_bible(slug, descriptor, brand_tokens, assets, findings)
    bible_path.write_text(bible_md, encoding="utf-8")

    manifest: dict
    if MANIFEST_PATH.is_file():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        manifest = {"phase": "ANIM-04", "schema_version": 1, "scenes": {}}
    manifest["scenes"][slug] = {
        "brand": brand,
        "bible_path": str(bible_path).replace("\\", "/"),
        "descriptor": descriptor,
        "brand_tokens": brand_tokens,
        "asset_count": len(assets),
        "assets": assets,
        "findings": findings,
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    audit_path = AUDIT_ROOT / f"{slug.lower()}-build-{ts}.json"
    audit = {"slug": slug, "brand": brand,
             "bible_path": str(bible_path).replace("\\", "/"),
             "manifest_path": str(MANIFEST_PATH).replace("\\", "/"),
             "asset_count": len(assets),
             "findings": findings, "timestamp": ts, "status": "OK"}
    audit_path.write_text(json.dumps(audit, indent=2))
    return audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.dry_run:
        bad = validate_slug(args.slug)
        if bad:
            print(json.dumps(bad, indent=2))
            return 6
        descriptors = load_descriptors()
        d = descriptors.get("scenes", {}).get(args.slug)
        if not d:
            print(json.dumps({"slug": args.slug, "status": "DESCRIPTOR_NOT_FOUND"}, indent=2))
            return 9
        substr = d.get("source_path_substr", args.slug.lower())
        assets = discover_scene_refs(substr)[:PACK_MAX]
        print(json.dumps({"slug": args.slug, "brand": d.get("brand"),
                          "matched_count": len(assets),
                          "preview": [str(p).replace("\\", "/") for p in assets[:3]]}, indent=2))
        return 0
    result = build_scene(args.slug, args.force)
    print(json.dumps(result, indent=2))
    code_for = {"OK": 0,
                "WILL_OVERWRITE_REFUSED": 5,
                "INVALID_SLUG": 6,
                "INVALID_BRAND": 6,
                "PATH_ESCAPE_REJECTED": 6,
                "BRAND_NOT_ALLOWED": 7,
                "ASSET_CATALOG_EMPTY": 8,
                "SUBSTR_INVALID": 8,
                "DESCRIPTOR_NOT_FOUND": 9,
                "BRAND_TOKENS_MISSING": 10}
    return code_for.get(result.get("status", ""), 4)


if __name__ == "__main__":
    sys.exit(main())
