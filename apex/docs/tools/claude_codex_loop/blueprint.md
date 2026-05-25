# BLUEPRINT - claude_codex_loop

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00023 (already registered in DOCUMENT_REGISTER) |
| **Tool Name** | claude_codex_loop |
| **File** | `registry/claude_codex_loop.py` |
| **Category** | ai |
| **Version** | 1.0 |
| **Author** | MB / SYS |
| **Created** | 2026-05-22 |
| **Status** | APPROVED |

## Purpose

Automation loop that runs a prepared Claude build prompt, then invokes `codex_bridge.py` to review the changed files. If Codex rejects the build, the loop feeds Codex's findings back to Claude as a fix prompt and retries — until Codex signs off, the builder fails, or the attempt cap is reached.

The intended use is **multi-pass agentic work where independent reviewer sign-off is required**: agent specs, governance changes, schema migrations, anything that needs a Codex gate per APEX doctrine. It exists specifically to prevent the "Claude self-reviews its own code" anti-pattern (per APEX_PARALLEL_MERGE_PLAYBOOK: "no Claude self-review fallback when Codex review is required").

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--prompt-file` | path | yes | Markdown/text file containing the prepared Claude build prompt |
| `--phase` | string | yes | Phase / job label used for the audit subdirectory (e.g. `AGEN-spec-agent`) |
| `--repo` | path | no | APEX repo path to snapshot for change detection. Default: `cwd` |
| `--claude-cwd` | path | no | Working directory passed to the Claude subprocess. Default: `cwd` |
| `--x-apex` | path | no | Shared APEX estate path made readable to Claude via `--add-dir`. Default: `\\192.168.50.246\Extra\Automations\apex` |
| `--codex-bridge` | path | no | Path to `codex_bridge.py`. Default: `C:\Users\Owner\apex_governance\cc_runbook\codex_bridge.py` |
| `--out-dir` | path | no | Loop log root. Default: `audit/claude_codex_loop` |
| `--max-attempts` | int | no | Maximum Claude/Codex iterations. Default: `5` |
| `--builder-timeout-minutes` | int | no | Timeout per Claude build attempt. Default: `120` |
| `--reviewer-timeout-minutes` | int | no | Timeout per Codex review attempt. Default: `60` |
| `--review-path` | string (repeatable) | no | Extra file or directory included in every Codex review beyond auto-detected changes |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | text | `[loop]` progress lines per attempt (`running Claude builder`, `running Codex review on N file(s)`, sign-off path) |
| audit dir | files | `<out-dir>/<phase>/attempt_NN_claude_builder.txt`, `attempt_NN_codex_review.txt`, `attempt_NN_changed_files.json` per iteration |
| audit dir | file | `<out-dir>/<phase>/SIGNED_OFF.json` on clean Codex pass (return code 0 from reviewer) |
| audit dir | file | `<out-dir>/<phase>/LOOP_FAILED.json` on cap reached / builder failed / reviewer failed |
| exit code | int | `0` Codex signed off, `1` loop ended without sign-off |

## Loop Status Values (in summary JSON)

| Status | Meaning |
|---|---|
| `signed_off` | Reviewer returned 0 — clean pass — SIGNED_OFF.json written |
| `builder_failed` | Claude subprocess returned non-zero — no review attempted this turn — loop exits |
| `reviewer_failed` | Codex subprocess returned a code other than 0 (sign-off) or 1 (issues) |
| `no_reviewable_changes` | Builder succeeded but no reviewable files changed (text suffixes / size cap excluded everything) |
| `running` | (in-flight only) |

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Python 3.10+ | runtime | stdlib only |
| `claude` CLI on PATH | tool | `shutil.which("claude")` required at call time |
| `codex_bridge.py` | sibling tool | Default path `C:\Users\Owner\apex_governance\cc_runbook\codex_bridge.py`; override via `--codex-bridge` |
| Claude subscription auth | account | Subprocess env scrubbed of `ANTHROPIC_API_KEY` / `CLAUDE_API_KEY`; forces `CLAUDE_AUTH_MODE=subscription` |
| Codex subscription auth | account | Subprocess env scrubbed of `OPENAI_API_KEY`; forces `CODEX_AUTH_MODE=subscription`; defaults `CODEX_MODEL=gpt-5.2` |
| Read+write access to `--repo` and `--out-dir` | filesystem | Builder mutates repo; loop writes audit logs |

## How It Works

1. SHA-256 snapshot the repo (excluding `.git/`) as the change-detection baseline.
2. For each attempt 1..max_attempts:
    1. Run the Claude builder with the current prompt (initial prompt for attempt 1; rebuilt fix prompt for attempts 2+).
    2. Write `attempt_NN_claude_builder.txt` with exit code, stdout, stderr.
    3. Re-snapshot; compute changed files vs baseline; filter to text suffixes within 1.5 MB; exclude anything under `audit/claude_codex_loop/` (self-reference avoidance); union with any extra `--review-path` entries; write `attempt_NN_changed_files.json`.
    4. If builder rc != 0 → mark `builder_failed`, write `LOOP_FAILED.json`, exit 1.
    5. If nothing reviewable → mark `no_reviewable_changes`, write `LOOP_FAILED.json`, exit 1.
    6. Invoke `codex_bridge.py review <paths> --phase <phase>` with subscription env.
    7. Write `attempt_NN_codex_review.txt`.
    8. If reviewer rc == 0 → mark `signed_off`, write `SIGNED_OFF.json`, exit 0.
    9. If reviewer rc == 1 → build `fix_prompt` containing changed files + Codex stdout/stderr + original prompt; loop to next attempt.
    10. Else → mark `reviewer_failed`, write `LOOP_FAILED.json`, exit 1.
3. If attempt cap reached → write `LOOP_FAILED.json` with `status` = last seen status, exit 1.

## Safety Posture

| Safety property | How enforced |
|---|---|
| Bounded retries | `--max-attempts` (default 5); no infinite loop possible |
| Bounded time | `--builder-timeout-minutes` + `--reviewer-timeout-minutes`; `TimeoutExpired` handled, exit 124 captured in log |
| No plaintext secrets | `safe_env_for_claude` POPs `ANTHROPIC_API_KEY`/`CLAUDE_API_KEY`; `safe_env_for_codex` POPs `OPENAI_API_KEY`. Subscription mode forced. |
| Explicit failure logs | Every attempt writes a deterministic `attempt_NN_*.txt`. Final state is either `SIGNED_OFF.json` or `LOOP_FAILED.json`. |
| Cost-bounded | Builder + reviewer subscription mode; no API-key spend path |
| Self-reference safe | Excludes `audit/claude_codex_loop/` from being fed back as reviewable changes |
| No silent retry on reviewer crash | rc not in {0,1} → `reviewer_failed`, loop exits |

## Limitations and Edge Cases

- Builder timeout is generous (120 min) — long enough for substantial work, but a hung Claude session ties up the loop until it expires. Tune downward for tighter feedback.
- Snapshot-based change detection misses metadata-only changes (mode/ACL/timestamp).
- Files >1.5 MB or non-text suffixes are silently skipped during review. Add them via `--review-path` if review is required.
- Loop does NOT roll back failed builds. If Claude makes destructive edits and Codex rejects, the repo is left in the post-build state for human review.
- The fix prompt is built by concatenating the original prompt + Codex output. Very large Codex outputs can blow Claude's prompt budget; the tool does not truncate.
- Only ONE reviewer pass per attempt — no human-in-loop check between builder and reviewer.

## Calling Convention

Standard run with all defaults:
```powershell
python registry/claude_codex_loop.py --prompt-file docs/spec/my_build_prompt.md --phase MY-PHASE-001
```

With explicit timeouts (shorter for iterative work):
```powershell
python registry/claude_codex_loop.py `
  --prompt-file docs/spec/agent_spec.md `
  --phase AGEN-spec-agent `
  --max-attempts 3 `
  --builder-timeout-minutes 30 `
  --reviewer-timeout-minutes 20
```

