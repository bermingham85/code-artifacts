"""ANIM-14 negative-path evidence probe.

Imports resolve_character_markers() and runs constructed inputs to demonstrate
each new error class fires as designed. ANIM-14 r2 F-4 fix: each probe is now
recorded with harness name, input mutation, expected status, actual status,
and a UTC timestamp so the evidence is auditable independently of the agent.
"""
from __future__ import annotations
import datetime
import json
import sys
from pathlib import Path

# Make repo root importable
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "apex" / "registry"))

from muscle_shot_storyboard_agent import resolve_character_markers  # noqa: E402

GROG_SRC = "X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/shot_list.json"
GROG_SHA = "6414235bd985e2d90c4e5875846739a276da0f2c7388abff4a99377332f6a428"
GROG_MARKERS = (
    "massive ogre with warm beige skin and rugged texture, "
    "smooth clean-shaven face, warm brown eyes, teal roughspun vest, "
    "fraying rope belt, patched fringe brown trousers"
)
YOUNG_GROG_MARKERS = (
    "tiny toddler ogre with warm beige skin, smooth round clean-shaven cheeks, "
    "wide innocent warm brown eyes, stubby chubby fingers, "
    "already twice the height of a full-grown adult"
)
HARNESS = "apex/audit/anim-14/negative_paths_probe.py"


def _now_utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def _probe(name: str, cfg: dict, ref_pack: dict, expected_status: str,
           mutation: str) -> dict:
    """Run resolve_character_markers() and record full auditable context."""
    result = resolve_character_markers(name, cfg, ref_pack)
    return {
        "probe_id": name,
        "harness": HARNESS,
        "function_under_test": "resolve_character_markers(project_slug, cfg, ref_pack)",
        "mutation": mutation,
        "expected_status": expected_status,
        "actual_status": result.get("status"),
        "pass": result.get("status") == expected_status,
        "result": result,
        "timestamp_utc": _now_utc(),
    }


# 1. CHARACTER_MARKERS_NOT_FOUND
r1 = _probe(
    "nf_probe",
    {"character": "grog"},
    {"characters": {"grog": {"bible_path": "x.md"}}},
    expected_status="CHARACTER_MARKERS_NOT_FOUND",
    mutation="cfg = {character: grog} only; manifest['characters']['grog'] has no marker fields",
)

# 2. CHARACTER_MARKERS_MANIFEST_PARTIAL — when project is absent
r2 = _probe(
    "pm_probe",
    {"character": "grog"},
    {"characters": {"grog": {
        "character_markers": GROG_MARKERS,
        "character_markers_provenance_source_path": GROG_SRC,
        "character_markers_provenance_field": "grog_identifiers",
        # missing sha256 -> 3-of-4
    }}},
    expected_status="CHARACTER_MARKERS_MANIFEST_PARTIAL",
    mutation="manifest['characters']['grog'] has 3-of-4 marker fields (sha256 absent); project carries no marker fields, so fallback is required",
)

# 3. CHARACTER_MARKERS_VALUE_MISMATCH from ANIM-03 path
r3 = _probe(
    "vm_probe",
    {"character": "grog"},
    {"characters": {"grog": {
        "character_markers": "fabricated wrong text — not from source",
        "character_markers_provenance_source_path": GROG_SRC,
        "character_markers_provenance_field": "grog_identifiers",
        "character_markers_provenance_sha256": GROG_SHA,
    }}},
    expected_status="CHARACTER_MARKERS_VALUE_MISMATCH",
    mutation="manifest carries provenance triple verifiable against source (sha matches), but character_markers text differs from the source field value",
)

# 4. CHARACTER_MARKERS_SOURCE_CONFLICT
r4 = _probe(
    "conf_probe",
    {
        "character": "grog",
        "character_markers": GROG_MARKERS,
        "character_markers_provenance_source_path": GROG_SRC,
        "character_markers_provenance_field": "grog_identifiers",
        "character_markers_provenance_sha256": GROG_SHA,
    },
    {"characters": {"grog": {
        "character_markers": YOUNG_GROG_MARKERS,
        "character_markers_provenance_source_path": GROG_SRC,
        "character_markers_provenance_field": "young_grog_identifiers",
        "character_markers_provenance_sha256": GROG_SHA,
    }}},
    expected_status="CHARACTER_MARKERS_SOURCE_CONFLICT",
    mutation="project + manifest both verifiable individually (against different fields in the same source file); recorded character_markers strings differ",
)

