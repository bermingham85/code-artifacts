# TROUBLESHOOT - claude_codex_loop

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00023 |
| Tool | claude_codex_loop |
| Version | 1.0 |
| Status | APPROVED |

## Fast Checks

| Check | Command or method | Expected |
|---|---|---|
| Script parses | `python -c "import ast; ast.parse(open('registry/claude_codex_loop.py').read())"` | No output, exit 0 |
| Claude CLI present | `where claude` | A path is printed |
| codex_bridge exists | `Test-Path C:\Users\Owner\apex_governance\cc_runbook\codex_bridge.py` | True |
| Audit dir writable | `New-Item -ItemType Directory -Force audit/claude_codex_loop` | Directory present |
| Tool is approved | Check `registry/TOOL_INDEX.md` and `docs/APEX_TOOL_MENU.md` | Entry under Approved Tools |
| Subscription env active | Look at any `attempt_NN_claude_builder.txt` recently | No API-key mention; subprocess used subscription auth |

## Common Failures

| Symptom | Likely cause | Fix | Verify |
|---|---|---|---|
| `RuntimeError: claude CLI not found on PATH` | `claude.exe` not installed or not on PATH | Install Claude Code CLI; restart shell so PATH propagates | `where claude` returns a path; re-run |
| `RuntimeError: codex bridge not found` | Default path wrong on this station | Pass `--codex-bridge "C:\actual\path\codex_bridge.py"` OR symlink to default location | Re-run; bridge invokes |
| `Prompt file not found:` exit 1 | Typo'd path or relative path resolved unexpectedly | Pass absolute path or run from repo root | Re-run reaches builder step |
| `Repo not found:` exit 1 | `--repo` is a file or non-existent path | Pass an existing directory (defaults to cwd) | Builder logs appear |
| `status=builder_failed` after attempt 1 | Claude subprocess returned non-zero | Read `attempt_01_claude_builder.txt` STDERR; usual causes: invalid prompt, claude CLI auth not configured, repo permission denied | Fix root cause; re-run |
| `status=no_reviewable_changes` | Builder ran but didn't change anything Codex-reviewable | Confirm prompt actually asks for changes; check `attempt_01_changed_files.json` — likely empty; possibly all changes were >1.5MB or non-text-suffix | Adjust prompt or add `--review-path` |
| Loop hits `max_attempts` and exits `LOOP_FAILED.json` | Codex keeps rejecting the build | Read `attempt_NN_codex_review.txt` for the LATEST iteration; address the specific finding manually OR refine the prompt and rerun | Re-run signs off |
| `status=reviewer_failed` with rc not in {0,1} | codex_bridge crashed or returned an unexpected exit code | Read `attempt_NN_codex_review.txt` stderr; check bridge log if any; common causes: codex CLI auth expired, network blip, model name in env wrong | Fix bridge issue; re-run |
| Builder times out (rc=124) | `--builder-timeout-minutes` too short for the work | Increase the timeout OR split the prompt into smaller phases | Re-run completes within window |
| Reviewer times out (rc=124) | `--reviewer-timeout-minutes` too short, OR too many files in review | Increase timeout OR exclude unrelated paths via prompt scoping OR reduce repo snapshot scope | Re-run completes |
| `audit/claude_codex_loop/<phase>/` from a previous run was overwritten | Same `--phase` used twice without renaming the prior dir | Rename the previous run dir before retrying: `Move-Item audit/claude_codex_loop/PHASE-001 audit/claude_codex_loop/PHASE-001-run1` | New run's files appear cleanly |
| ANTHROPIC_API_KEY shows up in audit log | Loop should be scrubbing the env — if you see this, the scrub regressed | Open issue immediately; revert source to the last known good revision; do NOT continue running | Re-test TC-005 |
| Snapshot phase is extremely slow | `--repo` points at a network share (e.g. `\\192.168.50.246\...`) | Use a LOCAL repo path; the snapshot SHA-256s every file | Snapshot completes in seconds for normal repo sizes |

## Rollback / Disable

To stop the loop being callable while leaving evidence intact (per playbook step 4 rollback requirement):

1. Disable scheduled callers (Task Scheduler / n8n / any wrapper script):
   - Identify callers with: `grep -r "claude_codex_loop" apex/` and inspect Task Scheduler GUI on each station.
   - Disable each schedule without deleting (so re-enable is one click).
2. Keep transcript evidence in place:
   - Do NOT delete `audit/claude_codex_loop/` — that's the historical record.
3. Restore the previous script version from Git if the latest broke:
   - `git log --oneline registry/claude_codex_loop.py`
   - `git checkout <prior-sha> -- registry/claude_codex_loop.py`
   - Commit with message `revert: claude_codex_loop to <sha> per APEX_PARALLEL_MERGE_PLAYBOOK rollback`
4. Mark the tool DEPRECATED in `docs/APEX_TOOL_MENU.json` and regenerate the menu.
5. Add a row to `docs/DOCUMENT_REGISTER.md` noting the rollback rationale.

## Reusable Fix Log

Append new fixes here. Keep entries short and version-controlled.

| Date | Symptom | Root cause | Fix | Verification |
|---|---|---|---|---|
| 2026-05-25 | Initial troubleshoot page created during APEX_PARALLEL_MERGE_PLAYBOOK promotion batch #2 | Operational doc gap; tool was registered in DOCUMENT_REGISTER but missing 4-doc trio | Drafted blueprint/guidance/test_record stub/troubleshoot per playbook | Test record completion + `validate_tool_docs --quiet` to be run by Codex |
| 2026-05-25 | Env-scrub safety test required all API keys absent from both subprocess envs | Claude env scrubbed Claude keys only; Codex env scrubbed OpenAI key only | Both env builders now remove `ANTHROPIC_API_KEY`, `CLAUDE_API_KEY`, and `OPENAI_API_KEY` | TC-005 output: `True True subscription subscription` |
| 2026-05-25 | Negative prompt/repo tests could create misleading empty log dirs | Output directory was created before validating prompt/repo | Moved output-dir creation after validation | Missing-prompt test left no phase directory |
| 2026-05-25 | `LOOP_FAILED.json` could keep `status=running` after all reviewer attempts returned findings | Max-attempts exhaustion did not set a terminal status | Set `status=max_attempts_exhausted` before writing final failure summary | Monkeypatched cap test produced `status=max_attempts_exhausted`, attempts=2 |
