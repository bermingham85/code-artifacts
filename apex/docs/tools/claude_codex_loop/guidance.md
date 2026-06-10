# GUIDANCE - claude_codex_loop

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00023 |
| **Version** | 1.0 |

## When to Use

- Agent or spec work where a Codex review gate is mandated.
- Any APEX phase whose Task Packet says "review required" or "no Claude self-review."
- Multi-iteration work where Codex's first read is expected to find issues (e.g. AGEN-* implementations).
- Doctrine or schema migrations that need an independent second pass before commit.

## Do Not Use

- For quick fixes or trivial doc changes — overhead is high.
- For builds where you want manual human review between iterations — this loop is fully automated up to `--max-attempts`.
- For tasks that should NOT be retried on failure — pass `--max-attempts 1` instead.
- As an alternative to writing a clear initial prompt. Garbage-in: Claude will burn 5 attempts confused. Get the prompt right before invoking.
- When the repo has unreviewed uncommitted changes. The work gate blocks this by default; inspect first, then use `--allow-dirty-work-gate` only if continuation is intentional.

## How to Call

Minimal:
```powershell
python registry/claude_codex_loop.py `
  --prompt-file docs/spec/your_build.md `
  --phase YOUR-PHASE-001
```

The loop runs `muscle_work_gate` before Claude starts. If local changes already exist, inspect them first and then use:

```powershell
python registry/claude_codex_loop.py `
  --prompt-file docs/spec/your_build.md `
  --phase YOUR-PHASE-001 `
  --allow-dirty-work-gate
```

Do not pass `--allow-x-apex` unless the task explicitly needs Claude to access the shared X Apex estate. Normal code work should stay inside the repo workspace.

Common production pattern (bounded, faster):
```powershell
python registry/claude_codex_loop.py `
  --prompt-file docs/spec/AGEN-spec-agent-v1.md `
  --phase AGEN-spec-agent `
  --max-attempts 3 `
  --builder-timeout-minutes 45 `
  --reviewer-timeout-minutes 20
```

Force certain files into every review (e.g. spec the build must comply with):
```powershell
python registry/claude_codex_loop.py `
  --prompt-file docs/spec/migration.md `
  --phase AGEN-migration-coordinator `
  --review-path docs/spec/migration.md `
  --review-path registry/migrations/
```

## Example SIGNED_OFF.json (truncated)

```json
{
  "phase": "AGEN-migration-coordinator",
  "prompt_file": "docs/spec/migration.md",
  "repo": "C:\\Users\\Owner\\Repos\\code-artifacts",
  "started": "2026-05-22T11:14:02Z",
  "completed": "2026-05-22T12:08:31Z",
  "status": "signed_off",
  "attempts": [
    {
      "attempt": 1,
      "builder_returncode": 0,
      "builder_log": "audit/claude_codex_loop/AGEN-migration-coordinator/attempt_01_claude_builder.txt",
      "changed_files": ["..."],
      "reviewed_files": ["..."],
      "reviewer_returncode": 1,
      "reviewer_log": "audit/claude_codex_loop/AGEN-migration-coordinator/attempt_01_codex_review.txt"
    },
    {
      "attempt": 2,
      "builder_returncode": 0,
      "reviewer_returncode": 0,
      "reviewer_log": "audit/claude_codex_loop/AGEN-migration-coordinator/attempt_02_codex_review.txt"
    }
  ]
}
```
Exit code: 0.

## Example LOOP_FAILED.json (truncated)

```json
{
  "phase": "AGEN-architecture-agent-post-migration",
  "status": "reviewer_failed",
  "attempts": [
    {
      "attempt": 1,
      "builder_returncode": 0,
      "reviewer_returncode": 2
    }
  ],
  "completed": "2026-05-22T18:42:11Z"
}
```
Exit code: 1.

## Reading the Audit Tree

For a given `<phase>` directory:
- `attempt_01_claude_builder.txt` — full Claude stdout/stderr for attempt 1.
- `attempt_01_changed_files.json` — exactly what changed + what was reviewed.
- `attempt_01_codex_review.txt` — Codex review output (the bridge between attempts).
- `attempt_02_*` — same shape for attempt 2 (only if attempt 1 didn't sign off).
- Final file = `SIGNED_OFF.json` OR `LOOP_FAILED.json`.

Do NOT require future contexts to read the whole audit tree — link only the latest SIGNED_OFF / LOOP_FAILED in your WorkOrder evidence section.

## Cost Awareness

The loop spends subscription tokens, not API credits, but it can still burn substantial wall-clock time and quota:
- Worst case = `max-attempts × (builder-timeout + reviewer-timeout)`. Default = `5 × (120 + 60) = 900 min` = 15 hours.
- Each attempt does a full repo snapshot (cheap on SSD, expensive on slow NAS — keep `--repo` local).
- Codex reviewer reads every file in `to_review`. Large diffs = larger Codex prompt.

Tune `--max-attempts`, the timeouts, and prompt scope deliberately.

## Recovery / Rollback

If the loop ended with `LOOP_FAILED.json`:
1. Read the final `attempt_NN_codex_review.txt` — Codex's last verdict tells you what went wrong.
2. Repo is in post-build state (loop does NOT auto-roll-back). Inspect with `git diff` / `git status`.
3. Decide: `git restore` to throw away, OR keep the partial work and fix manually.
4. To re-run from scratch with the same phase label, the loop will OVERWRITE attempt files (it doesn't preserve prior failed runs under the same phase). Rename the old phase dir if you want to keep both.

## Common Mistakes

- Running with default `--max-attempts 5` for a build that's likely to genuinely fail — burns 5 attempts before you find out.
- Forgetting `--review-path` for a spec file — Codex won't see it unless Claude touched it.
- Pointing `--repo` at a remote path (`\\192.168.50.246\...`) — snapshot SHA-256 over SMB is very slow.
- Re-running with the same `--phase` and getting confused which attempt belongs to which run. Use distinct phase labels per attempt (e.g. `MY-PHASE-001-retry-2`).
- Calling this for documentation-only edits — use direct Claude or Codex instead; the loop is for review-gated work.
