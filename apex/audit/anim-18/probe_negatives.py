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


def _read_real_key(shim) -> str:
    """Read the live FAL_AI_API_KEY for the leak-check assertion only.

    ANIM-18 r1 F-4 fix: reuse the shim's own resolve_fal_key() (which itself
    reuses muscle_video_agent.resolve_env_key_from_env_sync()). This avoids
    reimplementing env_sync key lookup in the harness, satisfying the
    ANIM-17 R20 no-new-env-key-resolver constraint.

    The value is held in process memory exclusively for the assertion; never
    returned to the caller, never logged, never written to disk by this
    harness. If env_sync is unreachable, leak-check is skipped (probes still
    run).
    """
    probe = shim.resolve_fal_key()
    if probe.get("status") != "OK":
        return ""
    v = probe.get("key")
    return v if isinstance(v, str) and v else ""


def _assert_no_key_leak(label: str, blob: str, real_key: str) -> dict:
    """ANIM-18 r2 F-2 fix: extend leak check to cover serialized/escaped
    forms of the key as well as the literal bytes. The JSON-escaped form is
    what would survive a json.dumps()/loads() round-trip if the parsed tree
    was redacted only at the serialized level."""
    if not real_key:
        return {"probe": label, "leak_check": "SKIPPED_NO_KEY"}
    escaped = json.dumps(real_key)[1:-1]
    leaked_literal = real_key in blob
    leaked_escaped = escaped != real_key and escaped in blob
    leaked = leaked_literal or leaked_escaped
    return {"probe": label,
            "leak_check": "LEAK" if leaked else "CLEAN",
            "leak_check_literal": leaked_literal,
            "leak_check_escaped": leaked_escaped}


