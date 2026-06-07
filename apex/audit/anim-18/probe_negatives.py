#!/usr/bin/env python3
"""ANIM-18 negative-path probe harness.

Probes exercised against muscle_fal_shim.py. Each probe asserts the shim
returns a stable status enum (not a Python traceback) and the raw key
never appears in any captured output.

ANIM-18 r5 hardening:
- Redaction-regression probes now use a SENTINEL key (not the live one),
  so coverage runs unconditionally — env_sync availability no longer
  decides whether the harness exercises the redaction layer.
- Harness is fail-closed: before printing the result blob to stdout, a
  global scrub redacts BOTH the live key (if resolvable) AND the sentinel
  from every string in the output tree. A redaction regression detected
  by a probe will surface as a failed probe + LEAK leak_check, but the
  printed output is sanitized — the harness never publishes the secret
  it was checking.

Run from repo root:
  APEX_REPO=. python apex/audit/anim-18/probe_negatives.py
"""
from __future__ import annotations
import importlib.util
import io as _io
import json
import os
import sys
import tempfile
import urllib.request as _ulr
from pathlib import Path
from urllib.error import HTTPError

REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
SHIM_PATH = REPO_ROOT / "apex/registry/muscle_fal_shim.py"

# Sentinel used in monkeypatched resolver/mock responses so the harness can
# inject "leaky" material without depending on a live credential. The shim's
# redaction layer must scrub the sentinel from every persisted/printed string
# exactly the way it must scrub the live key.
SENTINEL_KEY = "SENTINEL-FAL-KEY-NOT-FOR-USE-ABCDEFGHIJKLMNOPQRSTUVWXYZ-1234567890"


def load_shim():
    spec = importlib.util.spec_from_file_location("shim", str(SHIM_PATH))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import shim at {SHIM_PATH}")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _read_real_key(shim) -> str:
    """Read the live FAL_AI_API_KEY for the leak-check assertion only.

    Reuses the shim's own resolve_fal_key() (which itself reuses
    muscle_video_agent.resolve_env_key_from_env_sync()). The value is held
    in process memory exclusively for the assertion; never returned to
    callers outside this module.
    """
    probe = shim.resolve_fal_key()
    if probe.get("status") != "OK":
        return ""
    v = probe.get("key")
    return v if isinstance(v, str) and v else ""


def _check_key_leak(label: str, blob: str, key: str, key_label: str) -> dict:
    """Assert `key` does not appear (literal or JSON-escaped) in `blob`."""
    if not key:
        return {"probe": label,
                f"leak_check_{key_label}": "SKIPPED_NO_KEY"}
    escaped = json.dumps(key)[1:-1]
    leaked_literal = key in blob
    leaked_escaped = escaped != key and escaped in blob
    leaked = leaked_literal or leaked_escaped
    return {"probe": label,
            f"leak_check_{key_label}": "LEAK" if leaked else "CLEAN",
            f"leak_check_{key_label}_literal": leaked_literal,
            f"leak_check_{key_label}_escaped": leaked_escaped}


def _assert_no_leaks(label: str, blob: str, real_key: str) -> dict:
    """Check both the live key and the sentinel."""
    out = {}
    out.update(_check_key_leak(label, blob, real_key, "real"))
    out.update(_check_key_leak(label, blob, SENTINEL_KEY, "sentinel"))
    # Aggregate `leak_check` (back-compat with prior probe schema): LEAK if
    # either real or sentinel detected as leaked.
    out["leak_check"] = "CLEAN"
    if out.get("leak_check_real") == "LEAK" or out.get("leak_check_sentinel") == "LEAK":
        out["leak_check"] = "LEAK"
    return out


def _fail_closed_scrub(obj, *keys: str):
    """Recursively scrub every (literal + JSON-escaped) form of every key
    from `obj`. Used at the very end of the harness, immediately before
    printing the result blob, so a redaction regression cannot make the
    harness itself publish the secret it is checking."""
    real_keys = [k for k in keys if k]
    if not real_keys:
        return obj
    if isinstance(obj, str):
        out = obj
        for k in real_keys:
            out = out.replace(k, "[REDACTED]")
            esc = json.dumps(k)[1:-1]
            if esc != k:
                out = out.replace(esc, "[REDACTED]")
        return out
    if isinstance(obj, list):
        return [_fail_closed_scrub(x, *keys) for x in obj]
    if isinstance(obj, dict):
        return {_fail_closed_scrub(k, *keys) if isinstance(k, str) else k:
                _fail_closed_scrub(v, *keys)
                for k, v in obj.items()}
    return obj


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


