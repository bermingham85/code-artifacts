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


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """ANIM-18 r7 F-1 fix: refuse 30x redirects on FAL calls.

    CPython's default HTTPRedirectHandler rebuilds the redirected request with
    the original request's headers minus content-type/content-length. That
    means an `Authorization: Key <raw_key>` set with `req.add_header(...)`
    WOULD survive a redirect — including a redirect to a different host. A
    malicious or compromised upstream proxy could 30x to a logging endpoint
    and exfiltrate the credential.

    Defense: install this handler on a per-call opener so any 30x raises
    HTTPError instead of silently re-issuing. The redirect surfaces as
    FAL_HTTP_ERROR with the body already redacted by _redact_key_from_text().
    fal.ai queue API is documented as a direct queue endpoint; redirects are
    not part of its contract, so refusing them does not break legitimate
    traffic.
    """

    def http_error_301(self, req, fp, code, msg, headers):
        raise urllib.error.HTTPError(
            req.full_url, code, "redirect refused (FAL auth safety)",
            headers, fp)

    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


def _no_redirect_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(_NoRedirectHandler())


def _urlopen(req: urllib.request.Request,
             timeout: int = DEFAULT_TIMEOUT_SECONDS):
    """Module-level seam used by _http_post_json + poll_job. Calls into a
    fresh no-redirect opener so 30x responses raise HTTPError instead of
    being followed (ANIM-18 r7 F-1). Defined as a top-level function so
    the probe harness can monkeypatch a single attribute on this module
    rather than reaching into urllib internals.
    """
    return _no_redirect_opener().open(req, timeout=timeout)


def _import_video_agent():
    """Import muscle_video_agent so we can reuse the ANIM-17 key resolver.

    Using importlib (rather than a regular `from . import …`) keeps the shim
    runnable as a standalone script when registry/ is not on sys.path.

    ANIM-18 r6 F-3 fix: returns (module, None) on success or (None, status)
    where status is a stable enum dict. Callers must check the status
    before using the module — uncaught ImportError/OSError previously
    produced an unstructured traceback on every CLI mode.
    """
    here = Path(__file__).parent
    target = here / "muscle_video_agent.py"
    if not target.is_file():
        return None, {"status": "VIDEO_AGENT_NOT_FOUND",
                      "path": str(target).replace("\\", "/")}
    try:
        spec = importlib.util.spec_from_file_location(
            "muscle_video_agent", str(target))
        if spec is None or spec.loader is None:
            return None, {"status": "VIDEO_AGENT_IMPORT_FAILED",
                          "path": str(target).replace("\\", "/")}
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod, None
    except (OSError, ImportError, SyntaxError) as e:
        return None, {"status": "VIDEO_AGENT_IMPORT_FAILED",
                      "error": f"{type(e).__name__}"}


def load_tier_config() -> dict:
    """Load ANIM-05-tier-config.json. ANIM-18 r6 F-3 fix: any read/parse
    error now returns a stable {tiers: {}} shape with a __load_error entry
    so callers can detect the failure without a traceback. CLI modes that
    rely on FalCloud config will then surface TIER_NOT_CONFIGURED through
    the existing resolve_fal_key() path."""
    if not TIER_CONFIG_PATH.is_file():
        return {"tiers": {}, "__load_error": "TIER_CONFIG_NOT_FOUND"}
    try:
        text = TIER_CONFIG_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {"tiers": {}, "__load_error": "TIER_CONFIG_UNREADABLE"}
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return {"tiers": {}, "__load_error": "TIER_CONFIG_UNPARSEABLE"}
    if not isinstance(data, dict):
        return {"tiers": {}, "__load_error": "TIER_CONFIG_INVALID_SHAPE"}
    if "tiers" not in data or not isinstance(data["tiers"], dict):
        return {"tiers": {}, "__load_error": "TIER_CONFIG_MISSING_TIERS"}
    return data


def resolve_fal_key() -> dict:
    """Resolve FAL_AI_API_KEY via the ANIM-17 helper. Never persists the key."""
    cfg = load_tier_config().get("tiers", {}).get("FalCloud")
    # ANIM-18 r7 F-3 fix: previous guard `if not cfg:` only filtered None /
    # empty-dict. A tampered tier-config with e.g. "FalCloud": "tampered"
    # passed truthy and then crashed at cfg.get(...). Validate dict shape so
    # malformed configs return TIER_CONFIG_INVALID_SHAPE (structured) instead.
    if cfg is None:
        return {"status": "TIER_NOT_CONFIGURED", "tier": "FalCloud"}
    if not isinstance(cfg, dict):
        return {"status": "TIER_CONFIG_INVALID_SHAPE", "tier": "FalCloud",
                "actual_type": type(cfg).__name__}
    if not cfg:
        return {"status": "TIER_NOT_CONFIGURED", "tier": "FalCloud"}
    env_path = cfg.get("requires_env_key_from_env_sync_path")
    env_field = cfg.get("requires_env_key_field")
    if not env_path or not env_field:
        return {"status": "TIER_CONFIG_INCOMPLETE", "tier": "FalCloud"}
    va, import_err = _import_video_agent()
    if import_err is not None:
        return {"status": "VIDEO_AGENT_IMPORT_FAILED", **import_err}
    try:
        probe = va.resolve_env_key_from_env_sync(env_path, env_field)
    except (OSError, AttributeError, TypeError):
        return {"status": "RESOLVER_CRASHED"}
    return probe


