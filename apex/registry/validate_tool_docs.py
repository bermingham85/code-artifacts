"""
validate_tool_docs.py - Apex Tool Documentation Validator
Ref:        APEX-MB-PY-00026
Version:    1.0
Author:     MB / SYS
Description: Validates that approved tools have menu, docs, troubleshoot, register,
             manifest, and TOOL_INDEX coverage.
Inputs:     --root PATH   Apex repo root
            --quiet       Suppress human-readable details
Outputs:    JSON status on stdout. Exit 0 clean, 1 violations.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


APEX_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_DOCS = ("blueprint.md", "guidance.md", "test_record.md", "troubleshoot.md")
APPROVED_RE = re.compile(r"\bApproved\b[^\n]*\bYES\b", re.IGNORECASE)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_register_refs(root: Path) -> str:
    return (root / "docs" / "DOCUMENT_REGISTER.md").read_text(encoding="utf-8", errors="replace")


def approved_manifest_tools(root: Path) -> dict[str, dict]:
    manifest = load_json(root / "registry" / "manifest.json")
    out: dict[str, dict] = {}
    for skill in manifest.get("skills", []):
        name = skill.get("name")
        if name and skill.get("callable_as_muscle") and skill.get("approved"):
            out[name] = skill
    for tool in manifest.get("approved_tools", []):
        name = tool.get("name")
        if name and tool.get("approved"):
            out[name] = tool
    return out


def validate(root: Path) -> tuple[bool, list[dict]]:
    findings: list[dict] = []
    menu = load_json(root / "docs" / "APEX_TOOL_MENU.json")
    menu_tools = {tool["name"]: tool for tool in menu.get("approved_tools", [])}
    manifest_tools = approved_manifest_tools(root)
    tool_index = (root / "registry" / "TOOL_INDEX.md").read_text(encoding="utf-8", errors="replace")
    register = parse_register_refs(root)

    for name, meta in sorted(manifest_tools.items()):
        tool_dir = root / "docs" / "tools" / name
        if name not in menu_tools:
            findings.append({"tool": name, "issue": "missing from docs/APEX_TOOL_MENU.json"})
        if f"`{name}`" not in tool_index:
            findings.append({"tool": name, "issue": "missing from registry/TOOL_INDEX.md"})
        if name not in register:
            findings.append({"tool": name, "issue": "missing from docs/DOCUMENT_REGISTER.md"})
        for doc in REQUIRED_DOCS:
            path = tool_dir / doc
            if not path.is_file():
                findings.append({"tool": name, "issue": f"missing {doc}"})
        test_record = tool_dir / "test_record.md"
        if test_record.is_file():
            text = test_record.read_text(encoding="utf-8", errors="replace")
            if not APPROVED_RE.search(text):
                findings.append({"tool": name, "issue": "test_record.md lacks Approved: YES"})

    for name in sorted(menu_tools):
        if name not in manifest_tools:
            findings.append({"tool": name, "issue": "menu lists tool not approved in manifest"})

    return not findings, findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Apex approved tool docs.")
    parser.add_argument("--root", default=str(APEX_ROOT))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    ok, findings = validate(root)
    result = {"status": "OK" if ok else "ERROR", "findings": findings}
    print(json.dumps(result, indent=None if args.quiet else 2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
