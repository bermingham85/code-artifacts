#!/usr/bin/env python3
"""Read-only Supabase project boundary guard.

This helper verifies that an automation target project exists and is not a
protected project. It also requires an explicit marker proving the shared
Supabase boundary policy was loaded before write-oriented use. It never prints
Supabase key values.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request


DEFAULT_PROJECT_REF = "ylcepmvbjjnwmzvevxid"
DEFAULT_KEY_NAMES = (
    "SUPABASE_SERVICE_ROLE_KEY",
    "SUPABASE_SERVICE_KEY",
    "SUPABASE_KEY",
)
BOUNDARY_DOC_MARKER = "APEX-MB-DOC-00038-v1.0"
DEFAULT_FORBID_CODES = ("AGEN", "BERM", "FINX", "JESS", "MILK", "TALE", "BPIG")
DEFAULT_SHARED_CODES = ("INFR", "GOVN", "GNRL")


def boundary_doc_acknowledged() -> bool:
    return os.environ.get("APEX_BOUNDARY_DOC_READ") == BOUNDARY_DOC_MARKER


def env_key() -> tuple[str, str]:
    for name in DEFAULT_KEY_NAMES:
        value = os.environ.get(name)
        if value:
            return name, value
    raise SystemExit("No Supabase API key found in approved environment variables.")


def supabase_url(project_ref: str) -> str:
    value = os.environ.get("SUPABASE_URL")
    if value:
        return value.rstrip("/")
    return f"https://{project_ref}.supabase.co"


def get_json(url: str, key: str, path: str) -> list[dict]:
    req = urllib.request.Request(
        f"{url}/rest/v1/{path}",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        body = response.read().decode("utf-8")
    if not body:
        return []
    parsed = json.loads(body)
    if isinstance(parsed, list):
        return parsed
    return [parsed]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expect-code", default="APEX")
    parser.add_argument("--forbid-code", action="append", default=list(DEFAULT_FORBID_CODES))
    parser.add_argument("--shared-code", action="append", default=list(DEFAULT_SHARED_CODES))
    parser.add_argument(
        "--allow-shared",
        action="store_true",
        help="Acknowledge that this target is shared infrastructure with explicit work-order approval.",
    )
    parser.add_argument("--project-ref", default=DEFAULT_PROJECT_REF)
    args = parser.parse_args()

    if not boundary_doc_acknowledged():
        result = {
            "ok": False,
            "expect_code": args.expect_code,
            "boundary_doc_marker": "MISSING_OR_STALE",
            "required_boundary_doc_marker": BOUNDARY_DOC_MARKER,
            "required_doc": "docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md",
            "secrets_printed": False,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 5

    key_name, key = env_key()
    base_url = supabase_url(args.project_ref)
    codes = sorted(set([args.expect_code] + args.forbid_code + args.shared_code))
    encoded_codes = ",".join(urllib.parse.quote(code, safe="") for code in codes)
    rows = get_json(
        base_url,
        key,
        f"agent_projects?select=id,code,name,status&code=in.({encoded_codes})",
    )

    by_code = {row.get("code"): row for row in rows}
    expected = by_code.get(args.expect_code)
    protected = {code: by_code.get(code) for code in args.forbid_code if by_code.get(code)}
    shared = {code: by_code.get(code) for code in args.shared_code if by_code.get(code)}
    shared_blocked = args.expect_code in args.shared_code and not args.allow_shared

    result = {
        "ok": bool(expected) and args.expect_code not in args.forbid_code and not shared_blocked,
        "target": expected,
        "protected_projects_present": protected,
        "shared_projects_present": shared,
        "expect_code": args.expect_code,
        "forbid_code": args.forbid_code,
        "shared_code": args.shared_code,
        "allow_shared": args.allow_shared,
        "boundary_doc_marker": BOUNDARY_DOC_MARKER,
        "auth_env_name": key_name,
        "secrets_printed": False,
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    if not expected:
        return 2
    if args.expect_code in args.forbid_code:
        return 3
    if shared_blocked:
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
