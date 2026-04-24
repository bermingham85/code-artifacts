# BLUEPRINT — muscle_file_copy

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00004 |
| **Tool Name** | muscle_file_copy |
| **File** | `registry/muscle_file_copy.py` |
| **Category** | files |
| **Version** | 1.0 |
| **Status** | APPROVED |

## Purpose

Copies a single file from a source path to a destination path. Creates destination directory if it does not exist.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--source` | path | yes | Source file (must exist) |
| `--dest` | path | yes | Destination file path |

## Outputs

stdout: `{"status": "OK", "output": "<dest>"}` or `{"status": "ERROR", "error": "..."}`

## Dependencies

Python 3.11+ stdlib only (shutil, pathlib).

## Limitations

- Single file only — no directory recursion, no glob patterns
- Does not preserve symlinks
- Overwrites destination if it exists (no --no-overwrite flag)

## Calling Convention

```json
{
  "sop": { "action": "muscle_file_copy", "params": { "source": "A", "dest": "B" } },
  "qa":  { "rule": "FILE_EXISTS", "target": "B" }
}
```
