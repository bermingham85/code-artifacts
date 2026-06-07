#!/usr/bin/env python3
"""APEX-MB-PY-00118 muscle_fal_shim.py

fal.ai animation-agent wrapper shim — closes WO §1.4 FalCloud write side.
ANIM-17 closed the env-key READ side; this shim closes the WRITE side by
turning a tier-plan record into a deterministic fal.ai queue submission.

Modes:
  --probe                     auth-shape sanity check, no submission
  --build-payload --shot-id <id> --tier-plan <path>
                              deterministic payload assembly (dry-run print)
  --submit --shot-id <id> --tier-plan <path> [--live]
                              dry-run by default; --live REQUIRED to actually POST
  --poll --job-id <id>        status query against fal.ai

Key handling reuses muscle_video_agent.resolve_env_key_from_env_sync() —
no new env-key resolver per ANIM-17 R20. Fingerprint exposure only
(first4:last4 + sha256[:12] + key_length); raw key bytes never persisted.
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(os.environ.get("APEX_REPO", "."))
TIER_CONFIG_PATH = REPO_ROOT / "apex/docs/anim/ANIM-05-tier-config.json"
AUDIT_ROOT = REPO_ROOT / "apex/audit/anim-18"

# fal.ai queue endpoint surface (documented at fal.ai; pinned here so a future
# API rename is a one-line code change rather than a redesign).
FAL_QUEUE_BASE = "https://queue.fal.run"
FAL_MODEL_ID = "fal-ai/animation-agent"
SUBMIT_URL = f"{FAL_QUEUE_BASE}/{FAL_MODEL_ID}"
POLL_URL_TEMPLATE = f"{FAL_QUEUE_BASE}/{FAL_MODEL_ID}/requests/{{job_id}}/status"

SHOT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
JOB_ID_RE = re.compile(r"^[A-Za-z0-9\-]{8,128}$")
DEFAULT_TIMEOUT_SECONDS = 30


def _import_video_agent():
    """Import muscle_video_agent so we can reuse the ANIM-17 key resolver.

    Using importlib (rather than a regular `from . import …`) keeps the shim
    runnable as a standalone script when registry/ is not on sys.path.
    """
    here = Path(__file__).parent
    target = here / "muscle_video_agent.py"
    spec = importlib.util.spec_from_file_location(
        "muscle_video_agent", str(target))
    if spec is None or spec.loader is None:
        raise RuntimeError("muscle_video_agent.py not found beside shim")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_tier_config() -> dict:
    if not TIER_CONFIG_PATH.is_file():
        return {"tiers": {}}
    return json.loads(TIER_CONFIG_PATH.read_text(encoding="utf-8"))


def resolve_fal_key() -> dict:
    """Resolve FAL_AI_API_KEY via the ANIM-17 helper. Never persists the key."""
    cfg = load_tier_config().get("tiers", {}).get("FalCloud")
    if not cfg:
        return {"status": "TIER_NOT_CONFIGURED", "tier": "FalCloud"}
    env_path = cfg.get("requires_env_key_from_env_sync_path")
    env_field = cfg.get("requires_env_key_field")
    if not env_path or not env_field:
        return {"status": "TIER_CONFIG_INCOMPLETE", "tier": "FalCloud"}
    va = _import_video_agent()
    probe = va.resolve_env_key_from_env_sync(env_path, env_field)
    return probe


def fingerprint_only(probe: dict) -> dict:
    """Strip the raw key from a probe dict, leaving fingerprint metadata only."""
    return {k: v for k, v in probe.items() if k != "key"}


def validate_tier_plan(tier_plan_path: str) -> dict:
    p = Path(tier_plan_path)
    if not p.is_file():
        return {"status": "TIER_PLAN_NOT_FOUND",
                "tier_plan_path": tier_plan_path}
    try:
        # ANIM-18 r1 F-2 fix: catch UnicodeDecodeError as well so a non-UTF8
        # tier-plan returns a stable failure enum instead of crashing with
        # an unstructured stack trace.
        text = p.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        return {"status": "TIER_PLAN_UNREADABLE",
                "tier_plan_path": tier_plan_path,
                "error": f"{type(e).__name__}: {e}"}
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return {"status": "TIER_PLAN_UNPARSEABLE",
                "tier_plan_path": tier_plan_path, "error": str(e)}
    if not isinstance(data, dict):
        return {"status": "TIER_PLAN_UNPARSEABLE",
                "tier_plan_path": tier_plan_path,
                "error": "top-level JSON must be an object"}
    if data.get("phase") != "ANIM-16":
        return {"status": "TIER_PLAN_INVALID_PHASE",
                "tier_plan_path": tier_plan_path,
                "actual_phase": data.get("phase")}
    if not isinstance(data.get("shots"), list) or not data["shots"]:
        return {"status": "TIER_PLAN_EMPTY",
                "tier_plan_path": tier_plan_path}
    return {"status": "OK", "tier_plan": data,
            "tier_plan_path": tier_plan_path}


def pick_shot(tier_plan: dict, shot_id: str) -> dict:
    # ANIM-18 r1 F-3 fix: guard isinstance(shot, dict) so a malformed
    # tier-plan with e.g. [null] or [42] in shots does not crash with
    # AttributeError on shot.get().
    for shot in tier_plan["shots"]:
        if not isinstance(shot, dict):
            continue
        if str(shot.get("id")) == shot_id:
            return shot
    return {}


def build_payload(shot_id: str, tier_plan_path: str) -> dict:
    """Assemble a deterministic fal.ai submission payload from a tier-plan shot.

    Returns either {status: PAYLOAD, payload: {...}, key_fingerprint: {...}}
    or {status: <error-enum>, ...}. Same inputs always produce the same
    payload bytes (built_at field excluded from the payload itself — it lives
    in the wrapper envelope so live HTTP calls are still time-stamped).
    """
    if not SHOT_ID_RE.match(shot_id):
        return {"status": "INVALID_SHOT_ID", "shot": shot_id,
                "expected_regex": SHOT_ID_RE.pattern}
    tp = validate_tier_plan(tier_plan_path)
    if tp["status"] != "OK":
        return tp
    tier_plan = tp["tier_plan"]
    shot = pick_shot(tier_plan, shot_id)
    if not shot:
        return {"status": "SHOT_NOT_IN_TIER_PLAN",
                "shot_id": shot_id, "tier_plan_path": tier_plan_path}
    if shot.get("tier_chosen") != "FalCloud":
        return {"status": "SHOT_NOT_ROUTED_TO_FALCLOUD",
                "shot_id": shot_id,
                "tier_chosen": shot.get("tier_chosen")}
    key_probe = resolve_fal_key()
    if key_probe.get("status") != "OK":
        return {"status": "FAL_KEY_UNRESOLVED",
                "key_resolution": fingerprint_only(key_probe)}
    # Deterministic payload — no timestamps, no randomness. fal.ai
    # animation-agent input schema (input.prompt + input.image_url +
    # input.aspect_ratio + input.duration) is pinned here; documented in
    # ANIM-18-evidence.json. Fields drawn from the tier-plan shot record
    # only; nothing invented at runtime.
    duration = shot.get("duration_seconds")
    payload = {
        "input": {
            "prompt": shot.get("kontext_prompt_template") or "",
            "image_url": shot.get("anchor_image_url") or "",
            "aspect_ratio": shot.get("aspect_ratio") or "16:9",
            "duration": float(duration) if isinstance(duration, (int, float)) else 0.0,
            "needs_fill": bool(shot.get("needs_fill", False)),
        },
        "metadata": {
            "shot_id": shot_id,
            "tier_plan_phase": tier_plan.get("phase"),
            "tier_plan_project": tier_plan.get("project"),
            "scene_slug": tier_plan.get("scene_slug"),
            "character_markers": shot.get("character_markers"),
            "character_markers_source": shot.get("character_markers_source"),
        },
    }
    return {"status": "PAYLOAD",
            "payload": payload,
            "key_fingerprint": fingerprint_only(key_probe),
            "submit_url": SUBMIT_URL}


def _redact_key_from_text(text: str, raw_key: str | None) -> str:
    """Replace any occurrence of the raw key in `text` with a redaction marker.

    ANIM-18 r1 F-1 fix: an upstream proxy or fal.ai error envelope may echo
    the Authorization header back in the response body. Any persisted excerpt
    of that body must redact the raw key before being printed, logged or
    audited. Caller passes the raw key bytes for in-process scrubbing only —
    the key itself is never returned by this function.

    ANIM-18 r2 F-2 fix: also redact JSON-escaped forms of the key so that a
    raw key smuggled through json.dumps()/json.loads() cycles is caught. We
    compute the json.dumps() of the bare key (which produces the same
    sequence the encoder would emit) and strip the surrounding quotes; that
    yields the escaped key body to substitute against.
    """
    if not raw_key:
        return text
    out = text.replace(raw_key, "[REDACTED_FAL_KEY]")
    escaped = json.dumps(raw_key)[1:-1]  # strip surrounding quotes
    if escaped != raw_key:
        out = out.replace(escaped, "[REDACTED_FAL_KEY]")
    return out


def _redact_key_from_obj(obj, raw_key: str | None):
    """Recursively walk a parsed-JSON tree and redact raw_key from every str
    leaf AND from every dict key.

    ANIM-18 r2 F-2 fix: redacting only the serialized form misses keys whose
    JSON serialization escapes characters; walking the parsed tree directly
    redacts the literal string value before re-serialization.

    ANIM-18 r3 F-1 fix: also redact dict keys, not just values. A response
    where the raw FAL key appeared as a JSON property NAME would otherwise
    slip through value-only redaction and reach the audit JSON unredacted.
    """
    if not raw_key:
        return obj
    if isinstance(obj, str):
        return _redact_key_from_text(obj, raw_key)
    if isinstance(obj, list):
        return [_redact_key_from_obj(x, raw_key) for x in obj]
    if isinstance(obj, dict):
        return {_redact_key_from_text(k, raw_key) if isinstance(k, str) else k:
                _redact_key_from_obj(v, raw_key)
                for k, v in obj.items()}
    return obj


def _http_post_json(url: str, body: bytes, headers: dict, raw_key: str | None,
                    timeout: int = DEFAULT_TIMEOUT_SECONDS) -> dict:
    req = urllib.request.Request(url, data=body, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                return {"status": "FAL_UNPARSEABLE_RESPONSE",
                        "http_status": resp.status,
                        "error": _redact_key_from_text(str(e), raw_key)}
            # ANIM-18 r2 F-2 fix: redact by walking the parsed object tree
            # (str leaves only), then return the redacted dict directly. This
            # catches keys that JSON-escape (e.g. backslashes/control chars)
            # which the prior dumps-then-replace path missed.
            return {"status": "FAL_OK",
                    "http_status": resp.status,
                    "response": _redact_key_from_obj(parsed, raw_key)}
    except urllib.error.HTTPError as e:
        body_text = ""
        try:
            full_body = e.read().decode("utf-8", errors="replace")
        except (OSError, AttributeError):
            full_body = ""
        # ANIM-18 r2 F-1 fix: redact the FULL decoded body first, then
        # truncate the redacted text. The previous order truncated to 512
        # bytes BEFORE scrubbing, which could leave a key prefix at the
        # tail of the excerpt when the echoed Authorization value straddles
        # the boundary.
        body_text = _redact_key_from_text(full_body, raw_key)[:512]
        return {"status": "FAL_HTTP_ERROR",
                "http_status": getattr(e, "code", None),
                "reason": _redact_key_from_text(
                    str(getattr(e, "reason", "")), raw_key),
                "body_excerpt": body_text}
    except urllib.error.URLError as e:
        return {"status": "FAL_ENDPOINT_UNREACHABLE",
                "error": _redact_key_from_text(
                    f"{type(e).__name__}: {e}", raw_key)}
    except (TimeoutError, OSError) as e:
        return {"status": "FAL_ENDPOINT_UNREACHABLE",
                "error": _redact_key_from_text(
                    f"{type(e).__name__}: {e}", raw_key)}


def submit_shot(shot_id: str, tier_plan_path: str, live: bool) -> dict:
    """Build payload + (only if --live) POST to fal.ai queue. Default = dry-run."""
    built = build_payload(shot_id, tier_plan_path)
    if built["status"] != "PAYLOAD":
        return built
    payload = built["payload"]
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    if not live:
        return {"status": "DRY_RUN",
                "note": "DRY-RUN — no HTTP call made. Pass --live to actually submit.",
                "submit_url": SUBMIT_URL,
                "payload_sha256": hashlib.sha256(body).hexdigest(),
                "payload": payload,
                "key_fingerprint": built["key_fingerprint"]}
    key_probe = resolve_fal_key()
    if key_probe.get("status") != "OK":
        return {"status": "FAL_KEY_UNRESOLVED",
                "key_resolution": fingerprint_only(key_probe)}
    raw_key = key_probe["key"]
    headers = {
        "Authorization": f"Key {raw_key}",
        "Content-Type": "application/json",
    }
    http_result = _http_post_json(SUBMIT_URL, body, headers, raw_key)
    # Wrap result with fingerprint-only key metadata.
    out = {"status": http_result["status"],
           "submit_url": SUBMIT_URL,
           "payload_sha256": hashlib.sha256(body).hexdigest(),
           "fal_response": {k: v for k, v in http_result.items() if k != "status"},
           "key_fingerprint": fingerprint_only(key_probe),
           "submitted_at": datetime.datetime.now(
               datetime.timezone.utc).isoformat(timespec="seconds")}
    # ANIM-18 r3 F-1 fix: final redaction pass before the result leaves this
    # function. Even if _http_post_json missed a leak path, this pass walks
    # the entire output tree (dict keys + values, lists, nested dicts) and
    # strips raw_key + its JSON-escaped form. The previous main() pipeline
    # used json.loads(json.dumps(result)) which was a no-op round-trip.
    return _redact_key_from_obj(out, raw_key)


def poll_job(job_id: str) -> dict:
    if not JOB_ID_RE.match(job_id):
        return {"status": "INVALID_JOB_ID", "job_id": job_id,
                "expected_regex": JOB_ID_RE.pattern}
    key_probe = resolve_fal_key()
    if key_probe.get("status") != "OK":
        return {"status": "FAL_KEY_UNRESOLVED",
                "key_resolution": fingerprint_only(key_probe)}
    url = POLL_URL_TEMPLATE.format(job_id=job_id)
    raw_key = key_probe["key"]
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Key {raw_key}")
    # ANIM-18 r3 F-1 fix: poll_job applies a final _redact_key_from_obj()
    # pass on the result before return. Defined as a small inner wrapper to
    # keep the early-return branches DRY.
    def _seal(result: dict) -> dict:
        return _redact_key_from_obj(result, raw_key)
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SECONDS) as resp:
            raw = resp.read()
            try:
                parsed = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                return _seal({"status": "FAL_UNPARSEABLE_RESPONSE",
                              "http_status": resp.status,
                              "error": _redact_key_from_text(str(e), raw_key),
                              "key_fingerprint": fingerprint_only(key_probe)})
            return _seal({"status": "FAL_OK",
                          "http_status": resp.status,
                          "response": _redact_key_from_obj(parsed, raw_key),
                          "key_fingerprint": fingerprint_only(key_probe)})
    except urllib.error.HTTPError as e:
        return _seal({"status": "FAL_HTTP_ERROR",
                      "http_status": getattr(e, "code", None),
                      "reason": _redact_key_from_text(
                          str(getattr(e, "reason", "")), raw_key),
                      "key_fingerprint": fingerprint_only(key_probe)})
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return _seal({"status": "FAL_ENDPOINT_UNREACHABLE",
                      "error": _redact_key_from_text(
                          f"{type(e).__name__}: {e}", raw_key),
                      "key_fingerprint": fingerprint_only(key_probe)})


def probe() -> dict:
    """Sanity check: resolve key, confirm tier-config wiring, no HTTP call."""
    key_probe = resolve_fal_key()
    cfg = load_tier_config().get("tiers", {}).get("FalCloud", {})
    out = {
        "tier": "FalCloud",
        "submit_url": SUBMIT_URL,
        "key_resolution": fingerprint_only(key_probe),
        "tier_config_shim_status": cfg.get("shim_status"),
        "tier_config_wrapper_invocation": cfg.get("wrapper_invocation"),
    }
    if key_probe.get("status") == "OK" and cfg.get("shim_status") == "READY":
        out["status"] = "READY"
    elif key_probe.get("status") == "OK":
        out["status"] = "KEY_OK_SHIM_PENDING"
    else:
        out["status"] = "KEY_UNRESOLVED"
    return out


def _write_audit(name: str, payload: dict) -> Path:
    AUDIT_ROOT.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    path = AUDIT_ROOT / f"{name}-{ts}.json"
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true",
                    help="auth-shape sanity check; no submission")
    ap.add_argument("--build-payload", action="store_true",
                    help="deterministic payload assembly for one shot (no HTTP)")
    ap.add_argument("--submit", action="store_true",
                    help="dry-run by default; pass --live to actually POST")
    ap.add_argument("--poll", action="store_true",
                    help="GET status for one fal.ai job_id")
    ap.add_argument("--shot-id", help="shot id from the tier-plan")
    ap.add_argument("--tier-plan", help="path to ANIM-16 tier-plan JSON")
    ap.add_argument("--job-id", help="fal.ai job_id for --poll")
    ap.add_argument("--live", action="store_true",
                    help="REQUIRED for --submit to actually POST to fal.ai; "
                         "absence keeps the call dry-run")
    args = ap.parse_args()

    mode_count = sum(1 for x in (args.probe, args.build_payload,
                                  args.submit, args.poll) if x)
    if mode_count == 0:
        ap.print_help()
        return 2
    if mode_count > 1:
        print(json.dumps({"status": "MULTIPLE_MODES",
                          "hint": "pick exactly one of --probe/--build-payload/--submit/--poll"},
                         indent=2))
        return 6

    if args.probe:
        result = probe()
        print(json.dumps(result, indent=2))
        _write_audit("probe", result)
        code_for = {"READY": 0, "KEY_OK_SHIM_PENDING": 14,
                    "KEY_UNRESOLVED": 7}
        return code_for.get(result.get("status", ""), 4)

    if args.build_payload:
        if not args.shot_id or not args.tier_plan:
            print(json.dumps({"status": "MISSING_ARGS",
                              "hint": "--build-payload needs --shot-id and --tier-plan"},
                             indent=2))
            return 6
        result = build_payload(args.shot_id, args.tier_plan)
        print(json.dumps(result, indent=2))
        _write_audit("build-payload", result)
        return 0 if result.get("status") == "PAYLOAD" else 7

    if args.submit:
        if not args.shot_id or not args.tier_plan:
            print(json.dumps({"status": "MISSING_ARGS",
                              "hint": "--submit needs --shot-id and --tier-plan"},
                             indent=2))
            return 6
        result = submit_shot(args.shot_id, args.tier_plan, args.live)
        # Redact any accidental raw key in printed/audited output (defense-in-depth).
        result = json.loads(json.dumps(result))
        print(json.dumps(result, indent=2))
        _write_audit("submit", result)
        code_for = {"DRY_RUN": 0, "FAL_OK": 0,
                    "FAL_KEY_UNRESOLVED": 7,
                    "FAL_HTTP_ERROR": 11,
                    "FAL_ENDPOINT_UNREACHABLE": 12,
                    "FAL_UNPARSEABLE_RESPONSE": 13,
                    "SHOT_NOT_IN_TIER_PLAN": 10,
                    "SHOT_NOT_ROUTED_TO_FALCLOUD": 10,
                    "TIER_PLAN_NOT_FOUND": 10,
                    "TIER_PLAN_UNPARSEABLE": 10,
                    "TIER_PLAN_INVALID_PHASE": 10,
                    "TIER_PLAN_EMPTY": 10,
                    "TIER_PLAN_UNREADABLE": 10,
                    "INVALID_SHOT_ID": 6}
        return code_for.get(result.get("status", ""), 4)

    if args.poll:
        if not args.job_id:
            print(json.dumps({"status": "MISSING_ARGS",
                              "hint": "--poll needs --job-id"}, indent=2))
            return 6
        result = poll_job(args.job_id)
        print(json.dumps(result, indent=2))
        _write_audit("poll", result)
        code_for = {"FAL_OK": 0, "FAL_KEY_UNRESOLVED": 7,
                    "FAL_HTTP_ERROR": 11, "FAL_ENDPOINT_UNREACHABLE": 12,
                    "FAL_UNPARSEABLE_RESPONSE": 13,
                    "INVALID_JOB_ID": 6}
        return code_for.get(result.get("status", ""), 4)

    return 2


if __name__ == "__main__":
    sys.exit(main())
