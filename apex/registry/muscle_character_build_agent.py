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
import re
import sys
from pathlib import Path

CHARACTER_NAME_RE = re.compile(r"^[a-z][a-z0-9_]{0,31}$")
PACK_MIN, PACK_MAX = 4, 7

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
# Roles ordered so legacy ANIM-03 needles win first (back-compat); kontext_sheets/ roles trail.
PACK_ROLES = [
    ("primary_ref",         ["primary_ref", "_candidate_seed"],                     []),
    ("angle_front",         ["_front_", "/angles/front_", "/angles/front."],        ["three_quarter", "back"]),
    ("angle_three_quarter", ["front_three_quarter", "_three_quarter_"],             ["back_three_quarter"]),
    ("angle_side",          ["_side_", "side_left", "side_right", "/angles/side"],  []),
    ("angle_back",          ["_back_", "/angles/back_", "/angles/back."],           ["three_quarter"]),
    ("expression_neutral",  ["expr_neutral", "/expressions/neutral"],               []),
    ("alt_form",            ["alt_form", "dragon"],                                 []),
    # ANIM-07 extension: kontext_sheets/-layout role buckets (grog, lirian).
    # New needles are kontext-specific so they cannot leak into legacy ANIM-03 picks.
    ("turnaround_seed",     ["/kontext_sheets/turnaround_seed"],                    []),
    ("expression_happy",    ["/kontext_sheets/expr_happy"],                         []),
    ("expression_angry",    ["/kontext_sheets/expr_angry"],                         []),
    ("expression_sad",      ["/kontext_sheets/expr_sad"],                           []),
    ("pose_action",         ["/kontext_sheets/pose_bow_drawn",
                             "/kontext_sheets/pose_running",
                             "/kontext_sheets/pose_climbing",
                             "/kontext_sheets/pose_lifting"],                       []),
    ("pose_idle",           ["/kontext_sheets/pose_listening",
                             "/kontext_sheets/pose_arms_crossed",
                             "/kontext_sheets/pose_sitting",
                             "/kontext_sheets/pose_sleeping",
                             "/kontext_sheets/pose_walking",
                             "/kontext_sheets/pose_gentle_hand"],                   []),
]


