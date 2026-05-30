#!/usr/bin/env python3
"""Read-only Supabase project boundary guard.

This helper verifies that an automation target project exists and is not a
protected project such as JESS. It never prints Supabase key values.
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
    parser.add_argument("--forbid-code", action="append", default=["JESS"])
    parser.add_argument("--project-ref", default=DEFAULT_PROJECT_REF)
    args = parser.parse_args()

    key_name, key = env_key()
    base_url = supabase_url(args.project_ref)
    codes = sorted(set([args.expect_code] + args.forbid_code))
    encoded_codes = ",".join(urllib.parse.quote(code, safe="") for code in codes)
    rows = get_json(
        base_url,
        key,
        f"agent_projects?select=id,code,name,status&code=in.({encoded_codes})",
    )

    by_code = {row.get("code"): row for row in rows}
    expected = by_code.get(args.expect_code)
    protected = {code: by_code.get(code) for code in args.forbid_code if by_code.get(code)}

    result = {
        "ok": bool(expected),
        "target": expected,
        "protected_projects_present": protected,
        "expect_code": args.expect_code,
        "forbid_code": args.forbid_code,
        "auth_env_name": key_name,
        "secrets_printed": False,
    }

    print(json.dumps(result, indent=2, sort_keys=True))
    if not expected:
        return 2
    if args.expect_code in args.forbid_code:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
