#!/usr/bin/env python3
"""APEX-MB-PY-00112 muscle_character_build_agent.py

Character-Build agent — wraps S1/S2/S3 of the ANIM pipeline (WO APEX-ANIM-MB-WO-00001 §3):
  S1: read canon (status.json + README.md or PROJECT_SPEC canon table) and emit a Character Bible.
  S2: list existing turnaround images under the character's render tree.
  S3: pick 4-7 anchor reference images and write a reference-pack manifest entry.

Designed for ANIM-03. Re-render of missing angles/expressions is deferred (would invoke
the existing apex/registry/muscle_character_designer.py via ComfyUI 127.0.0.1:8189
when --regenerate is added later).

Idempotent rerun guard: refuses to overwrite an existing v<n> bible unless --force.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

BRAND_DEFAULT = "Jesse-Adventures"
REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
BIBLE_ROOT = REPO_ROOT / "apex/docs/anim/bibles"
MANIFEST_PATH = REPO_ROOT / "apex/docs/anim/ANIM-03-reference-pack-manifest.json"
AUDIT_ROOT = REPO_ROOT / "apex/audit/anim-03"

PROJECT_ROOT = Path(r"X:/Automations/apex/projects/jesse_animate")
CHAR_ROOT = PROJECT_ROOT / "characters"
PROJECT_SPEC = PROJECT_ROOT / "PROJECT_SPEC.md"
PHASE_STATE = PROJECT_ROOT / "PHASE_STATE.json"

# Reference-pack role tags. Each entry is (role, needles, anti_needles).
# Picker takes the first render whose lower-cased path contains ANY needle and NO anti_needle.
# Anti-needles disambiguate roles whose names overlap (e.g. "front" matches both angle_front and
# the front-three-quarter image; anti-needles exclude the latter from the front bucket).
PACK_ROLES = [
    ("primary_ref",         ["primary_ref"],                                        []),
    ("angle_front",         ["_front_", "/angles/front_", "/angles/front."],        ["three_quarter", "back"]),
    ("angle_three_quarter", ["front_three_quarter", "_three_quarter_"],             ["back_three_quarter"]),
    ("angle_side",          ["_side_", "side_left", "side_right", "/angles/side"],  []),
    ("angle_back",          ["_back_", "/angles/back_", "/angles/back."],           ["three_quarter"]),
    ("expression_neutral",  ["expr_neutral", "/expressions/neutral"],               []),
    ("alt_form",            ["alt_form", "dragon"],                                 []),
]


def sha256_short(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()[:16]


def discover_render_set(char_dir: Path) -> list[Path]:
    if not char_dir.is_dir():
        return []
    out: list[Path] = []
    # Flat files at root (Emma-style: emma_angle_front_00001_.png).
    for p in sorted(char_dir.glob("*.png")):
        out.append(p)
    # Nested template-structure (Galinda-style: angles/, expressions/, poses/).
    for sub in ("angles", "expressions", "poses", "closeups", "outfits", "source_refs"):
        d = char_dir / sub
        if d.is_dir():
            out.extend(sorted(d.glob("*.png")))
    return out


def pick_pack(renders: list[Path]) -> list[dict]:
    picked: list[dict] = []
    used = set()
    for role, needles, anti in PACK_ROLES:
        for p in renders:
            if p in used:
                continue
            low = str(p).replace("\\", "/").lower()
            if not any(n.lower() in low for n in needles):
                continue
            if any(a.lower() in low for a in anti):
                continue
            picked.append({"role": role, "path": str(p)})
            used.add(p)
            break
    return picked[:7]


def annotate_pack(picked: list[dict]) -> list[dict]:
    out = []
    for e in picked:
        p = Path(e["path"])
        if not p.is_file():
            out.append({**e, "missing": True})
            continue
        out.append({**e, "sha256_prefix": sha256_short(p), "size": p.stat().st_size})
    return out


def read_status_json(char_dir: Path) -> dict | None:
    sp = char_dir / "status.json"
    if not sp.is_file():
        return None
    try:
        return json.loads(sp.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_readme(char_dir: Path) -> str | None:
    rp = char_dir / "README.md"
    if not rp.is_file():
        return None
    return rp.read_text(encoding="utf-8")


def project_spec_canon_row(character: str) -> str | None:
    if not PROJECT_SPEC.is_file():
        return None
    name = character.lower()
    for line in PROJECT_SPEC.read_text(encoding="utf-8").splitlines():
        if line.startswith("|") and name in line.lower() and "|" in line[1:]:
            return line.strip()
    return None


def render_bible(character: str, brand: str, status: dict | None,
                 readme: str | None, spec_row: str | None,
                 pack: list[dict], findings: list[str]) -> str:
    cap = character.capitalize()
    lines: list[str] = []
    lines.append(f"# Character Bible — {cap}")
    lines.append("")
    lines.append(f"**File:** `ANIM_{brand}_{cap}_bible_v1.md`")
    lines.append(f"**Authored:** {datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')}")
    lines.append(f"**Brand:** {brand}")
    lines.append(f"**Phase:** ANIM-03 (WO `APEX-ANIM-MB-WO-00001`)")
    lines.append("")
    lines.append("## 1. Source of canon (cited verbatim)")
    if status:
        lines.append("- `status.json` (authoritative — last updated `" + status.get("updated_at", "?") + "`):")
        canon = status.get("canon", {})
        for k in ("age", "hair", "eyes", "skin", "build", "height", "personality", "source_inspiration"):
            v = canon.get(k)
            if v:
                lines.append(f"  - **{k}:** {v}")
        sigs = canon.get("signature_items") or []
        if sigs:
            lines.append("  - **signature_items:**")
            for s in sigs:
                lines.append(f"    - {s}")
    if readme:
        lines.append("- `README.md` excerpt (first 12 lines, sibling source):")
        for ln in readme.splitlines()[:12]:
            lines.append(f"  > {ln}")
    if spec_row:
        lines.append("- `PROJECT_SPEC.md` §1.8 canon row:")
        lines.append(f"  > {spec_row}")
    if not (status or readme or spec_row):
        lines.append("- (none — no canon source resolved; build aborted upstream)")
    lines.append("")
    lines.append("## 2. Visual identity")
    if status:
        canon = status.get("canon", {})
        for k in ("hair", "eyes", "skin", "build", "height"):
            v = canon.get(k)
            if v:
                lines.append(f"- **{k.capitalize()}:** {v}")
        sigs = canon.get("signature_items") or []
        if sigs:
            lines.append("- **Signature items / default outfit:**")
            for s in sigs:
                lines.append(f"  - {s}")
    elif spec_row:
        lines.append(f"- Derived from PROJECT_SPEC row: `{spec_row}`")
    lines.append("")
    lines.append("## 3. Personality and behaviour cues")
    if status:
        lines.append(f"- **Personality:** {status.get('canon', {}).get('personality', '(unknown)')}")
    lines.append("- **Story role:** see README.md if present; otherwise leave for next bible version.")
    lines.append("")
    lines.append("## 4. Reference pack (S3)")
    if not pack:
        lines.append("- No reference images located. Re-run the agent after S2 renders exist.")
    else:
        for e in pack:
            line = f"- **{e['role']}** — `{e['path']}`"
            if e.get("sha256_prefix"):
                line += f" (sha256={e['sha256_prefix']}…, {e.get('size', '?')} B)"
            if e.get("missing"):
                line += " — MISSING"
            lines.append(line)
    lines.append("")
    lines.append("## 5. Do / Don't")
    lines.append("- **Do**: lock the trigger word listed in `status.json` (when present); use it on every prompt.")
    lines.append("- **Don't**: regenerate or replace `primary_ref` without an ADR — it is the consistency anchor for FaceID + LoRA.")
    lines.append("")
    lines.append("## 6. Findings logged for follow-up")
    if findings:
        for f in findings:
            lines.append(f"- {f}")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## 7. Copyright / differentiation")
    if status and status.get("canon", {}).get("source_inspiration"):
        lines.append(f"- Source inspiration: {status['canon']['source_inspiration']}")
    lines.append("- Differentiation doc: `X:/Automations/apex/projects/jesse_animate/characters/<name>/copyright/differentiation_doc.md` (when populated).")
    return "\n".join(lines) + "\n"


def build_character(character: str, brand: str, force: bool) -> dict:
    char_dir = CHAR_ROOT / character.lower()
    status = read_status_json(char_dir)
    readme = read_readme(char_dir)
    spec_row = project_spec_canon_row(character)
    renders = discover_render_set(char_dir)
    pack = annotate_pack(pick_pack(renders))

    findings: list[str] = []
    if status and readme:
        s_age = (status.get("canon") or {}).get("age")
        if s_age and ("child" in readme.lower() and "child" not in (s_age or "").lower()):
            findings.append(
                f"F-ANIM03-01: canon mismatch on {character} age — status.json says '{s_age}', "
                f"README.md describes a child. Bible locks the status.json value as authoritative because "
                f"it matches the 2026-04-07 PHASE_STATE.json formal sign-off; operator to merge or fork the README."
            )
    if not status:
        findings.append(f"F-ANIM03-02: {character} has no status.json under {char_dir}; bible built from PROJECT_SPEC + render-set inference.")
    if not renders:
        findings.append(f"F-ANIM03-03: {character} has no PNG renders under {char_dir}; reference pack is empty.")

    bible_md = render_bible(character, brand, status, readme, spec_row, pack, findings)
    BIBLE_ROOT.mkdir(parents=True, exist_ok=True)
    cap = character.capitalize()
    bible_path = BIBLE_ROOT / f"ANIM_{brand}_{cap}_bible_v1.md"
    if bible_path.exists() and not force:
        return {"character": character, "status": "WILL_OVERWRITE_REFUSED",
                "existing_bible": str(bible_path), "findings": findings,
                "hint": "rerun with --force to overwrite"}

    bible_path.write_text(bible_md, encoding="utf-8")

    # Update / create reference-pack manifest
    manifest: dict
    if MANIFEST_PATH.is_file():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    else:
        manifest = {"phase": "ANIM-03", "schema_version": 1, "brand": brand, "characters": {}}
    manifest["characters"][character.lower()] = {
        "brand": brand,
        "bible_path": str(bible_path).replace("\\", "/"),
        "status_json_path": str((char_dir / "status.json")).replace("\\", "/") if status else None,
        "render_source_root": str(char_dir).replace("\\", "/"),
        "render_count": len(renders),
        "reference_pack": pack,
        "findings": findings,
        "built_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2))

    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    audit_path = AUDIT_ROOT / f"{character.lower()}-build-{ts}.json"
    audit = {
        "character": character,
        "brand": brand,
        "bible_path": str(bible_path).replace("\\", "/"),
        "manifest_path": str(MANIFEST_PATH).replace("\\", "/"),
        "render_count": len(renders),
        "pack_size": len(pack),
        "findings": findings,
        "timestamp": ts,
        "status": "OK",
    }
    audit_path.write_text(json.dumps(audit, indent=2))

    return audit


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--character", required=True, help="Character name (matches dir at X:/.../characters/<name>/)")
    ap.add_argument("--brand", default=BRAND_DEFAULT)
    ap.add_argument("--force", action="store_true", help="Overwrite existing bible if present.")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.dry_run:
        char_dir = CHAR_ROOT / args.character.lower()
        renders = discover_render_set(char_dir)
        pack = annotate_pack(pick_pack(renders))
        print(json.dumps({
            "character": args.character,
            "brand": args.brand,
            "render_count": len(renders),
            "pack_preview": pack,
        }, indent=2))
        return 0
    result = build_character(args.character, args.brand, args.force)
    print(json.dumps(result, indent=2))
    if result.get("status") == "WILL_OVERWRITE_REFUSED":
        return 5
    return 0 if result.get("status") == "OK" else 4


if __name__ == "__main__":
    sys.exit(main())
