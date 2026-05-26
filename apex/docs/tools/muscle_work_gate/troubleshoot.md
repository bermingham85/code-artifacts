# TROUBLESHOOT - muscle_work_gate

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-DOC-00034 |
| **Version** | 1.0 |
| **Status** | ACTIVE |

## Known Failures

| Symptom | Likely Cause | Fix | Verification |
|---|---|---|---|
| `repo path is not a git repository` | Tool was run from the wrong folder | Pass `--repo C:/path/to/repo` | Rerun and confirm `repo.is_git_repo` is true |
| `promotion requires a successful remote fetch/latest check` | Promotion run did not use `--fetch` or network failed | Rerun with `--fetch`; if offline, keep work provisional | Status is not `BLOCK` for promotion |
| `current branch is protected` | Agent is on `main`/`master` | Create a `codex/*` or `agent/*` branch | Rerun gate and confirm blocker clears |
| `working tree is dirty` | Existing local or user work is present | Inspect changes; continue with `--allow-dirty` only for write-mode, never promotion | Gate reports write route without dirty blocker |

## Reusable Fix Log

No reusable fixes recorded yet.
