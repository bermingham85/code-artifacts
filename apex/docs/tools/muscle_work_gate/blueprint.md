# BLUEPRINT - muscle_work_gate

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00029 |
| **Tool Name** | muscle_work_gate |
| **File** | `registry/muscle_work_gate.py` |
| **Category** | governance |
| **Version** | 1.0 |
| **Author** | MB / SYS |
| **Created** | 2026-05-26 |
| **Status** | APPROVED |

## Purpose

Runs an authority preflight before repository work, fallback work, or artifact promotion. It prevents agents from treating stale local files as source of truth by checking the Git branch, upstream state, protected branches, dirty working tree, and Apex authority manifest.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--repo` | path | no | Repository/workspace path to inspect. Defaults to current directory. |
| `--project` | string | no | Project label for audit output. Defaults to `APEX`. |
| `--mode` | enum | no | `normal`, `fallback`, or `auto`. Defaults to `auto`. |
| `--intent` | enum | no | `read`, `write`, or `promote`. Defaults to `write`. |
| `--fetch` | flag | no | Runs `git fetch --all --prune` before checking. Required for promotion. |
| `--allow-dirty` | flag | no | Allows write-mode continuation after dirty worktree review. Does not allow dirty promotion. |
| `--no-audit` | flag | no | Suppresses audit report writing. |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | JSON | Gate result with status, blockers, warnings, permissions, and required route. |
| file | JSON | Audit report under `audit/work_gate/` unless `--no-audit` is used. |

## How It Works

1. Reads `docs/APEX_AUTHORITY_MANIFEST.json`.
2. Inspects the repository with Git.
3. Optionally fetches remotes.
4. Blocks protected-branch writes, stale promotion, and unreviewed dirty worktrees.
5. Marks fallback work as provisional until promotion passes.
6. Writes a durable audit record for later review.

## Limitations

- It cannot prove remote freshness unless `--fetch` succeeds.
- It does not itself create branches or pull requests.
- It does not move artifacts from inbox to canonical storage; it gates the decision.

## Calling Convention

```json
{
  "sop": {
    "action": "muscle_work_gate",
    "params": {
      "repo": ".",
      "intent": "write",
      "fetch": true
    }
  },
  "qa": {
    "rule": "JSON_FIELD_NOT_EQUALS",
    "target": "status",
    "value": "BLOCK"
  }
}
```
