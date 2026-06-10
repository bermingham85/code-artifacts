"""
generate_tool_menu.py - Apex Tool Menu Generator
Ref:        APEX-MB-PY-00025
Version:    1.0
Author:     MB / SYS
Description: Generates docs/APEX_TOOL_MENU.md from docs/APEX_TOOL_MENU.json.
Inputs:     --input PATH      Menu JSON source
            --output PATH     Markdown menu output
Outputs:    JSON status on stdout.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


APEX_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = APEX_ROOT / "docs" / "APEX_TOOL_MENU.json"
DEFAULT_OUTPUT = APEX_ROOT / "docs" / "APEX_TOOL_MENU.md"


def esc(value: str) -> str:
    return value.replace("|", "\\|")


def generate(source: Path, output: Path) -> None:
    data = json.loads(source.read_text(encoding="utf-8"))
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data["generated_at"] = generated_at
    source.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# Apex Tool Menu",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Ref Code | APEX-MB-DOC-00012 |",
        f"| Version | {data.get('version', '1.0')} |",
        "| Status | ACTIVE |",
        "| Purpose | Low-token tool selection menu with current state, exact use path, and editable troubleshooting links |",
        f"| Generated | {generated_at} |",
        "",
        "## How To Use This Menu",
        "",
        "1. Pick the tool by outcome.",
        "2. If you only need the command, use the `Exact call` column.",
        "3. If you need safe usage detail, open that tool's `guidance.md`.",
        "4. If it fails, open that tool's `troubleshoot.md`.",
        "5. When a new fix is discovered, append it to the tool's `troubleshoot.md` under `Reusable Fix Log`.",
        "",
        "Do not load every tool document up front. This menu is the cover page. Load only the selected row's guidance or troubleshoot file.",
        "",
        "## Approved Tool Selection",
        "",
        "| Need | Tool | State | Exact call | How to | Troubleshoot |",
        "|---|---|---|---|---|---|",
    ]

    for tool in data.get("approved_tools", []):
        lines.append(
            "| {need} | `{name}` | {state} | `{call}` | `{how_to}` | `{troubleshoot}` |".format(
                need=esc(tool["need"]),
                name=tool["name"],
                state=tool["state"],
                call=esc(tool["exact_call"]),
                how_to=tool["how_to"],
                troubleshoot=tool["troubleshoot"],
            )
        )

    lines += [
        "",
        "## Pending Tool Queue",
        "",
        "These are not production-callable until their blueprint, guidance, test record, troubleshoot page, and approval status are complete.",
        "",
        "| Tool | State | Missing |",
        "|---|---|---|",
    ]

    for tool in data.get("pending_tools", []):
        lines.append(
            f"| `{tool['name']}` | {tool['state']} | `{', '.join(tool.get('missing', []))}` |"
        )

    lines += [
        "",
        "## Maintenance Rule",
        "",
        "When a tool fails and a reusable fix is found:",
        "",
        "1. Add the fix to `docs/tools/<tool>/troubleshoot.md`.",
        "2. Include date, symptom, likely cause, fix, verification command, and any prevention rule.",
        "3. Keep the fix short and operational.",
        "4. Commit the change so future contexts inherit the repair.",
        "",
        "## Source Of Truth",
        "",
        "| Need | Source |",
        "|---|---|",
        "| Approved callable tools | `registry/TOOL_INDEX.md` |",
        "| Artifact status and paths | `docs/DOCUMENT_REGISTER.md` |",
        "| Tool metadata | `registry/manifest.json` |",
        "| Machine-readable menu source | `docs/APEX_TOOL_MENU.json` |",
        "| Tool approval standard | `docs/NAMING_CONVENTION.md` |",
        "",
    ]

    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Apex tool menu markdown.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    source = Path(args.input)
    output = Path(args.output)
    generate(source, output)
    print(json.dumps({"status": "OK", "input": str(source), "output": str(output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