def sha256_of(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def discover_render_set(char_dir: Path) -> list[Path]:
    if not char_dir.is_dir():
        return []
    out: list[Path] = []
    # Flat files at root (Emma-style: emma_angle_front_00001_.png; also Lirian's
    # lirian_candidate_seed*.png and Grog's primary_ref.png).
    for p in sorted(char_dir.glob("*.png")):
        out.append(p)
    # Nested layouts:
    #   ANIM-03 (Galinda-style): angles/, expressions/, poses/, closeups/, outfits/, source_refs/.
    #   ANIM-07 extension (Grog/Lirian): kontext_sheets/ (turnaround_seed*, expr_*, pose_*);
    #     midjourney_refs/ holds raw refs — included for render_count provenance only because
    #     no PACK_ROLES needle targets midjourney UUID names, so they cannot be picked into
    #     the reference pack but do contribute to the manifest's audit-grade render_count.
    for sub in ("angles", "expressions", "poses", "closeups", "outfits", "source_refs",
                "kontext_sheets", "midjourney_refs"):
        d = char_dir / sub
        if d.is_dir():
            out.extend(sorted(d.glob("*.png")))
    return out


def pick_pack(renders: list[Path]) -> list[dict]:
    """Pick at most PACK_MAX role-tagged refs.

    Universal exclusion: `/midjourney_refs/` paths are never picked into the pack —
    they are raw operator references with non-canonical UUID filenames that can
    accidentally satisfy needle matches (e.g. "stand_side_<uuid>.png" hitting
    `_side_`). They still count toward render_count for provenance, but are not
    pack-eligible. To make a midjourney ref pack-eligible, the operator must
    promote it under a canonical name.
    """
    picked: list[dict] = []
    used = set()
    for role, needles, anti in PACK_ROLES:
        for p in renders:
            if p in used:
                continue
            low = str(p).replace("\\", "/").lower()
            if "/midjourney_refs/" in low:
                continue
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
        out.append({**e, "sha256": sha256_of(p), "size": p.stat().st_size})
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


CANON_SECTION_HEADER_RE = re.compile(r"^###\s+1\.8\s+Character Canon\b", re.IGNORECASE)
NEXT_SECTION_RE = re.compile(r"^#{1,3}\s+\S")


def project_spec_canon_row(character: str) -> str | None:
    """Find the §1.8 character-canon row whose first cell exactly equals the character name.

    Two-layer scope: (1) only scan lines that fall inside the §1.8 section (header to the
    next ## or ### heading); (2) inside that section, only return a row whose first cell
    exactly equals the character name. Fails closed on no-match OR ambiguous-match.
    """
    if not PROJECT_SPEC.is_file():
        return None
    target = character.strip().lower()
    matches: list[str] = []
    in_section = False
    for line in PROJECT_SPEC.read_text(encoding="utf-8").splitlines():
        if not in_section:
            if CANON_SECTION_HEADER_RE.match(line):
                in_section = True
            continue
        # Closing condition: next major section heading.
        if NEXT_SECTION_RE.match(line) and not CANON_SECTION_HEADER_RE.match(line):
            break
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells:
            continue
        if cells[0].lower() == target:
            matches.append(stripped)
    if len(matches) == 1:
        return matches[0]
    return None  # 0 = no canon row in §1.8; 2+ = ambiguous within §1.8, refuse to guess


def readme_line_matching(readme: str, needle: str) -> tuple[int, str] | None:
    """Return (1-based line, line text) of the first line containing needle (case-insensitive)."""
    n = needle.lower()
    for i, line in enumerate(readme.splitlines(), start=1):
        if n in line.lower():
            return i, line
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
            sha = e.get("sha256")
            if sha:
                line += f" (sha256={sha}, {e.get('size', '?')} B)"
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


def validate_character_arg(character: str) -> tuple[bool, dict | Path]:
    """Shared validation called by both build and dry-run paths.

    Returns (True, char_dir) on success or (False, error_dict) on rejection.
    """
    if not CHARACTER_NAME_RE.match(character):
        return False, {"character": character, "status": "INVALID_CHARACTER_NAME",
                       "expected_regex": CHARACTER_NAME_RE.pattern,
                       "hint": "lowercase a-z, 0-9, underscore; must start with a-z; max 32 chars"}
    char_dir = CHAR_ROOT / character
    try:
        resolved = char_dir.resolve(strict=False)
        root_resolved = CHAR_ROOT.resolve(strict=False)
        if Path(os.path.commonpath([str(resolved), str(root_resolved)])) != root_resolved:
            return False, {"character": character, "status": "PATH_ESCAPE_REJECTED",
                           "resolved": str(resolved), "char_root": str(root_resolved)}
    except ValueError:
        return False, {"character": character, "status": "PATH_ESCAPE_REJECTED",
                       "char_root": str(CHAR_ROOT)}
    return True, char_dir


def build_character(character: str, brand: str, force: bool) -> dict:
    ok, ret = validate_character_arg(character)
    if not ok:
        return ret  # type: ignore[return-value]
    char_dir = ret  # type: ignore[assignment]

    # F-4 r2 fix: check overwrite guard BEFORE volatile render discovery and hashing so
    # rerunning an already-built bible always returns WILL_OVERWRITE_REFUSED (exit 5),
    # independent of whether source renders are still present or the pack still meets PACK_MIN.
    cap = character.capitalize()
    bible_path = BIBLE_ROOT / f"ANIM_{brand}_{cap}_bible_v1.md"
    if bible_path.exists() and not force:
        return {"character": character, "status": "WILL_OVERWRITE_REFUSED",
                "existing_bible": str(bible_path),
                "hint": "rerun with --force to overwrite"}

    status = read_status_json(char_dir)
    readme = read_readme(char_dir)
    spec_row = project_spec_canon_row(character)

    # F-3 r2 fix: fail closed if no canon source is resolved at all. Render-set
    # inference alone is not enough to issue a bible.
    if not (status or spec_row):
        return {"character": character, "status": "NO_CANON_SOURCE",
                "char_dir": str(char_dir),
                "checked": ["status.json", "PROJECT_SPEC.md §1.8 first-cell match"],
                "hint": "populate <char>/status.json or add a §1.8 row before retrying"}

    renders = discover_render_set(char_dir)
    pack = annotate_pack(pick_pack(renders))

    findings: list[str] = []
    # F-4 fix: when flagging the README-vs-status canon mismatch, quote the exact README line
    # that triggered the flag (with 1-based line number) so the claim is anchored.
    if status and readme:
        s_age = (status.get("canon") or {}).get("age")
        match = readme_line_matching(readme, "child")
        if s_age and match and "child" not in (s_age or "").lower():
            line_no, line_txt = match
            findings.append(
                f"F-ANIM03-01: canon mismatch on {character} age — status.json says '{s_age}'; "
                f"README.md line {line_no} reads '{line_txt.strip()}'. Bible locks the status.json "
                f"value as authoritative because it matches the 2026-04-07 PHASE_STATE.json formal "
                f"sign-off and the 15/15 production-ready renders; operator to merge or fork the README."
            )
    if not status:
        findings.append(f"F-ANIM03-02: {character} has no status.json under {char_dir}; bible built from PROJECT_SPEC + render-set inference.")
    if not renders:
        findings.append(f"F-ANIM03-03: {character} has no PNG renders under {char_dir}; reference pack is empty.")
    # F-6 fix: enforce pack-size pass criterion BEFORE writing deliverables.
    if len(pack) < PACK_MIN:
        return {"character": character, "status": "PACK_TOO_SMALL",
                "pack_size": len(pack), "required_min": PACK_MIN,
                "hint": "Re-render missing angles or add status.json/PROJECT_SPEC canon to widen role coverage."}

    bible_md = render_bible(character, brand, status, readme, spec_row, pack, findings)
    BIBLE_ROOT.mkdir(parents=True, exist_ok=True)
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
        ok, ret = validate_character_arg(args.character)
        if not ok:
            print(json.dumps(ret, indent=2))
            return 6
        char_dir = ret  # type: ignore[assignment]
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
    code_for = {
        "OK": 0,
        "WILL_OVERWRITE_REFUSED": 5,
        "INVALID_CHARACTER_NAME": 6,
        "PATH_ESCAPE_REJECTED": 6,
        "PACK_TOO_SMALL": 7,
        "NO_CANON_SOURCE": 8,
    }
    return code_for.get(result.get("status", ""), 4)


if __name__ == "__main__":
    sys.exit(main())
