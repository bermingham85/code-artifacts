# Builder Agent — Test Plan

**Document ID:** AGEN-TEST-builder-test-plan-v1
**Date:** 2026-05-25
**Workflow under test:** `AGEN-WKFL-builder-agent-v1.json` deployed at `POST ${N8N_BASE_URL}/webhook/builder-agent` (resolve concrete endpoint from the ops secrets/configuration registry at runtime — concrete LAN endpoints stay in operator-private runbooks)

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
- **Reviewed spec (live):** `fc400853-13df-4205-a091-e7d6b82ffd1a` (status=reviewed, 2 requirements with binary AC) — captured as `${SPEC_ID}`
- **Architecture row (produced by Architecture Agent for the above spec):** captured as `${ARCH_ID}` from the Architecture Agent's `decompose` response; the decomposition entry under test is `architecture.tasks[0]` with `architecture.tasks[0].task_id = ${ARCH_TASK_UUID}` (the decomposition's UUID — not necessarily equal to any `agent_tasks.id`).
- **agent_tasks row for the build target:** `agent_tasks` does NOT have an `architecture_id` foreign key (the schema links architectures to specs, not to individual tasks). Before T1 runs, INSERT an `agent_tasks` row capturing the buildable unit: `id=${SEED_TASK_ID}` (any UUID), `project_id='5f59c200-...'`, `title=<from architecture.tasks[0].name>`, `description=<from architecture.tasks[0].description>`, `status='pending'`, `spec_reference=${SPEC_ID}::text`. Callers pin the architecture/spec context via the request body (`architecture_id`, `spec_id`) rather than via the agent_tasks row.
- **Idempotency keys:** `build-e2e-2026-05-25-<random>` per test — never reuse across runs.

## Test cases

### T1 — happy path build
**Pre-requisite:** Architecture row exists for `(project_id, spec_id)` with status ∈ {draft, reviewed}; `agent_tasks` row `${SEED_TASK_ID}` exists per the Fixtures section (status=pending, spec_reference=${SPEC_ID}). The caller pins the architecture/spec context via the request body — agent_tasks itself has no architecture_id column.