def _record(out, probe_id, expected, result, real_key, extra=None):
    rec = {
        "id": probe_id,
        "expected_status": expected,
        "actual_status": result.get("status"),
        "pass": result.get("status") == expected,
        "result": result,
        **_assert_no_leaks(probe_id, json.dumps(result), real_key),
    }
    if extra:
        rec.update(extra)
    out["probes"].append(rec)


def main() -> int:
    shim = load_shim()
    real_key = _read_real_key(shim)
    out = {"phase": "ANIM-18",
           "sentinel_key_used_for_unconditional_coverage": True,
           "probe_count": 0, "probes": [],
           "leak_check_global": None}

    # ---- P1-P6: build_payload negative paths (no key needed) ----

    r = shim.build_payload("1", "/path/that/does/not/exist.json")
    _record(out, "TIER_PLAN_NOT_FOUND", "TIER_PLAN_NOT_FOUND", r, real_key)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write("not-a-json-doc{{{")
        bad_path = f.name
    try:
        r = shim.build_payload("1", bad_path)
        _record(out, "TIER_PLAN_UNPARSEABLE", "TIER_PLAN_UNPARSEABLE", r, real_key)
    finally:
        os.unlink(bad_path)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        f.write(json.dumps({"phase": "ANIM-99", "shots": [{"id": "1"}]}))
        wrong_phase_path = f.name
    try:
        r = shim.build_payload("1", wrong_phase_path)
        _record(out, "TIER_PLAN_INVALID_PHASE", "TIER_PLAN_INVALID_PHASE", r, real_key)
    finally:
        os.unlink(wrong_phase_path)

    falcloud_plan = str(REPO_ROOT
                        / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json")
    energy_plan = str(REPO_ROOT
                      / "apex/docs/anim/ANIM-16-tier-plan-grog_playground-energy.json")

    r = shim.build_payload("99999", falcloud_plan)
    _record(out, "SHOT_NOT_IN_TIER_PLAN", "SHOT_NOT_IN_TIER_PLAN", r, real_key)

    r = shim.build_payload("1", energy_plan)
    _record(out, "SHOT_NOT_ROUTED_TO_FALCLOUD", "SHOT_NOT_ROUTED_TO_FALCLOUD", r, real_key)

    r = shim.build_payload("invalid id with spaces", falcloud_plan)
    _record(out, "INVALID_SHOT_ID", "INVALID_SHOT_ID", r, real_key)

    # ---- P7: key-unresolved regression (monkeypatched resolver) ----

    original_resolver = shim.resolve_fal_key
    shim.resolve_fal_key = lambda: {"status": "ENV_KEY_MISSING",
                                      "env_sync_path": "X:/env_sync/user_portable.json",
                                      "field": "FAL_AI_API_KEY"}
    try:
        r = shim.build_payload("1", falcloud_plan)
    finally:
        shim.resolve_fal_key = original_resolver
    _record(out, "FAL_KEY_UNRESOLVED", "FAL_KEY_UNRESOLVED", r, real_key)

    # ---- P8: dry-run urlopen suppression (tripwire spy) ----

    called = {"urlopen": False}

    def _tripwire(*a, **kw):
        called["urlopen"] = True
        raise AssertionError("urlopen called in dry-run path")

    original_urlopen = _ulr.urlopen
    _ulr.urlopen = _tripwire
    try:
        r = shim.submit_shot("1", falcloud_plan, live=False)
    finally:
        _ulr.urlopen = original_urlopen
    _record(out, "DRY_RUN_URLOPEN_SUPPRESSED", "DRY_RUN", r, real_key,
            extra={"urlopen_called": called["urlopen"],
                   "pass": r.get("status") == "DRY_RUN" and not called["urlopen"]})

    # ---- P9-P11: live-path mocked-response redaction with SENTINEL key ----
    # Unconditional (do not require real_key). Monkeypatch resolve_fal_key
    # to return a sentinel-bearing OK probe so submit_shot --live exercises
    # the live HTTP redaction path regardless of env_sync availability.

    sentinel_probe = {
        "status": "OK", "key": SENTINEL_KEY,
        "fingerprint": "SENT:INEL",
        "key_sha256_first_12": "deadbeef0000",
        "key_length": len(SENTINEL_KEY),
        "env_sync_path": "<sentinel>", "field": "FAL_AI_API_KEY",
    }

    shim.resolve_fal_key = lambda: dict(sentinel_probe)
    try:
        # P9 — successful JSON response with sentinel in a value field.
        body = json.dumps({"request_id": "abc12345",
                           "echo": SENTINEL_KEY}).encode("utf-8")
        _ulr.urlopen = lambda req, timeout=30: _FakeResp(body, 200)
        try:
            r = shim.submit_shot("1", falcloud_plan, live=True)
        finally:
            _ulr.urlopen = original_urlopen
        _record(out, "MOCK_LIVE_VALUE_REDACTED", "FAL_OK", r, real_key)

        # P10 — successful JSON response with sentinel as a property name.
        body = json.dumps({"request_id": "abc12346",
                           SENTINEL_KEY: "value-under-sentinel-key-name"}).encode("utf-8")
        _ulr.urlopen = lambda req, timeout=30: _FakeResp(body, 200)
        try:
            r = shim.submit_shot("1", falcloud_plan, live=True)
        finally:
            _ulr.urlopen = original_urlopen
        _record(out, "MOCK_LIVE_DICT_KEY_REDACTED", "FAL_OK", r, real_key)

        # P11 — HTTPError body containing the sentinel (echo of Authorization).
        err_body = ("UNAUTHORIZED: header=Authorization: Key "
                    + SENTINEL_KEY).encode("utf-8")

        def _raise_http_error(req, timeout=30):
            raise HTTPError(url=getattr(req, "full_url", ""),
                            code=401, msg="Unauthorized",
                            hdrs=None, fp=_io.BytesIO(err_body))

        _ulr.urlopen = _raise_http_error
        try:
            r = shim.submit_shot("1", falcloud_plan, live=True)
        finally:
            _ulr.urlopen = original_urlopen
        _record(out, "MOCK_LIVE_HTTP_ERROR_BODY_REDACTED", "FAL_HTTP_ERROR",
                r, real_key)

    finally:
        shim.resolve_fal_key = original_resolver

    # ---- P12-P14: non-live resolver leak surface with SENTINEL key ----
    # Unconditional. The leaky resolver returns the sentinel in extra value
    # field, nested dict, and as a dict KEY. allowlist fingerprint_only +
    # _seal_outward must strip all three regardless of which mode runs.

    leaky_sentinel_probe = {
        "status": "OK", "key": SENTINEL_KEY,
        "echo": SENTINEL_KEY,
        "nested": {"deeper": SENTINEL_KEY},
        SENTINEL_KEY: "value-under-sentinel-key-name",
        "fingerprint": "SENT:INEL",
        "key_sha256_first_12": "deadbeef0000",
        "key_length": len(SENTINEL_KEY),
        "env_sync_path": "<sentinel>", "field": "FAL_AI_API_KEY",
    }
    shim.resolve_fal_key = lambda: dict(leaky_sentinel_probe)
    try:
        r = shim.probe()
        _record(out, "RESOLVER_LEAK_PROBE", "READY", r, real_key,
                extra={"pass": r.get("status") in ("READY", "KEY_OK_SHIM_PENDING")})
        r = shim.build_payload("1", falcloud_plan)
        _record(out, "RESOLVER_LEAK_BUILD_PAYLOAD", "PAYLOAD", r, real_key)
        r = shim.submit_shot("1", falcloud_plan, live=False)
        _record(out, "RESOLVER_LEAK_DRY_RUN", "DRY_RUN", r, real_key)
    finally:
        shim.resolve_fal_key = original_resolver

    # ---- Aggregate + fail-closed scrub before any print ----

    out["probe_count"] = len(out["probes"])
    passed = sum(1 for p in out["probes"] if p.get("pass"))
    out["passed"] = passed
    out["failed"] = out["probe_count"] - passed

    # Global leak check across the entire output blob — both keys, both forms.
    raw_blob = json.dumps(out)
    real_leaked = bool(real_key) and (
        real_key in raw_blob
        or (json.dumps(real_key)[1:-1] != real_key
            and json.dumps(real_key)[1:-1] in raw_blob))
    sentinel_leaked = (SENTINEL_KEY in raw_blob
                       or (json.dumps(SENTINEL_KEY)[1:-1] != SENTINEL_KEY
                           and json.dumps(SENTINEL_KEY)[1:-1] in raw_blob))
    out["leak_check_global"] = (
        "LEAK" if (real_leaked or sentinel_leaked) else "CLEAN")
    out["leak_check_global_real"] = real_leaked
    out["leak_check_global_sentinel"] = sentinel_leaked

    # ANIM-18 r5 F-1 fix: fail-closed sanitization. If any redaction
    # regression caused the live key or the sentinel to enter `out`, the
    # leak_check fields above report it, but we MUST NOT print the actual
    # leaked secret on stdout. Scrub both keys from the printed copy.
    printable = _fail_closed_scrub(out, real_key, SENTINEL_KEY)
    print(json.dumps(printable, indent=2))

    ok = passed == out["probe_count"] and out["leak_check_global"] != "LEAK"
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
