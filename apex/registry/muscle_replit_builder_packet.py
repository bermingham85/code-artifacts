"""
muscle_replit_builder_packet.py - Replit Builder Packet Muscle
Ref:        APEX-MB-PY-00024
Version:    1.0
Author:     MB / SYS
Description: Converts Claude-style build instructions into a Replit Agent
             handoff packet with prompt, manifest, and audit status files.
Inputs:     --instruction TEXT, --instruction-file PATH, --input PATH
Outputs:    JSON on stdout and files under audit/replit_builder/<packet_id>/.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import uuid
from pathlib import Path
from typing import Any


APEX_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT_DIR = APEX_ROOT / "audit" / "replit_builder"
MAX_INLINE_CHARS = 80_000


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(value: str, fallback: str = "replit-build") -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return (slug or fallback)[:64]


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_text_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Input path is not a file: {path}")
    return path.read_text(encoding="utf-8", errors="replace")


def compact_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def extract_instruction_from_json(path: Path, data: dict[str, Any]) -> str:
    """Best-effort extraction from WorkOrder-like JSON or arbitrary packet JSON."""
    if isinstance(data.get("instruction"), str):
        return data["instruction"]
    if isinstance(data.get("claude_instruction"), str):
        return data["claude_instruction"]
    if isinstance(data.get("prompt"), str):
        return data["prompt"]

    sop = data.get("sop")
    if isinstance(sop, dict):
        parts = []
        action = sop.get("action")
        if action:
            parts.append(f"Requested Apex action: {action}")
        inputs = sop.get("inputs")
        if inputs:
            parts.append(f"Inputs: {compact_json(inputs)}")
        params = sop.get("parameters")
        if params:
            parts.append(f"Parameters: {compact_json(params)}")
        if parts:
            return "\n\n".join(parts)

    return f"JSON source from {path}:\n\n{compact_json(data)}"


def collect_instruction_parts(args: argparse.Namespace) -> tuple[str, list[dict[str, str]]]:
    parts: list[str] = []
    sources: list[dict[str, str]] = []

    if args.instruction:
        parts.append(args.instruction.strip())
        sources.append({"type": "inline", "value": "cli:--instruction"})

    for raw in args.instruction_file or []:
        path = Path(raw).expanduser()
        text = read_text_file(path)
        parts.append(text.strip())
        sources.append({"type": "instruction_file", "value": str(path)})

    for raw in args.input or []:
        path = Path(raw).expanduser()
        text = read_text_file(path)
        if path.suffix.lower() == ".json":
            try:
                extracted = extract_instruction_from_json(path, json.loads(text))
                parts.append(extracted.strip())
            except json.JSONDecodeError:
                parts.append(text.strip())
        else:
            parts.append(text.strip())
        sources.append({"type": "input", "value": str(path)})

    instruction = "\n\n---\n\n".join(part for part in parts if part).strip()
    if not instruction:
        raise ValueError("No build instruction supplied. Use --instruction, --instruction-file, or --input.")
    if len(instruction) > MAX_INLINE_CHARS:
        raise ValueError(f"Instruction is {len(instruction)} chars; max is {MAX_INLINE_CHARS}. Split the task first.")
    return instruction, sources


def build_replit_prompt(
    packet_id: str,
    title: str,
    mode: str,
    app_stack: str,
    project: str,
    target_repo: Path,
    instruction: str,
) -> str:
    return f"""# Replit Builder Packet: {title}

Packet ID: {packet_id}
Project: {project}
Mode: {mode}
Preferred app stack: {app_stack}
Source repo context: {target_repo}

You are Replit Agent acting as the core code builder for this Apex task.

## External Research Rule

Use Perplexity Pro first for external research; keep web/source reads targeted.

If Perplexity Pro is unavailable inside Replit, say so in the build notes and use official or primary sources where possible. Do not paste private repo code, credentials, tokens, or secrets into external research tools.

## Claude Build Instruction

{instruction}