**Request:**
```json
{
  "action": "build",
  "project_id": "5f59c200-62cd-44e8-8852-bcbb9dcd27a9",
  "task_id": "${SEED_TASK_ID}",
  "architecture_id": "${ARCH_ID}",
  "spec_id": "${SPEC_ID}",
  "idempotency_key": "build-e2e-2026-05-25-T1"
}
```
**Expected:** HTTP 200, body is the **flat** webhook response shape (top-level fields, NOT a nested `artifact` object):
- `artifact_id` (uuid)
- `task_id="${SEED_TASK_ID}"`
- `project_id="5f59c200-..."`
- `architecture_id="${ARCH_ID}"`
- `version=1`
- `status="complete"` (this is the **artifact row's** status — `complete` for a successful build, `rejected` if the model returned a rejection)
- `type ∈ {supabase_sql, n8n_workflow, prompt, edge_function, script, config, doc}` (top-level)
- `name` matches `/^AGEN-(SCRPT|WKFL|PRMPT|EDGE|CFG|DOC)-[a-z0-9-]+-v\d+\.[a-z0-9]+$/` (top-level)
- `content` non-empty, no TODO/FIXME markers (top-level)
- `deploy_instructions` non-empty (top-level)
- `content_hash` is 64-char sha256 hex matching `sha256(content)`
- `content_bytes` equals `Buffer.byteLength(content, 'utf8')` (octet_length, not character length)
- `parent_artifact_id=null`, `root_artifact_id=null` for v1 (the RPC self-roots after insert)
- `rejection_reason=null`
- `replayed=false`
- `request_id` echoed

### T2 — safe replay
Re-POST T1's exact body. **Expected:** HTTP 200, identical `artifact_id`, `replayed=true`, no new DB row (verify by SQL: `SELECT count(*) FROM agent_build_artifacts WHERE task_id='${SEED_TASK_ID}'` MUST remain 1).

### T3 — idempotency conflict
Re-POST T1 with same `idempotency_key="build-e2e-2026-05-25-T1"` but a different `notes` field. **Expected:** HTTP 409, `error="idempotency_conflict"`.

### T4 — retry without prior artifact
**Pre-requisite:** Seed a fresh `agent_tasks` row `${T4_TASK_ID}` with `project_id='5f59c200-...'`, `status='pending'`, `title='T4 retry-without-prior fixture'`, `description='non-empty placeholder so Verify Task passes'`. The row MUST exist before T4 fires, otherwise the workflow returns `task_not_found` at the Verify Task stage (HTTP 404) BEFORE reaching the prior-artifact guard.
```json
{ "action": "retry", "project_id": "5f59c200-...", "task_id": "${T4_TASK_ID}", "idempotency_key": "build-e2e-2026-05-25-T4" }
```
**Expected:** HTTP 404, `error="prior_artifact_not_found"` (NOT `task_not_found` — that means the fixture row is missing; re-seed before retrying the test).

### T5 — retry of T1
After T1 succeeds:
```json
{ "action": "retry", "project_id": "...", "task_id": "${SEED_TASK_ID}", "idempotency_key": "build-e2e-2026-05-25-T5", "notes": "regenerate after codex finding F1" }
```
**Expected:** HTTP 200, new `artifact_id`, `version=2`, `parent_artifact_id` equals T1's artifact_id, `root_artifact_id` equals T1's artifact_id.

### T6 — get_latest after T5
```json
{ "action": "get_latest", "project_id": "...", "task_id": "${SEED_TASK_ID}" }
```
**Expected:** HTTP 200, returns the v2 row (highest version, status ≠ verified-from-prior-revision); NEVER the v1 row.

### T7 — get_latest with no artifact
A `task_id` that has no `agent_build_artifacts` rows. **Expected:** HTTP 404, `error="artifact_not_found"`.

### T8 — invalid action
`action="explode"`. **Expected:** HTTP 400, `error="invalid_action"`.

### T9 — invalid UUID
`project_id="not-a-uuid"`. **Expected:** HTTP 400, `error="invalid_uuid"`.

### T10 — task not found
`task_id=00000000-0000-0000-0000-000000000000`. **Expected:** HTTP 404, `error="task_not_found"`.

### T11 — task/project mismatch
`task_id` valid but belongs to a different `project_id`. **Expected:** HTTP 409, `error="task_project_mismatch"`.

### T12 — auth fail
Omit `Authorization` header. **Expected:** HTTP 401, `error="unauthorized"`.

### T13 — build with prior artifact already present
After T1 succeeds, POST another `build` (not `retry`) for the same `task_id` with a different `idempotency_key`. **Expected:** HTTP 422, `error="artifact_exists"`, with a hint to use `retry`. (This mirrors the architecture agent's `architecture_exists` guard — a `build` on a task that already has a non-rejected artifact is a contract violation; the operator must explicitly request `retry`.)

### T14 — model returns rejected
Build a task whose description is `"do the thing"` (intentionally unclear). **Expected:** HTTP 200 (the workflow ran successfully and persisted an artifact row), body's top-level `status="rejected"` (the workflow returns the artifact-row status, not a separate envelope status), `rejection_reason` is a non-empty one-sentence diagnosis, and `type="doc"`, `name="AGEN-DOC-builder-rejection-v1.txt"`, `content=<the rejection_reason>` (the validator synthesizes a deterministic doc-type row so the RPC's NOT-NULL + 64-char-hex content_hash CHECKs are satisfied). Verify with SQL: `SELECT status, rejection_reason FROM agent_build_artifacts WHERE id='<artifact_id from response>'` — both fields MUST match the response body.

### T15 — banned vague-language scrub
Inject a task description that would push the LLM toward banned words ("make it fast and robust"). **Expected:** the LLM's output is parsed and the validator finds an unpaired banned word → HTTP 500 `internal_error` with `details.issues` listing the banned-word match. (No DB row written.)

### T16 — TODO marker scrub
Inject a task that would push the LLM toward a TODO ("add a TODO for later sub-tasks"). **Expected:** the validator finds the TODO marker → HTTP 500 `internal_error` with `details.issues` listing `artifact_content_contains_todo`.

### T17 — oversize content
Use a task whose Builder output would exceed the workflow's `MAX_CONTENT_BYTES` (default 256 KiB). **Expected:** HTTP 413, `error="content_too_large"`. AR-B1 (no DB-level cap) compensated by workflow-level cap.

### T18 — sha256 + content_bytes invariants
After T1: SQL `SELECT content_hash, content_bytes, octet_length(content) AS db_bytes, encode(digest(content,'sha256'),'hex') AS db_hash FROM agent_build_artifacts WHERE id='<T1 id>'`. **Expected:** `content_bytes = db_bytes` AND `content_hash = db_hash`. (Catches the F6 byte-vs-character regression in the migration's `bld_content_bytes_matches` CHECK.)

## Verification queries

```sql
-- T1 result
SELECT id, version, status, type, name, content_bytes, length(content_hash) AS hash_len
FROM agent_build_artifacts
WHERE task_id = '${SEED_TASK_ID}'
ORDER BY version;

-- T5 lineage
SELECT id, version, parent_artifact_id, root_artifact_id, status
FROM agent_build_artifacts
WHERE task_id = '${SEED_TASK_ID}'
ORDER BY version;
-- expect: v1 parent=NULL root=v1.id; v2 parent=v1.id root=v1.id

-- T18 hash/bytes invariant
SELECT id, content_hash, content_bytes,
       octet_length(content) AS db_bytes,
       encode(digest(content::bytea,'sha256'),'hex') AS db_hash,
       (content_hash = encode(digest(content::bytea,'sha256'),'hex')) AS hash_match,
       (content_bytes = octet_length(content)) AS bytes_match
FROM agent_build_artifacts
WHERE task_id = '${SEED_TASK_ID}';
-- expect: hash_match=true, bytes_match=true for every row

-- agent_memories hook (T1)
SELECT id, agent_name, memory_type, content, metadata
FROM agent_memories
WHERE agent_name='builder_agent'
  AND metadata->>'task_id' = '${SEED_TASK_ID}'
ORDER BY created_at DESC LIMIT 5;

-- idempotency store integrity (T2 vs T3)
SELECT idempotency_key, request_payload_hash,
       (stored_response IS NOT NULL) AS has_stored
FROM agent_build_artifacts
WHERE idempotency_key LIKE 'build-e2e-2026-05-25-%'
ORDER BY created_at;
```

## Codex adversarial review

Run `codex_bridge.py review` (CODEX_MODEL=gpt-5.2) on:
- `AGEN-WKFL-builder-agent-v1.json`
- `AGEN-PRMPT-builder-system-prompt-v1.md`
- `AGEN-TEST-builder-test-plan-v1.md`
- `AGEN-SCRPT-builder-supabase-migration-v1.sql` (already codex-clean through pass 4; re-confirm against the workflow shape)

Iterate fixes until findings = 0. Architecture spawn closed after 9 passes; budget similarly. Track every pass in `audit/claude_codex_loop/AGEN-builder-agent/`.

## Pass criteria

Builder Agent is `ready_for_ship` when ALL of:
- T1–T18 pass against the live deployed workflow.
- Codex review returns zero CRITICAL/HIGH findings.
- `agent_build_artifacts` row from T1 verified via `update_artifact_verification_outcome(<id>, 'verified', NULL)` succeeds without error.
- `doc_controller.py` has registered: `AGEN-WKFL-builder-agent-v1.json` (WF), `AGEN-PRMPT-builder-system-prompt-v1.md` (DOC), this test plan (DOC).
- `agent_sessions` row inserted with `agent_name='builder_agent_builder'`, `status='completed'`, `tasks_completed` including the build steps.
- `agent_tasks.id='641341d9-cb61-4cde-9db3-55cb5e0c5bd9'` is `status='complete'`.
