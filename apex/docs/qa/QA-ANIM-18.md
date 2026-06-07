# QA-ANIM-18 — fal.ai shim test report

## What was tested

1. **Probe mode** — `--probe` resolves FAL_AI_API_KEY from `X:/env_sync/user_portable.json`, reports fingerprint `95de:0714` (matches ANIM-17 cert), reports tier-config `shim_status: READY` and `wrapper_invocation: ...muscle_fal_shim.py...`, returns exit 0.
2. **Build-payload determinism** — `build_payload("1", falcloud.json)` invoked twice; SHA256 of the canonical (sorted-keys) payload bytes identical across runs. Same input → same output, no time-based fields in the payload itself.
3. **Default submit is dry-run** — `--submit --shot-id 1 --tier-plan falcloud.json` (no `--live`) returns `DRY_RUN` status, prints the phrase "DRY-RUN — no HTTP call made.", computes payload_sha256, returns exit 0. **Zero HTTP calls issued.**
4. **17-probe negative + redaction-regression harness** at `apex/audit/anim-18/probe_negatives.py` (expanded through rounds 1–6 in response to Codex findings):
   - P1 `TIER_PLAN_NOT_FOUND` — missing path
   - P2 `TIER_PLAN_UNPARSEABLE` — non-JSON file
   - P3 `TIER_PLAN_INVALID_PHASE` — wrong phase tag
   - P4 `SHOT_NOT_IN_TIER_PLAN` — shot_id not present
   - P5 `SHOT_NOT_ROUTED_TO_FALCLOUD` — shot exists but tier_chosen ≠ FalCloud
   - P6 `INVALID_SHOT_ID` — regex reject (id with spaces)
   - P7 `FAL_KEY_UNRESOLVED` — monkeypatched resolver returns `ENV_KEY_MISSING`
   - P8 `DRY_RUN_URLOPEN_SUPPRESSED` — tripwire-asserts urlopen NOT called when --live absent
   - P9–P11 (sentinel-key live-path redaction): `MOCK_LIVE_VALUE_REDACTED`, `MOCK_LIVE_DICT_KEY_REDACTED`, `MOCK_LIVE_HTTP_ERROR_BODY_REDACTED` — sentinel in value, in dict-key, and in HTTPError body echo of Authorization
   - P12–P14 (resolver-leak surface with key in scope): `RESOLVER_LEAK_PROBE`, `RESOLVER_LEAK_BUILD_PAYLOAD`, `RESOLVER_LEAK_DRY_RUN` — allowlist + `_seal_outward` strip sentinel from value field, nested dict, and dict-key forms across probe/build_payload/dry-run modes
   - P15–P17 (resolver-leak surface with NO key in scope — round 6 F-1 fix coverage): `RESOLVER_LEAK_NO_KEY_PROBE`, `RESOLVER_LEAK_NO_KEY_BUILD_PAYLOAD`, `RESOLVER_LEAK_NO_KEY_DRY_RUN` — verifies `fingerprint_only()` suppresses sentinel embedded in the free-form `error` field even when `_seal_outward()` no-ops (no raw key to scrub against)
5. **Leak check** — for every probe, both the live `FAL_AI_API_KEY` (if resolvable from env_sync) AND a sentinel key are asserted absent from probe output (literal + JSON-escaped forms). Harness is fail-closed: `_fail_closed_scrub()` runs on the entire output tree before any print, so a redaction regression surfaces as failed probe + LEAK flag rather than secret leaked to stdout. Global leak-check across the entire harness output also CLEAN.
6. **Tier-config flip** — `effective_tier_status("FalCloud", cfg)` now resolves to `READY` post-flip (was `KEY_OK_SHIM_PENDING` before), and `plan_tier("FalCloud", ...)` returns regular `PLAN` (no longer `TIER_KEY_OK_SHIM_PENDING`).

## How it was tested

- Direct CLI invocation from repo root.
- Property-test of determinism via importlib reload + bytes equality.
- Negative probes exercised through a single harness that asserts stable status enums + clean leak-check per probe.

## Results

| Property | Outcome |
|---|---|
| Probe READY + correct fingerprint | PASS |
| Build-payload determinism (2 runs) | PASS (identical SHA `0b55098b7f33...`) |
| Default --submit is dry-run | PASS (0 HTTP calls) |
| 17/17 negative + redaction-regression probes return stable status | PASS |
| Per-probe leak check (real + sentinel keys, literal + escaped) | PASS (17/17 CLEAN) |
| Global leak check | PASS (CLEAN) |
| Fail-closed scrub before stdout print | PASS |
| Tier-config flip → FalCloud READY | PASS |

## Known limits

1. **Live HTTP path is untested in CI** — by design. The shim's `--live` branch only runs under operator-explicit invocation; CI must never call it (would incur cloud spend). The shape correctness of the request (headers, body, URL) is asserted at the build-payload level; a future cert may add a live integration test with a fal.ai sandbox endpoint if one exists.
2. **Upstream data quality** — the existing Grog FalCloud tier-plan carries `character_markers: null` and empty `image_url`. The shim correctly passes these through (it does not invent fields). Quality at the source is the storyboard/anchor-image upstream responsibility — tracked under `MA-ANIM-14-MARKERS-{...}` (markers) and the not-yet-built reference-pack anchor flow (image_url).
3. **fal.ai API surface drift** — pinned in shim constants. If fal.ai renames the model id or queue base, the change is a one-line code edit. The negative-path harness will detect API drift as `FAL_HTTP_ERROR` / `FAL_UNPARSEABLE_RESPONSE` rather than crashing.

## Data used

- `apex/docs/anim/ANIM-16-tier-plan-grog_playground-falcloud.json` — 43-shot FalCloud-routed plan (ANIM-16 evidence).
- `apex/docs/anim/ANIM-16-tier-plan-grog_playground-energy.json` — energy-routed plan (used by P5 to assert SHOT_NOT_ROUTED_TO_FALCLOUD).
- `X:/env_sync/user_portable.json:FAL_AI_API_KEY` — live key, fingerprint `95de:0714`, length 69.

## Pass criteria

All seven from SPEC-ANIM-18 §"Pass criteria" satisfied at this writing. Awaiting codex silent-twice + cert + PR.