## Builder Contract

1. Build exactly what the Claude instruction requests.
2. Keep implementation complete enough to run, inspect, and iterate in Replit.
3. Do not invent real credentials. Use environment variables and safe placeholders.
4. Preserve user data and existing app behavior unless the instruction explicitly changes it.
5. If the task is too broad, split it into a small working vertical slice first and list the next slices.
6. Prefer ordinary, maintainable project structure over clever abstractions.
7. Add or update tests/checks when there is meaningful behavior to protect.
8. At the end, provide a concise build report with changed areas, run steps, test results, and any blocked items.

## Return To Apex

When the Replit build is done, return:
- Replit app URL or repo URL
- Build summary
- Changed files or generated modules
- Commands/tests run
- Open risks or missing credentials
- Any follow-up instruction Claude should review
"""


def write_packet(args: argparse.Namespace) -> dict[str, Any]:
    instruction, sources = collect_instruction_parts(args)
    target_repo = Path(args.target_repo).expanduser().resolve()
    title = args.title or instruction.splitlines()[0][:72] or "Replit build"
    packet_id = f"{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d-%H%M%S')}-{slugify(title)}-{uuid.uuid4().hex[:8]}"
    out_root = Path(args.out_dir).expanduser()
    out_dir = out_root / packet_id
    out_dir.mkdir(parents=True, exist_ok=True)

    prompt = build_replit_prompt(
        packet_id=packet_id,
        title=title,
        mode=args.mode,
        app_stack=args.app_stack,
        project=args.project,
        target_repo=target_repo,
        instruction=instruction,
    )

    manifest = {
        "status": "OK",
        "packet_id": packet_id,
        "created_at": utc_now(),
        "title": title,
        "project": args.project,
        "mode": args.mode,
        "app_stack": args.app_stack,
        "target_repo": str(target_repo),
        "sources": sources,
        "instruction_sha256": sha256_text(instruction),
        "prompt_sha256": sha256_text(prompt),
        "files": {
            "prompt": str(out_dir / "replit_prompt.md"),
            "manifest": str(out_dir / "packet.json"),
            "status": str(out_dir / "status.json"),
        },
        "handoff": {
            "preferred": "Open the generated prompt in Replit Agent or pass it through an approved Replit connector.",
            "connector_note": "The Codex Replit connector can create or update apps from natural-language prompts, but local scripts do not receive direct Replit account credentials.",
        },
    }

    (out_dir / "replit_prompt.md").write_text(prompt, encoding="utf-8")
    (out_dir / "packet.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (out_dir / "status.json").write_text(json.dumps({"status": "READY_FOR_REPLIT", **manifest}, indent=2), encoding="utf-8")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a Replit Agent build packet from Claude instructions.")
    parser.add_argument("--task-folder", default="", help="Foreman task folder; accepted for muscle compatibility.")
    parser.add_argument("--input", action="append", default=[], help="Input file. Repeatable. JSON WorkOrders are summarized.")
    parser.add_argument("--instruction", default="", help="Inline Claude build instruction.")
    parser.add_argument("--instruction-file", action="append", default=[], help="File containing Claude build instruction. Repeatable.")
    parser.add_argument("--title", default="", help="Human-readable packet title.")
    parser.add_argument("--project", default="APEX", help="Project code to include in the packet.")
    parser.add_argument("--mode", choices=["create", "update", "inspect"], default="create", help="Replit operation mode.")
    parser.add_argument("--app-stack", choices=["react_website", "mobile_app", "generic"], default="react_website", help="Preferred Replit app stack.")
    parser.add_argument("--target-repo", default=str(APEX_ROOT), help="Local repo context for the handoff notes.")
    parser.add_argument("--out-dir", default=str(DEFAULT_OUT_DIR), help="Packet output root.")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        result = write_packet(build_parser().parse_args(argv))
        print(json.dumps({"status": "OK", "packet_id": result["packet_id"], "output": result["files"]["prompt"]}))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
