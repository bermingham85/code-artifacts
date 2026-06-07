#!/usr/bin/env python3
"""ANIM-18 negative-path probe harness.

Six structured-failure paths exercised against muscle_fal_shim.py without
making any live HTTP call. Each probe asserts the shim returns a stable
status enum (not a Python traceback) and the raw key never appears in any
captured output.

Run from repo root:
  APEX_REPO=. python apex/audit/anim-18/probe_negatives.py
"""
from __future__ import annotations
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

# Locate the shim relative to repo root (APEX_REPO env or cwd).
REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
SHIM_PATH = REPO_ROOT / "apex/registry/muscle_fal_shim.py"


def load_shim():
    spec = importlib.util.spec_from_file_location("shim", str(SHIM_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import shim at {SHIM_PATH}")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _read_real_key() -> str:
    """Read the live FAL_AI_API_KEY for the leak-check assertion only.

    The value is held in process memory exclusively for the assertion; never
    returned to the caller, never logged, never written to disk by this
    harness. If env_sync is unreachable, leak-check is skipped (probe still
    runs).
    """
    cfg_path = REPO_ROOT / "apex/docs/anim/ANIM-05-tier-config.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        fc = cfg["tiers"]["FalCloud"]
        env_path = Path(fc["requires_env_key_from_env_sync_path"])
        env_field = fc["requires_env_key_field"]
        data = json.loads(env_path.read_text(encoding="utf-8-sig"))
        v = data.get(env_field)
        return v if isinstance(v, str) and v else ""
    except (OSError, KeyError, json.JSONDecodeError):
        return ""


def _assert_no_key_leak(label: str, blob: str, real_key: str) -> dict:
    if not real_key:
        return {"probe": label, "leak_check": "SKIPPED_NO_KEY"}
    leaked = real_key in blob
    return {"probe": label,
            "leak_check": "LEAK" if leaked else "CLEAN"}


def main() -> int:
    shim = load_shim()
    real_key = _read_real_key()
    out = {"phase": "ANIM-18", "probe_count": 0, "probes": [],
           "leak_check_global": None}

    # Probe 1 — tier-plan path missing.
    r = shim.build_payload("1", "/path/that/does/not/exist.json")
    out["probes"].append({
        "id": "TIER_PLAN_NOT_FOUND",
        "expected_status": "TIER_PLAN_NOT_FOUND",
        "actual_status": r.get("status"),
        "pass": r.get("status") == "TIER_PLAN_NOT_FOUND",
        "result": r,
        **_assert_no_key_leak("P1", json.dumps(r), real_key),
    })

    # Probe 2 — tier-plan is not valid JSON.
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write("not-a-json-doc{{{")
        bad_path = f.name
    try:
        r = shim.build_payload("1", bad_path)
        out["probes"].append({
            "id": "TIER_PLAN_UNPARSEABLE",
            "expected_status": "TIER_PLAN_UNPARSEABLE",
            "actual_status": r.get("status"),
            "pass": r.get("status") == "TIER_PLAN_UNPARSEABLE",
            "result": r,
            **_assert_no_key_leak("P2", json.dumps(r), real_key),
        })
    finally:
        os.unlink(bad_path)

    # Probe 3 — tier-plan with wrong phase tag.
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(json.dumps({"phase": "ANIM-99", "shots": [{"id": "1"}]}))
        wrong_phase_path = f.name
    try:
        r = shim.build_payload("1", wrong_phase_path)
        out["probes"].append({
            "id": "TIER_PLAN_INVALID_PHASE",
            "expected_status": "TIER_PLAN_INVALID_PHASE",
            "actual_status": r.get("status"),
            "pass": r.get("status") == "TIER_PLAN_INVALID_PHASE",
            "result": r,
            **_assert_no_key_leak("P3", json.dumps(r), real_key),
        })
    finally:
        os.unlink(wrong_phase_path)

    # Probe 4 — shot not present in plan.
    r = shim.build_payload(
        "99999", str(REPO_ROOT
                     / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json"))
    out["probes"].append({
        "id": "SHOT_NOT_IN_TIER_PLAN",
        "expected_status": "SHOT_NOT_IN_TIER_PLAN",
        "actual_status": r.get("status"),
        "pass": r.get("status") == "SHOT_NOT_IN_TIER_PLAN",
        "result": r,
        **_assert_no_key_leak("P4", json.dumps(r), real_key),
    })

    # Probe 5 — shot exists but is routed to a different tier.
    r = shim.build_payload(
        "1", str(REPO_ROOT
                 / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-energy.json"))
    out["probes"].append({
        "id": "SHOT_NOT_ROUTED_TO_FALCLOUD",
        "expected_status": "SHOT_NOT_ROUTED_TO_FALCLOUD",
        "actual_status": r.get("status"),
        "pass": r.get("status") == "SHOT_NOT_ROUTED_TO_FALCLOUD",
        "result": r,
        **_assert_no_key_leak("P5", json.dumps(r), real_key),
    })

    # Probe 6 — invalid shot-id (regex reject).
    r = shim.build_payload(
        "invalid id with spaces",
        str(REPO_ROOT / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json"))
    out["probes"].append({
        "id": "INVALID_SHOT_ID",
        "expected_status": "INVALID_SHOT_ID",
        "actual_status": r.get("status"),
        "pass": r.get("status") == "INVALID_SHOT_ID",
        "result": r,
        **_assert_no_key_leak("P6", json.dumps(r), real_key),
    })

    out["probe_count"] = len(out["probes"])
    passed = sum(1 for p in out["probes"] if p.get("pass"))
    out["passed"] = passed
    out["failed"] = out["probe_count"] - passed

    # Global leak check across the entire output blob.
    if real_key:
        out["leak_check_global"] = (
            "LEAK" if real_key in json.dumps(out) else "CLEAN")
    else:
        out["leak_check_global"] = "SKIPPED_NO_KEY"

    print(json.dumps(out, indent=2))
    return 0 if passed == out["probe_count"] and out["leak_check_global"] != "LEAK" else 1


if __name__ == "__main__":
    sys.exit(main())
