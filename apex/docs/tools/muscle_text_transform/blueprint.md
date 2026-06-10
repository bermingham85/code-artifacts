# BLUEPRINT — muscle_text_transform

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00005 |
| **Tool Name** | muscle_text_transform |
| **File** | `registry/muscle_text_transform.py` |
| **Category** | data |
| **Version** | 1.0 |
| **Status** | APPROVED |

## Purpose

Applies a text transformation operation to a file: uppercase, lowercase, strip whitespace, find-replace, or word count.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--input` | path | yes | Source text file |
| `--output` | path | yes | Output file path |
| `--operation` | string | yes | `upper` \| `lower` \| `strip` \| `replace` \| `word_count` |
| `--find` | string | if replace | String to find |
| `--replace` | string | if replace | Replacement string |

## Outputs

stdout: `{"status": "OK", "output": "<path>"}` or `{"status": "OK", "result": <int>}` for word_count

## Limitations

- Text files only (UTF-8), not binary
- `replace` is simple string replace, not regex
- `word_count` prints count to stdout, does not write file
