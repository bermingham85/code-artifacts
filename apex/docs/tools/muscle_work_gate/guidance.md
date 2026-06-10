# GUIDANCE - muscle_work_gate

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00029 |
| **Version** | 1.0 |

## When to Use

- Before any agent edits a repository.
- When continuing work from a laptop or fallback station.
- Before promoting inbox artifacts to canonical X storage.
- Before claiming local work is current with GitHub.
- After finding multiple stale copies of the same project.

## How to Call

```bash
# Normal preflight before code edits
python registry/muscle_work_gate.py --repo . --intent write --fetch

# Fallback/degraded mode when GPU/main station is unavailable
python registry/muscle_work_gate.py --repo . --mode fallback --intent write --fetch

# Continue after explicitly reviewing existing local changes
python registry/muscle_work_gate.py --repo . --intent write --fetch --allow-dirty

# Promotion gate before anything becomes official
python registry/muscle_work_gate.py --repo . --intent promote --fetch
```

## Result Meaning

| Status | Meaning |
|---|---|
| `OK` | No blockers or warnings found. Follow the required route. |
| `WARN` | Work may continue cautiously, usually as provisional fallback work. |
| `BLOCK` | Do not promote or perform official writes until blockers are resolved. |

## Agent Handling Rule

If the gate returns `BLOCK`, the agent may only create a task branch, write to an inbox/provisional area, or ask for operator approval. It must not overwrite canonical X folders or push protected branches.

Normal write mode requires a successful remote fetch/latest check. Fallback mode may continue provisionally when remote freshness cannot be proven, but only through a task branch or inbox route and never as official promotion.

## Common Mistakes

- Running without `--fetch` and then claiming the repo is current.
- Treating fallback work as official before a promotion run.
- Using `--allow-dirty` without reviewing existing local changes.
- Resolving conflicts by timestamp only.
- Searching every C drive instead of using the manifest and Git remote.
