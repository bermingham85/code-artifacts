# SPEC-ANIM-17 — FalCloud tier env-key resolution via X:/env_sync

## Identity
- Phase ID: `ANIM-17`
- Title: Wire ANIM-05 video agent to resolve `FAL_AI_API_KEY` from `X:/env_sync/user_portable.json` so the FalCloud tier flips from operator-gated (G9) to env-resolvable. Shim implementation deferred to a follow-on phase.
- Parent subproject: `ANIM` (WO `APEX-ANIM-MB-WO-00001` §6).
- Owner agent: APEX orchestrator (Claude Opus 4.7).
- Depends-on: ANIM-05 (CERT-ANIM-05 — video agent + tier config).
- Blocks: future fal.ai shim phase (build the actual wrapper); follow-on bursts using FalCloud once shim lands.
- Reference patterns: ANIM-14 schema-extension + env-override pattern (`APEX_PHASE_AUDIT_DIR`); ANIM-13 provenance-triple verification (re-used here for env-key probe shape).
- Branch: `phase/ANIM-17-fal-key` (stacked on `phase/ANIM-14-marker-schema`).
- Cert tag: `cert/ANIM-17@<sha>`.

## Why ANIM-17

ANIM-05's FalCloud tier carried a hard `OPERATOR_GATED` status with the blocker "G9 — fal.ai key-resolution route TBD; key NOT in env_sync; not pursuable autonomously". `FAL_AI_API_KEY` is in fact registered in `X:/env_sync/user_portable.json:FAL_AI_API_KEY` (verified at spec time). ANIM-17 wires the agent to resolve it, exposes a non-leaking fingerprint (first-4 + last-4 chars only) in the tier probe output, and changes the static blocker to a clear "shim not built" follow-on.

This does NOT implement the fal.ai wrapper shim. It closes the key-resolution half of the gate so the next phase can build the shim against a known-good key path.

## Context window budget
- ≤6 files committed; ≤200 LOC delta.
- Files in scope:
  1. `apex/docs/spec/SPEC-ANIM-17.md` (this).
  2. `apex/registry/muscle_video_agent.py` (APEX-MB-PY-00114; modify, no new muscle).
  3. `apex/docs/anim/ANIM-05-tier-config.json` (FalCloud entry updated).
  4. `apex/docs/anim/ANIM-17-evidence.json` (phase evidence with probe outputs).
  5. `apex/audit/anim-17/` (per-run audit JSONs + key-probe transcript).
- Out of scope: fal.ai animation-agent shim (separate phase); any actual render; storing the resolved key anywhere other than process memory.

## Access matrix
| Resource | Path | R/W | Source |
|---|---|---|---|
| Repo | `bermingham85/code-artifacts` branch `phase/ANIM-17-fal-key` | RW | env_sync GitHub PAT |
| Video agent | `apex/registry/muscle_video_agent.py` | RW | local (registered APEX-MB-PY-00114) |
| Tier config | `apex/docs/anim/ANIM-05-tier-config.json` | RW | local |
| env_sync | `X:/env_sync/user_portable.json` | R | local NAS-mounted |
| Codex | gpt-5.5 | invoke | local |

## Inputs (verified at spec time)
- `X:/env_sync/user_portable.json` contains `FAL_AI_API_KEY: "95de69b8-...:ea42a27df..."` (32-byte UUID + 32-hex secret format; treated as opaque string).
- File parses as a valid JSON object.

## Schema extension (ANIM-05-tier-config.json FalCloud entry)

Bump `schema_version` 1 → 2. FalCloud entry gains:

```jsonc
"FalCloud": {
  "label": "fal.ai animation-agent (cloud burst fallback)",
  "model_files": [],
  "vram_gb": 0,
  "approx_seconds_per_clip": 60,
  "cost_usd_per_clip": 0.10,
  "best_for": "burst-scale render windows when local GPU is busy",

  "status": "ENV_KEY_GATED",            // was OPERATOR_GATED; agent recomputes effective_status at runtime
  "requires_env_key": "FAL_AI_API_KEY",
  "requires_env_key_from_env_sync_path": "X:/env_sync/user_portable.json",
  "requires_env_key_field": "FAL_AI_API_KEY",

  "shim_status": "PENDING",
  "shim_blocker": "fal.ai animation-agent wrapper script not yet built; ANIM-17 closes the key-resolution gate only — shim implementation is a follow-on phase",
  "wrapper_invocation": null
}
```

## Agent change (muscle_video_agent.py)

1. New helper `resolve_env_key_from_env_sync(env_sync_path, field) -> dict`:
   - Reads the env_sync file; verifies it parses as a JSON object.
   - Reads the named field; verifies it's a non-empty string.
   - Returns `{"status": "OK", "key": <secret>, "fingerprint": "<first4>...<last4>", "key_sha256_first_12": "<12 hex>"}` on success.
   - Returns `{"status": "ENV_SYNC_PATH_MISSING" | "ENV_SYNC_UNPARSEABLE" | "ENV_KEY_MISSING" | "ENV_KEY_NOT_STRING" | "ENV_KEY_EMPTY"}` on failure.
   - The actual `key` value is included in the helper's return for inline use but MUST NOT be persisted by the caller (only fingerprint is logged).

2. New helper `effective_tier_status(tier_name, cfg) -> dict`:
   - If `cfg.get("requires_env_key")` is absent → returns `{"effective_status": cfg.get("status"), "key_resolution": None}` (unchanged).
   - Else probe env_sync. If probe fails → `{"effective_status": "ENV_KEY_GATED", "key_resolution": {"status": <failure code>, "fingerprint": null}}`.
   - Else if `cfg.get("shim_status") != "READY"` → `{"effective_status": "KEY_OK_SHIM_PENDING", "key_resolution": {"status": "OK", "fingerprint": <8-char>, "key_sha256_first_12": <12 hex>}, "shim_blocker": cfg.get("shim_blocker")}`.
   - Else → `{"effective_status": "READY", "key_resolution": {...}}`.

