# Apex Work Gate

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00031 |
| Version | 1.0 |
| Status | ACTIVE |
| Purpose | Enforced preflight for normal and fallback work so agents cannot treat stale local files as authority |

## Authority Model

| Area | Authority |
|---|---|
| Committed code | GitHub protected branch and accepted pull requests |
| Local shared artifacts | `X:/Apex/Canonical` plus manifest/index records |
| New non-code outputs | `X:/Apex/Inbox/<station>` until promoted |
| Machine-local files | Working state only; not durable truth |

## Required Gate

Before modifying a repository or promoting artifacts, run:

```bash
python registry/muscle_work_gate.py --repo . --intent write --fetch
```

If the gate blocks because local work already exists, inspect it first. Only then rerun with:

```bash
python registry/muscle_work_gate.py --repo . --intent write --fetch --allow-dirty
```

For fallback work when the GPU or main station is unavailable:

```bash
python registry/muscle_work_gate.py --repo . --mode fallback --intent write --fetch
```

Before anything becomes official:

```bash
python registry/muscle_work_gate.py --repo . --intent promote --fetch
```

## Agent Rule

Agents may continue work in fallback mode, but the work is provisional. A blocked or warning gate result is not permission to overwrite canonical X folders, push protected branches, or declare local files official.

## Safe Routes

| Situation | Route |
|---|---|
| Normal code work | Task branch, local commit, PR or approved branch push |
| Fallback code work | Task branch, provisional work, promotion gate before merge |
| Non-code artifact | Save to X inbox, hash/index, promote to canonical folder |
| Stale or unknown copy | Stop official promotion, reconcile against GitHub and manifest |

## Hard Boundaries

- Do not write directly to protected branches.
- Do not overwrite `X:/Apex/Canonical` directly.
- Do not decide source of truth by timestamp alone.
- Do not scan every C drive looking for "latest" unless the manifest/gate says the work was never promoted.
- Do not treat a successful edit as official until the promotion or merge gate passes.
- Do not use `--allow-dirty` until existing local changes have been reviewed.