# ANIM-18 r6 F-1 fix: split the allowlist into two classes —
#   "safe-shape" fields whose values are well-defined enums or short bounded
#   strings under the shim's own control (these are emitted as-is); and
#   "free-form" fields (currently just `error`) whose values can carry
#   arbitrary content from the underlying resolver and must NOT be passed
#   through, because the seal pass cannot scrub them when no key is in scope.
#   The free-form fields are replaced with a fixed placeholder.
FINGERPRINT_SAFE_SHAPE = (
    "status", "fingerprint", "key_sha256_first_12", "key_length",
    "env_sync_path", "field", "actual_type",
)
FINGERPRINT_FREE_FORM = ("error",)

# ANIM-18 r7 F-2 fix: each safe-shape field's VALUE must also match a strict
# shape — name-only allowlisting let a tampered resolver inject the raw key
# string into a permitted field name (e.g. "status": "<raw_key>"). When no
# resolved key is in scope, _seal_outward() has nothing to scrub against, so
# the validators here are the last line of defense. Validators are tight: the
# legitimate values used by ANIM-17 resolve_env_key_from_env_sync() + this
# shim are short, ASCII-only, and structurally narrow.
_STATUS_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,63}$")
_FINGERPRINT_RE = re.compile(r"^[A-Za-z0-9]{1,16}:[A-Za-z0-9]{1,16}$")
_HEX12_RE = re.compile(r"^[a-f0-9]{12}$")
_FIELD_NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]{0,63}$")
# env_sync_path is either a Windows / POSIX JSON path or the literal
# "<sentinel>" used by P12-P17 probes. Path body restricted to filesystem
# characters; JSON suffix required so an attacker-supplied free-form string
# cannot match (a raw key has neither a `.json` suffix nor the bracket form).
_ENV_SYNC_PATH_RE = re.compile(
    r"^(?:<sentinel>|[A-Za-z]?:?[/\\]?[\w\-./\\: ]{1,255}\.json)$")
# Python type names from type(x).__name__: simple identifiers, optionally
# dotted (e.g. 'NoneType', 'collections.OrderedDict'). Bounded to 32 chars.
_ACTUAL_TYPE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]{0,31}$")


def _validate_safe_shape(name: str, value) -> bool:
    """Return True iff `value` matches the strict shape contract for `name`."""
    if name == "status":
        return isinstance(value, str) and bool(_STATUS_RE.match(value))
    if name == "fingerprint":
        return isinstance(value, str) and bool(_FINGERPRINT_RE.match(value))
    if name == "key_sha256_first_12":
        return isinstance(value, str) and bool(_HEX12_RE.match(value))
    if name == "key_length":
        return isinstance(value, int) and not isinstance(value, bool) \
               and 0 <= value <= 1024
    if name == "env_sync_path":
        return isinstance(value, str) and bool(_ENV_SYNC_PATH_RE.match(value))
    if name == "field":
        return isinstance(value, str) and bool(_FIELD_NAME_RE.match(value))
    if name == "actual_type":
        return isinstance(value, str) and bool(_ACTUAL_TYPE_RE.match(value))
    return False


def fingerprint_only(probe: dict) -> dict:
    """Project a probe dict down to a fixed set of safe diagnostic fields.

    ANIM-18 r4 F-1 fix: previous implementation was a denylist that only
    dropped a top-level "key" field. A resolver that emitted the raw key in
    any other field name, nested position, or as a dict-key would have
    leaked through. This is now an allowlist: only the documented safe
    diagnostic fields survive.

    ANIM-18 r6 F-1 fix: free-form fields like "error" are still capable of
    carrying attacker-controlled / tampered-resolver content, and when the
    resolver returns no usable `key` (status != OK), the outward sealing
    pass has nothing to scrub against. Replace any free-form field with a
    fixed placeholder; the structured `status` enum already carries the
    failure category, so the suppressed `error` text is information that
    operators can recover from the live resolver call directly (it is never
    silently dropped — only kept out of the persisted result).

    ANIM-18 r7 F-2 fix: field-name allowlisting alone was insufficient — a
    tampered resolver could still stuff the raw key into a permitted field
    NAME (e.g. emit `{"status": "<raw_key>"}`). When the resolver returns
    no `key`, `_seal_outward()` no-ops because it has nothing to scrub
    against. Each safe-shape field now also has a VALUE-shape validator
    (regex / type / length bound). Values that fail their validator are
    replaced with the same suppression placeholder.
    """
    out = {}
    for k in FINGERPRINT_SAFE_SHAPE:
        if k not in probe:
            continue
        out[k] = probe[k] if _validate_safe_shape(k, probe[k]) \
                          else "<suppressed-by-fingerprint_only>"
    for k in FINGERPRINT_FREE_FORM:
        if k in probe:
            out[k] = "<suppressed-by-fingerprint_only>"
    return out


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