3. `plan_tier()` consults `effective_tier_status()` instead of `cfg.get("status")`:
   - effective_status="READY" → existing PLAN path.
   - effective_status="KEY_OK_SHIM_PENDING" → new status `TIER_KEY_OK_SHIM_PENDING` (exit 14): reports `tier_status`, `key_resolution.fingerprint`, `shim_blocker`. PLAN withheld until shim lands.
   - Any other → existing `TIER_NOT_READY` path.

4. `--list-tiers` now annotates each tier with its `effective_status` + `key_resolution.fingerprint` (when applicable). The raw key is never emitted.

5. New CLI flag `--probe-key <tier>`: runs `effective_tier_status()` only and prints the resolution + fingerprint. Useful for evidence + ops health checks.

New exit code: 14 / `TIER_KEY_OK_SHIM_PENDING`.

## Security

- The actual key value is read into process memory only when `resolve_env_key_from_env_sync()` is called.
- The key value is NEVER emitted to stdout, stderr, audit JSONs, or storyboard outputs.
- Only the fingerprint (first 4 + last 4 chars) and first 12 hex of sha256 are exposed in agent output. Both are non-reversible / non-usable as the secret itself.
- The env_sync file lives at `X:/env_sync/user_portable.json` which is NAS-backed (`\\192.168.50.246\Extra`); leakage surface is already understood per `feedback_settings_secrets_hygiene`. ANIM-17 does not widen that surface.

## Definition of Done
- FalCloud tier config carries `requires_env_key` + `requires_env_key_from_env_sync_path` + `requires_env_key_field` + `shim_status` + `shim_blocker`.
- `effective_tier_status("FalCloud", cfg)` returns `effective_status: "KEY_OK_SHIM_PENDING"` with a non-null `key_resolution.fingerprint` of length 9 (4 + "..." + 4 wait — actually I'll use `<first4>:<last4>` format = 9 chars including the colon).
- `--probe-key FalCloud` prints the resolution with fingerprint and zero secret bytes.
- `--plan-tier FalCloud --shot 1` returns `TIER_KEY_OK_SHIM_PENDING` exit 14 with the shim_blocker shown.
- Negative probe constructions captured in evidence:
  - env_sync path missing → `ENV_SYNC_PATH_MISSING` reported in key_resolution.status.
  - env_sync parses but field missing → `ENV_KEY_MISSING`.
  - env_sync field is empty string → `ENV_KEY_EMPTY`.
- Codex silent-twice on gpt-5.5.
- Cert + handover + PR.

## Test plan
1. `python apex/registry/muscle_video_agent.py --probe-key FalCloud` → KEY_OK_SHIM_PENDING, fingerprint = `95de:0714` (first4=`95de`, last4=`0714` from the verified key).
2. `python apex/registry/muscle_video_agent.py --plan-tier FalCloud --shot 1` → `TIER_KEY_OK_SHIM_PENDING` exit 14.
3. `python apex/registry/muscle_video_agent.py --plan-tier Wan22 --shot 1 --scene MagicalRealmPlayground` → unchanged PLAN behavior (no regression).
4. `python apex/registry/muscle_video_agent.py --list-tiers` → FalCloud entry shows `effective_status: KEY_OK_SHIM_PENDING` + `fingerprint: 95de:0714`; other tiers unchanged.
5. Negative probes via the inline harness `apex/audit/anim-17/key_probe_negatives.py`:
   - Temp tier config pointing at non-existent env_sync path → ENV_SYNC_PATH_MISSING.
   - Temp env_sync without FAL_AI_API_KEY → ENV_KEY_MISSING.
   - Temp env_sync with empty FAL_AI_API_KEY → ENV_KEY_EMPTY.

## Pass criteria
- [ ] Tier config schema updated; FalCloud now ENV_KEY_GATED + requires_env_key.
- [ ] effective_tier_status() resolves FalCloud to KEY_OK_SHIM_PENDING with fingerprint at runtime.
- [ ] plan_tier and probe-key flows expose fingerprint + shim_blocker; never the secret.
- [ ] Negative probes pass.
- [ ] Codex silent-twice.
- [ ] PR opened, cert minted, handover delivered, certs/index.json appended.

## Open follow-on (out of scope)
- `ANIM-18` (or later): build the fal.ai animation-agent shim that consumes a shot list + the resolved key and submits jobs to fal.ai. Once shim is wired and tested, shim_status flips to "READY" and FalCloud's effective_status reaches "READY" → plan_tier returns PLAN.

## Rollback plan
- `git restore` the changed files; ANIM-05 returns to OPERATOR_GATED FalCloud immediately.

## Doctrine conformance
- **P3** (no invention): the key value is sourced verbatim from env_sync; never composed or guessed.
- **R15**: silent-twice on the diff bundle.
- **R16**: max 5 fix rounds.
- **R19**: REUSE — extends existing APEX-MB-PY-00114 (no new muscle); reuses the env_sync canonical path documented in PLAN_CRITERIA §1.4.
- **R20**: preserves detail — the resolved key is never truncated/rephrased; only a non-reversible fingerprint is exposed.
- **O2/O6/O9**: tier_config schema_version 1→2; ISO8601 UTC audit JSON timestamps; secret never written to disk outside env_sync's authoritative location.
