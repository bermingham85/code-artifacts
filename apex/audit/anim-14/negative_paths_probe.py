"""ANIM-14 negative-path evidence probe.

Imports resolve_character_markers() and runs four constructed inputs to
demonstrate the new error classes fire as designed. Output is captured to
apex/docs/anim/ANIM-14-evidence.json by the caller.
"""
from __future__ import annotations
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

# 1. CHARACTER_MARKERS_NOT_FOUND — project+manifest both have nothing
cfg_nf = {"character": "grog"}
manifest_nf = {"characters": {"grog": {"bible_path": "x.md"}}}
r1 = resolve_character_markers("nf_probe", cfg_nf, manifest_nf)

# 2. CHARACTER_MARKERS_MANIFEST_PARTIAL — manifest has 3/4 marker fields
cfg_pm = {"character": "grog"}
manifest_pm = {"characters": {"grog": {
    "character_markers": GROG_MARKERS,
    "character_markers_provenance_source_path": GROG_SRC,
    "character_markers_provenance_field": "grog_identifiers",
    # missing sha256
}}}
r2 = resolve_character_markers("pm_probe", cfg_pm, manifest_pm)

# 3. CHARACTER_MARKERS_VALUE_MISMATCH from ANIM-03 path —
#    manifest has wrong character_markers text but correct sha + field
cfg_vm = {"character": "grog"}
manifest_vm = {"characters": {"grog": {
    "character_markers": "fabricated wrong text — not from source",
    "character_markers_provenance_source_path": GROG_SRC,
    "character_markers_provenance_field": "grog_identifiers",
    "character_markers_provenance_sha256": GROG_SHA,
}}}
r3 = resolve_character_markers("vm_probe", cfg_vm, manifest_vm)

# 4. CHARACTER_MARKERS_SOURCE_CONFLICT — projects.json + ANIM-03 both valid
#    but record different marker strings (verified individually against
#    DIFFERENT source fields)
cfg_conf = {
    "character": "grog",
    "character_markers": GROG_MARKERS,
    "character_markers_provenance_source_path": GROG_SRC,
    "character_markers_provenance_field": "grog_identifiers",
    "character_markers_provenance_sha256": GROG_SHA,
}
YOUNG_GROG_MARKERS = (
    "tiny toddler ogre with warm beige skin, smooth round clean-shaven cheeks, "
    "wide innocent warm brown eyes, stubby chubby fingers, "
    "already twice the height of a full-grown adult"
)
manifest_conf = {"characters": {"grog": {
    "character_markers": YOUNG_GROG_MARKERS,
    "character_markers_provenance_source_path": GROG_SRC,
    "character_markers_provenance_field": "young_grog_identifiers",
    "character_markers_provenance_sha256": GROG_SHA,
}}}
r4 = resolve_character_markers("conf_probe", cfg_conf, manifest_conf)

# Sanity: success path resolving from ANIM-03 only
cfg_ok = {"character": "grog"}
manifest_ok = {"characters": {"grog": {
    "character_markers": GROG_MARKERS,
    "character_markers_provenance_source_path": GROG_SRC,
    "character_markers_provenance_field": "grog_identifiers",
    "character_markers_provenance_sha256": GROG_SHA,
}}}
r5 = resolve_character_markers("ok_probe", cfg_ok, manifest_ok)

# ANIM-14 r1 F-3 fix: project-complete must succeed even when manifest is
# incidentally partial (registry-inconsistency tolerance for the project
# that already declares its markers explicitly).
cfg_full_proj = {
    "character": "grog",
    "character_markers": GROG_MARKERS,
    "character_markers_provenance_source_path": GROG_SRC,
    "character_markers_provenance_field": "grog_identifiers",
    "character_markers_provenance_sha256": GROG_SHA,
}
manifest_partial = {"characters": {"grog": {
    "character_markers": GROG_MARKERS,
    "character_markers_provenance_source_path": GROG_SRC,
    "character_markers_provenance_field": "grog_identifiers",
    # missing sha256 (3-of-4)
}}}
r6 = resolve_character_markers("proj_full_manifest_partial_probe",
                                cfg_full_proj, manifest_partial)

out = {
    "phase": "ANIM-14",
    "probes": {
        "CHARACTER_MARKERS_NOT_FOUND": r1,
        "CHARACTER_MARKERS_MANIFEST_PARTIAL_when_project_absent": r2,
        "CHARACTER_MARKERS_VALUE_MISMATCH_from_manifest": r3,
        "CHARACTER_MARKERS_SOURCE_CONFLICT": r4,
        "OK_via_manifest_only": r5,
        "OK_project_complete_with_manifest_partial_tolerated": r6,
    },
}
print(json.dumps(out, indent=2))
