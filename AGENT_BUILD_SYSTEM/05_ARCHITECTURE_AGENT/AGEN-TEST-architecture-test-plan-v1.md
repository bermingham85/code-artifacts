# Architecture Agent — Test Plan

**Document ID:** AGEN-TEST-architecture-test-plan-v1
**Date:** 2026-05-24
**Workflow under test:** `AGEN-WKFL-architecture-agent-v1.json` deployed at `POST ${N8N_BASE_URL}/webhook/architecture-agent` (resolve concrete endpoint from the ops secrets/configuration registry at runtime — concrete LAN endpoints stay in operator-private runbooks)

---

## Auth header

All requests require:
```
Authorization: Bearer <APEX_WEBHOOK_TOKEN>   # credential ref ${CRED_APEX_WEBHOOK_TOKEN} (resolve concrete id from ops secrets registry)
Content-Type: application/json
```

Missing/invalid token → `401 unauthorized`.

## Fixtures

- **Project (live):** `5f59c200-62cd-44e8-8852-bcbb9dcd27a9`
- **Reviewed spec (live):** `fc400853-13df-4205-a091-e7d6b82ffd1a` (status=reviewed, 2 requirements with binary AC)
- **Idempotency key for E2E:** generate once per run as `arch-e2e-<UTC timestamp>-<random>`; capture it as `RUN_IDEMPOTENCY_KEY`. Never commit or reuse a concrete key across runs.

## Test cases

### T1 — happy path decompose
**Request:**
```json
{
  "action": "decompose",
  "project_id": "5f59c200-62cd-44e8-8852-bcbb9dcd27a9",
  "spec_id": "fc400853-13df-4205-a091-e7d6b82ffd1a",
  "idempotency_key": "${RUN_IDEMPOTENCY_KEY}"
}
```
**Expected:** HTTP 200, body contains `architecture_id` (uuid), `version=1`, `status="draft"`, non-empty `components`, non-empty `tasks`, valid `build_order`, every task `estimated_hours ∈ [0.5, 2.0]`, every task `component` is in `components[].name`.

### T2 — safe replay
Re-POST T1's exact captured request body from the same run, including the same `${RUN_IDEMPOTENCY_KEY}`. **Expected:** HTTP 200, identical `architecture_id`, `replayed: true` somewhere in response, no new DB row.

### T3 — idempotency conflict
Re-POST with same `idempotency_key` but a different `notes` field. **Expected:** HTTP 409, `error="idempotency_conflict"`.

### T4 — refine without prior
```json
{ "action": "refine", "project_id": "...", "spec_id": "<NEW spec>", "idempotency_key": "arch-e2e-2026-05-24-T4" }
```
**Expected:** HTTP 404, `error="architecture_not_found"`.

### T5 — refine of T1
After T1 succeeds:
```json
{ "action": "refine", "project_id": "...", "spec_id": "fc400853-...", "idempotency_key": "arch-e2e-2026-05-24-T5" }
```
**Expected:** HTTP 200, `version=2`, prior v1 row's `status` transitions to `superseded` (verify with SQL).

### T6 — get_latest after T5
```json
{ "action": "get_latest", "project_id": "...", "spec_id": "fc400853-..." }
```
**Expected:** HTTP 200, returns the v2 row (highest non-superseded), NEVER the superseded v1.

### T7 — get_latest with no architecture
`spec_id` has no rows. **Expected:** HTTP 404, `error="architecture_not_found"`.

### T8 — invalid action
`action="explode"`. **Expected:** HTTP 400, `error="invalid_action"`.

### T9 — invalid UUID
`project_id="not-a-uuid"`. **Expected:** HTTP 400, `error="invalid_uuid"`.

### T10 — spec not reviewable
Use a `draft` spec_id. **Expected:** HTTP 422, `error="spec_not_reviewable"`.

### T11 — spec not found
`spec_id=00000000-0000-0000-0000-000000000000`. **Expected:** HTTP 404, `error="spec_not_found"`.

### T12 — auth fail
Omit `Authorization` header. **Expected:** HTTP 401, `error="unauthorized"`.

### T13 — decompose with active row
After T1 succeeds, re-POST T1 with a DIFFERENT `idempotency_key`. **Expected:** HTTP 422 with `error="architecture_exists"` (RPC bounce — use `refine`).

## Verification queries

```sql
-- T1 result
SELECT id, version, status, jsonb_array_length(tasks) AS task_count
FROM agent_architectures
WHERE project_id='5f59c200-...' AND spec_id='fc400853-...'
ORDER BY version;

-- T5 supersede check
SELECT version, status FROM agent_architectures
WHERE project_id='5f59c200-...' AND spec_id='fc400853-...';
-- expect v1=superseded, v2 in {draft, reviewed}

-- T6 get_latest matches the T1 v1 architecture when no refine has run
SELECT get_latest_architecture('5f59c200-...'::uuid, 'fc400853-...'::uuid);
```

## E2E gate (RULE 4)

The shipped agent passes when **T1, T2, T6, T8, T9, T10, T11, T12** all return the expected status. For this gate, T6 validates `get_latest` against the T1 v1 architecture because no refine has run. T3/T4/T5/T7/T13 are regression tests for the refine/conflict paths and are run in a follow-up regression session.
