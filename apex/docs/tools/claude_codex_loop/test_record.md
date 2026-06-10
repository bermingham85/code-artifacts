# TEST RECORD - claude_codex_loop

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00023 |
| **Tested By** | Codex |
| **Test Date** | 2026-05-25 |
| **Overall Result** | PASS - APPROVED |

## Test Environment

| Field | Value |
|---|---|
| OS | Windows |
| Workspace | `C:\Users\Owner\Repos\code-artifacts\apex` |
| Python | 3.13.12 |
| Claude CLI on PATH | `C:\Users\Owner\AppData\Roaming\npm\claude`, `claude.cmd` |
| codex_bridge.py | `C:\Users\Owner\apex_governance\cc_runbook\codex_bridge.py` exists |
| Out dir | `audit/claude_codex_loop/` |

## Codex Source Fixes Applied

| Fix | Root cause | Result |
|---|---|---|
| Scrub all API-key env vars from both subprocess envs | Claude env removed Claude keys only; Codex env removed OpenAI key only | `ANTHROPIC_API_KEY`, `CLAUDE_API_KEY`, and `OPENAI_API_KEY` are absent from both env dicts |
| Validate repo/prompt before creating output dir | Negative tests could leave misleading empty log dirs | Missing-prompt test now exits before `out-dir/phase` is created |
| Explicit max-attempts terminal status | If every reviewer pass returned findings, `LOOP_FAILED.json` could retain `status=running` | Loop now writes `status=max_attempts_exhausted` when the cap is reached |

## Test Cases

| Test | Result | Evidence |
|------|--------|----------|
| TC-001 Syntax | PASS | `python -m py_compile registry\claude_codex_loop.py` exited 0 |
| TC-002 Argparse | PASS | `python registry\claude_codex_loop.py --help` listed all required flags |
| TC-003 Missing prompt file | PASS | `Prompt file not found: C:\nonexistent.md`; no `C:\tmp\apex_loop_neg\SMOKE-NEG-PROMPT` dir created |
| TC-004 Missing repo dir | PASS | `Repo not found: C:\nonexistent` |
| TC-005 Env scrub | PASS | Assertion output: `True True subscription subscription` |
| TC-006 Smoke loop | PASS WITH EXPECTED NO-REVIEW PATH | One-attempt live smoke wrote `audit/claude_codex_loop/SMOKE/marker.txt`, then ended deterministically with `status=no_reviewable_changes` because audit-loop paths are intentionally excluded from review |
| TC-007 max_attempts cap | PASS | Temporary monkeypatched test returned `{"attempts": 2, "code": 1, "status": "max_attempts_exhausted"}` |
| TC-008 Audit self-reference exclusion | PASS | `audit/claude_codex_loop/SMOKE-001/attempt_01_changed_files.json` had marker/log files in `changed_files` and empty `reviewed_files` |
| TC-009 Live evidence link | PASS | `audit/claude_codex_loop/AGEN-migration-coordinator/SIGNED_OFF.json` is valid with `status=signed_off`; `audit/claude_codex_loop/AGEN-verification-agent/LOOP_FAILED.json` is valid failure evidence with `status=reviewer_failed`. Claude's originally selected `AGEN-architecture-agent-post-migration/LOOP_FAILED.json` was rejected as evidence because it has `status=running`. |

## Evidence Paths

| Evidence | Path |
|---|---|
| Smoke summary | `audit/claude_codex_loop/SMOKE-001/LOOP_FAILED.json` |
| Smoke manifest | `audit/claude_codex_loop/SMOKE-001/attempt_01_changed_files.json` |
| Smoke marker | `audit/claude_codex_loop/SMOKE/marker.txt` |
| Existing signed-off evidence | `audit/claude_codex_loop/AGEN-migration-coordinator/SIGNED_OFF.json` |
| Existing valid failure evidence | `audit/claude_codex_loop/AGEN-verification-agent/LOOP_FAILED.json` |

## Blocker Report

| Field | Value |
|---|---|
| Exact blocker | None remaining for tool promotion |
| Why it blocks promotion | n/a |
| Lowest-friction resolution | n/a |
| Safe fallback | If a future regression appears, follow `docs/tools/claude_codex_loop/troubleshoot.md` rollback steps |
| Work that can continue | Batch 3 doctrine/policy merge can continue independently |

**All tests passed:** YES
**Approved:** YES - 2026-05-25