With extra files always included in Codex review:
```powershell
python registry/claude_codex_loop.py `
  --prompt-file docs/spec/migration.md `
  --phase AGEN-migration `
  --review-path docs/spec/migration.md `
  --review-path registry/migrations/
```

## Apex WorkOrder Use

This is the canonical "review-required" runner. Recommended call sites:
- Agent spec implementation (AGEN-*)
- Schema migrations
- Doctrine changes that must pass Codex gate
- Any task labeled "requires Codex review" in its Task Packet

NOT recommended for:
- Quick fixes
- Documentation-only changes (use direct Claude / Codex separately)
- Anything where a single failed attempt should NOT be auto-retried (set `--max-attempts 1` if you want a one-shot)

## Promotion Provenance

Already registered (`APEX-MB-PY-00023`, ACTIVE since 2026-05-22). Was missing the four tool docs. Promoted per APEX_PARALLEL_MERGE_PLAYBOOK step 4 batch #2.

Existing audit evidence under `audit/claude_codex_loop/`:
- `AGEN-architecture-agent/` — SIGNED_OFF (also has earlier LOOP_FAILED — re-run worked)
- `AGEN-architecture-agent-post-migration/` — LOOP_FAILED (link as evidence of expected failure semantics)
- `AGEN-architecture-agent-v2/`
- `AGEN-migration-coordinator/` — SIGNED_OFF
- `AGEN-verification-agent/` — SIGNED_OFF (also has LOOP_FAILED)

Test record should reference ONE SIGNED_OFF + ONE LOOP_FAILED transcript as evidence, per playbook directive "do not require future contexts to read the whole audit tree."