def _seal_outward(result: dict, key_probe: dict | None) -> dict:
    """ANIM-18 r4 F-1 fix: apply _redact_key_from_obj() as a final-sealing
    pass on every outward-bound result that could have touched the resolved
    key, regardless of mode (probe / build_payload / submit dry-run / submit
    live / poll). The raw_key is pulled from the probe dict if present;
    otherwise the resolved key was never in scope and no scrubbing is needed.
    """
    raw = None
    if isinstance(key_probe, dict):
        v = key_probe.get("key")
        if isinstance(v, str) and v:
            raw = v
    return _redact_key_from_obj(result, raw)


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
        return _seal_outward(
            {"status": "FAL_KEY_UNRESOLVED",
             "key_resolution": fingerprint_only(key_probe)},
            key_probe)
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
    return _seal_outward(
        {"status": "PAYLOAD",
         "payload": payload,
         "key_fingerprint": fingerprint_only(key_probe),
         "submit_url": SUBMIT_URL},
        key_probe)


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
    # ANIM-18 r7 F-1 fix: Authorization is added via add_unredirected_header()
    # so even if the no-redirect opener were bypassed, the credential header
    # is dropped on redirected requests. Other headers (Content-Type) go
    # through add_header() as before.
    auth_value = headers.pop("Authorization", None)
    for k, v in headers.items():
        req.add_header(k, v)
    if auth_value is not None:
        req.add_unredirected_header("Authorization", auth_value)
    try:
        with _urlopen(req, timeout=timeout) as resp:
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
    # Resolve once so we have a raw_key for the dry-run sealing pass even
    # though no HTTP is made. (resolve_fal_key already executed inside
    # build_payload; this second call is the same OK probe and is cheap.)
    key_probe_for_seal = resolve_fal_key()
    if not live:
        return _seal_outward(
            {"status": "DRY_RUN",
             "note": "DRY-RUN — no HTTP call made. Pass --live to actually submit.",
             "submit_url": SUBMIT_URL,
             "payload_sha256": hashlib.sha256(body).hexdigest(),
             "payload": payload,
             "key_fingerprint": built["key_fingerprint"]},
            key_probe_for_seal)
    key_probe = resolve_fal_key()
    if key_probe.get("status") != "OK":
        return _seal_outward(
            {"status": "FAL_KEY_UNRESOLVED",
             "key_resolution": fingerprint_only(key_probe)},
            key_probe)
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
        return _seal_outward(
            {"status": "FAL_KEY_UNRESOLVED",
             "key_resolution": fingerprint_only(key_probe)},
            key_probe)
    url = POLL_URL_TEMPLATE.format(job_id=job_id)
    raw_key = key_probe["key"]
    req = urllib.request.Request(url, method="GET")
    # ANIM-18 r7 F-1 fix: Authorization as unredirected header — dropped on
    # any 30x redirect (defense in depth alongside _no_redirect_opener()).
    req.add_unredirected_header("Authorization", f"Key {raw_key}")
    # ANIM-18 r3 F-1 fix: poll_job applies a final _redact_key_from_obj()
    # pass on the result before return. Defined as a small inner wrapper to
    # keep the early-return branches DRY.
    def _seal(result: dict) -> dict:
        return _redact_key_from_obj(result, raw_key)
    try:
        with _urlopen(req, timeout=DEFAULT_TIMEOUT_SECONDS) as resp:
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
    # ANIM-18 r7 F-3 fix: guard cfg type before `.get()`. A non-dict FalCloud
    # entry previously crashed here; now it falls through with empty cfg and
    # the structured key_probe status carries TIER_CONFIG_INVALID_SHAPE.
    cfg_raw = load_tier_config().get("tiers", {}).get("FalCloud")
    cfg = cfg_raw if isinstance(cfg_raw, dict) else {}
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
    return _seal_outward(out, key_probe)


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
