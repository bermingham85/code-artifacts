# BLUEPRINT - muscle_replit_builder_packet

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00024 |
| **Tool Name** | muscle_replit_builder_packet |
| **File** | `registry/muscle_replit_builder_packet.py` |
| **Category** | ai |
| **Version** | 1.0 |
| **Author** | MB / SYS |
| **Created** | 2026-05-23 |
| **Status** | READY |

## Purpose

Creates a Replit Agent handoff packet from Claude-style build instructions. The packet lets Claude remain the planner and reviewer while Replit becomes the core code builder for app creation or iteration.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--instruction` | string | no | Inline Claude build instruction |
| `--instruction-file` | path | no | File containing Claude's instruction; repeatable |
| `--input` | path | no | Foreman-compatible input file; repeatable |
| `--mode` | enum | no | `create`, `update`, or `inspect` |
| `--app-stack` | enum | no | `react_website`, `mobile_app`, or `generic` |
| `--project` | string | no | Apex project code, default `APEX` |
| `--target-repo` | path | no | Local repo context to include in packet |
| `--out-dir` | path | no | Packet output root |

At least one of `--instruction`, `--instruction-file`, or `--input` is required.

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | JSON | `{"status": "OK", "packet_id": "...", "output": "<prompt path>"}` |
| `replit_prompt.md` | Markdown | Natural-language prompt for Replit Agent |
| `packet.json` | JSON | Packet metadata, source list, hashes, and file paths |
| `status.json` | JSON | Foreman-friendly ready status |

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Python 3.11+ | runtime | stdlib only |
| Replit Agent | external builder | Uses generated natural-language handoff |
| Claude/Codex doctrine | process | Prompt includes the Perplexity-first research rule for delegated external research |

## How It Works

1. Reads inline instructions, instruction files, or WorkOrder-like JSON inputs.
2. Normalizes the content into one Claude build instruction.
3. Writes a Replit Agent prompt with builder rules, security constraints, and return requirements.
4. Writes a JSON manifest with hashes and output paths for audit.
5. Prints a compact JSON result for Foreman and scripts.

## Limitations

- This tool does not call a private or undocumented Replit API.
- The generated prompt must be given to Replit Agent manually or through an approved Replit connector.
- Local scripts do not receive Replit account credentials.
- The tool packages instructions; it does not verify the Replit build output by itself.

## Calling Convention

```json
{
  "sop": {
    "action": "muscle_replit_builder_packet",
    "inputs": ["path/to/claude_instruction.md"],
    "parameters": {
      "mode": "create",
      "app-stack": "react_website",
      "project": "APEX"
    }
  },
  "qa_gate": {
    "rule": "FILE_EXISTS",
    "checks": [
      {
        "rule": "FILE_EXISTS",
        "target": "output.log"
      }
    ]
  }
}
```
