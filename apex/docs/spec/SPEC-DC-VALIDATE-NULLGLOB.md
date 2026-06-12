# SPEC — dc-validate workflow nullglob hardening

**ID:** SPEC-DC-VALIDATE-NULLGLOB
**Scope:** `.github/workflows/dc-validate.yml`
**Author:** APEX orchestrator (Claude Code)
**Date:** 2026-06-12
**Authority:** `apex_governance/PLAN_CRITERIA.md` §0; `CLAUDE_CODEX_DOCTRINE` (Codex reviewer-of-record).
**Related WO:** APEX-ANIM-MB-WO-00001 (ANIM-18 merge unblock).
**Related PRs:** #25 (introduced bug), #27 (first victim).

## 1. Problem

`Document Control Validation` workflow (added in PR #25) fails on every PR that does not contain real `workers/<name>/MANIFEST.json` files, because the bash `for` loops iterate the literal glob pattern when no files match:

```
for manifest in workers/*/MANIFEST.json; do
  ...
done
```

With default bash, the unmatched glob expands to the literal string `workers/*/MANIFEST.json`. The subsequent `python3 -c "...open('$manifest')..."` call fails with `FileNotFoundError`, the error is swallowed by `2>/dev/null`, and the script proceeds to its FAIL=1 branch — printing the literal-string filename as "missing required field".

Repo currently contains only `workers/_base/README.md`. No PR can pass DC compliance until either (a) the workflow is hardened, or (b) every PR seeds real worker manifests. (b) is impractical for any PR not specifically about workers, so (a) is the right fix.

## 2. Acceptance criteria

- AC1: When the repo has zero `workers/<name>/MANIFEST.json` files, the workflow exits 0 on every step (no false-positive failure).
- AC2: When the repo has a valid worker manifest (with all four required fields), the workflow exits 0.
- AC3: When the repo has a worker directory missing its `MANIFEST.json`, step 1 still fails.
- AC4: When the repo has a worker manifest missing a required field, step 2 still fails.
- AC5: Change is minimal and additive: only `shopt -s nullglob` added at top of each `run:` block.

## 3. Out of scope

- No semantic change to which fields are required.
- No change to `_base` skip behavior.
- No change to root-level file warning rules.
- No change to the python validation snippet.

## 4. Verification

- V1 (local): `bash -c 'shopt -s nullglob; for m in workers/*/MANIFEST.json; do echo X; done; echo EXIT=$?'` → no `ITER` lines, `EXIT=0`. Run pre-merge — DONE this session.
- V2 (CI on this fix PR): the `Validate DC Compliance` check passes on the fix PR itself.
- V3 (CI re-run on PR #27 after merge to main + #27 rebase or re-run): `Validate DC Compliance` passes on PR #27 with no other changes.

## 5. Deliverables

- `.github/workflows/dc-validate.yml` — three `shopt -s nullglob` lines added.
- `apex_governance/certs/CERT-DC-VALIDATE-NULLGLOB.json` — sign-off.
- This spec.
- Codex adversarial-review transcripts under `apex_governance/codex_runs/DC-VALIDATE-NULLGLOB/`.

## 6. Rollback

Single-file revert; no downstream coupling. `git revert <merge-commit>` is sufficient.
