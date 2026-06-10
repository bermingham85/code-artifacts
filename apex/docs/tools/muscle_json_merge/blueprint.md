# BLUEPRINT — muscle_json_merge

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00006 |
| **Tool Name** | muscle_json_merge |
| **Category** | data |
| **Version** | 1.0 |
| **Status** | APPROVED |

## Purpose

Deep-merges two or more JSON files into one. Last file wins on key conflicts.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--inputs` | paths | yes | Comma-separated JSON file paths |
| `--output` | path | yes | Output merged JSON file |

## Outputs

stdout: `{"status": "OK", "output": "<path>"}`. Merged JSON written to --output.

## Limitations

- Arrays are replaced (not merged/appended) by the later file
- All inputs must be valid JSON