# 5. OK via manifest-only
r5 = _probe(
    "ok_probe",
    {"character": "grog"},
    {"characters": {"grog": {
        "character_markers": GROG_MARKERS,
        "character_markers_provenance_source_path": GROG_SRC,
        "character_markers_provenance_field": "grog_identifiers",
        "character_markers_provenance_sha256": GROG_SHA,
    }}},
    expected_status="OK",
    mutation="manifest carries full verifiable marker block; project carries no marker fields",
)

# 6. r3 F-6 fix (supersedes r1 F-3): manifest_partial is ALWAYS fatal per
#    SPEC-ANIM-14 — "the agent re-validates this at runtime" is unconditional.
#    A project with its own complete marker block still cannot run while the
#    manifest's marker block for the bound character is in registry-inconsistent
#    partial state. This forces the registry fix.
r6 = _probe(
    "proj_full_manifest_partial_probe",
    {
        "character": "grog",
        "character_markers": GROG_MARKERS,
        "character_markers_provenance_source_path": GROG_SRC,
        "character_markers_provenance_field": "grog_identifiers",
        "character_markers_provenance_sha256": GROG_SHA,
    },
    {"characters": {"grog": {
        "character_markers": GROG_MARKERS,
        "character_markers_provenance_source_path": GROG_SRC,
        "character_markers_provenance_field": "grog_identifiers",
        # missing sha256 -> partial manifest
    }}},
    expected_status="CHARACTER_MARKERS_MANIFEST_PARTIAL",
    mutation="project carries full verifiable marker block; manifest has 3-of-4 (registry inconsistency); r3 F-6 surfaces MANIFEST_PARTIAL to force registry fix",
)

# 7. F-5 fix evidence: source file top-level non-dict JSON
#    Build a temp file containing a JSON array to exercise the
#    isinstance(src_data, dict) guard in _verify_markers_against_source().
_tmp_dir = REPO / "apex" / "audit" / "anim-14" / "tmp"
_tmp_dir.mkdir(parents=True, exist_ok=True)
_tmp_src = _tmp_dir / "non_object_source.json"
_tmp_src.write_text('["this", "is", "an", "array"]', encoding="utf-8")
import hashlib  # noqa: E402
_tmp_sha = hashlib.sha256(_tmp_src.read_bytes()).hexdigest()
r7 = _probe(
    "non_object_source_probe",
    {"character": "grog"},
    {"characters": {"grog": {
        "character_markers": "anything",
        "character_markers_provenance_source_path": str(_tmp_src).replace("\\", "/"),
        "character_markers_provenance_field": "anything",
        "character_markers_provenance_sha256": _tmp_sha,
    }}},
    expected_status="CHARACTER_MARKERS_SOURCE_UNPARSEABLE",
    mutation=(
        f"temp source {_tmp_src.name} contains a JSON array (top-level non-object); "
        "sha256 + path verifiable; isinstance(src_data, dict) guard returns "
        "CHARACTER_MARKERS_SOURCE_UNPARSEABLE rather than crashing on .get()"
    ),
)

out = {
    "phase": "ANIM-14",
    "harness": HARNESS,
    "doctrine_evidence_class": "O9 (auditable probe trail)",
    "probes": [r1, r2, r3, r4, r5, r6, r7],
    "summary": {
        "total_probes": 7,
        "pass": sum(1 for r in [r1, r2, r3, r4, r5, r6, r7] if r["pass"]),
        "fail": sum(1 for r in [r1, r2, r3, r4, r5, r6, r7] if not r["pass"]),
    },
    "built_at": _now_utc(),
}
print(json.dumps(out, indent=2))