def main() -> int:
    shim = load_shim()
    real_key = _read_real_key(shim)
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

    # Probe 7 — ANIM-18 r1 F-5 fix: key-unresolved regression. Monkeypatch
    # resolve_fal_key() to simulate env_sync being missing/empty and assert
    # build_payload returns FAL_KEY_UNRESOLVED with fingerprint-only metadata.
    original_resolver = shim.resolve_fal_key
    shim.resolve_fal_key = lambda: {"status": "ENV_KEY_MISSING",
                                      "env_sync_path": "X:/env_sync/user_portable.json",
                                      "field": "FAL_AI_API_KEY"}
    try:
        r = shim.build_payload(
            "1", str(REPO_ROOT
                     / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json"))
    finally:
        shim.resolve_fal_key = original_resolver
    out["probes"].append({
        "id": "FAL_KEY_UNRESOLVED",
        "expected_status": "FAL_KEY_UNRESOLVED",
        "actual_status": r.get("status"),
        "pass": (r.get("status") == "FAL_KEY_UNRESOLVED"
                 and isinstance(r.get("key_resolution"), dict)
                 and "key" not in r.get("key_resolution", {})),
        "result": r,
        **_assert_no_key_leak("P7", json.dumps(r), real_key),
    })

    # Probe 8 — ANIM-18 r1 F-5 fix: dry-run urlopen suppression spy. Monkeypatch
    # urllib.request.urlopen to a tripwire that flips a flag if called. Default
    # submit_shot() (live=False) MUST NOT call urlopen. If the tripwire fires,
    # the probe fails — that is a HIGH regression (accidental cloud spend).
    import urllib.request as _ulr
    called = {"urlopen": False}

    def _tripwire(*a, **kw):
        called["urlopen"] = True
        raise AssertionError("urlopen called in dry-run path")

    original_urlopen = _ulr.urlopen
    _ulr.urlopen = _tripwire
    try:
        r = shim.submit_shot(
            "1",
            str(REPO_ROOT
                / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json"),
            live=False)
    finally:
        _ulr.urlopen = original_urlopen
    out["probes"].append({
        "id": "DRY_RUN_URLOPEN_SUPPRESSED",
        "expected_status": "DRY_RUN",
        "actual_status": r.get("status"),
        "urlopen_called": called["urlopen"],
        "pass": r.get("status") == "DRY_RUN" and not called["urlopen"],
        "result": r,
        **_assert_no_key_leak("P8", json.dumps(r), real_key),
    })

    # Probes 9–11 — ANIM-18 r3 F-2 fix: monkeypatch urlopen with synthetic
    # responses that smuggle the live key into the body, as a property name,
    # and as a JSON-escaped string. The shim's redaction layer must scrub
    # every form before the result is printed or audited. Without these
    # probes, regressions in _http_post_json / _redact_key_from_obj /
    # poll_job would not be caught.
    import urllib.request as _ulr
    import io as _io

    class _FakeResp:
        def __init__(self, body_bytes: bytes, status: int = 200):
            self._body = body_bytes
            self.status = status
        def read(self):
            return self._body
        def __enter__(self):
            return self
        def __exit__(self, *a):
            return False

    if real_key:
        # P9 — successful JSON response with raw key as a value.
        body = json.dumps({"request_id": "abc12345",
                           "echo": real_key}).encode("utf-8")
        original = _ulr.urlopen
        _ulr.urlopen = lambda req, timeout=30: _FakeResp(body, 200)
        try:
            r = shim.submit_shot(
                "1",
                str(REPO_ROOT
                    / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json"),
                live=True)
        finally:
            _ulr.urlopen = original
        out["probes"].append({
            "id": "MOCK_LIVE_VALUE_REDACTED",
            "expected_status": "FAL_OK",
            "actual_status": r.get("status"),
            "pass": (r.get("status") == "FAL_OK"
                     and "FAL_OK" in r.get("status", "")),
            "result": r,
            **_assert_no_key_leak("P9", json.dumps(r), real_key),
        })

        # P10 — successful JSON response with raw key as a property NAME
        # (this is the F-1 HIGH that r3 added dict-key redaction to fix).
        body = json.dumps({"request_id": "abc12346",
                           real_key: "value-under-key-name"}).encode("utf-8")
        _ulr.urlopen = lambda req, timeout=30: _FakeResp(body, 200)
        try:
            r = shim.submit_shot(
                "1",
                str(REPO_ROOT
                    / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json"),
                live=True)
        finally:
            _ulr.urlopen = original
        out["probes"].append({
            "id": "MOCK_LIVE_DICT_KEY_REDACTED",
            "expected_status": "FAL_OK",
            "actual_status": r.get("status"),
            "pass": r.get("status") == "FAL_OK",
            "result": r,
            **_assert_no_key_leak("P10", json.dumps(r), real_key),
        })

        # P11 — HTTPError body containing the raw key (echo of Authorization).
        class _FakeHTTPError(Exception):
            def __init__(self, body_bytes: bytes):
                self._body = body_bytes
                self.code = 401
                self.reason = "Unauthorized"
            def read(self):
                return self._body

        # Need a urllib.error.HTTPError subclass for the except branch to
        # match. Build a real one with the live body bytes.
        from urllib.error import HTTPError
        err_body = ("UNAUTHORIZED: header=Authorization: Key "
                    + real_key).encode("utf-8")

        def _raise_http_error(req, timeout=30):
            raise HTTPError(url=req.full_url if hasattr(req, "full_url") else "",
                            code=401, msg="Unauthorized",
                            hdrs=None, fp=_io.BytesIO(err_body))

        _ulr.urlopen = _raise_http_error
        try:
            r = shim.submit_shot(
                "1",
                str(REPO_ROOT
                    / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json"),
                live=True)
        finally:
            _ulr.urlopen = original
        out["probes"].append({
            "id": "MOCK_LIVE_HTTP_ERROR_BODY_REDACTED",
            "expected_status": "FAL_HTTP_ERROR",
            "actual_status": r.get("status"),
            "pass": r.get("status") == "FAL_HTTP_ERROR",
            "result": r,
            **_assert_no_key_leak("P11", json.dumps(r), real_key),
        })

    out["probe_count"] = len(out["probes"])
    passed = sum(1 for p in out["probes"] if p.get("pass"))
    out["passed"] = passed
    out["failed"] = out["probe_count"] - passed

    # Global leak check across the entire output blob — literal + escaped.
    if real_key:
        blob = json.dumps(out)
        escaped = json.dumps(real_key)[1:-1]
        leaked_literal = real_key in blob
        leaked_escaped = escaped != real_key and escaped in blob
        out["leak_check_global"] = (
            "LEAK" if (leaked_literal or leaked_escaped) else "CLEAN")
        out["leak_check_global_literal"] = leaked_literal
        out["leak_check_global_escaped"] = leaked_escaped
    else:
        out["leak_check_global"] = "SKIPPED_NO_KEY"

    print(json.dumps(out, indent=2))
    return 0 if passed == out["probe_count"] and out["leak_check_global"] != "LEAK" else 1


if __name__ == "__main__":
    sys.exit(main())
