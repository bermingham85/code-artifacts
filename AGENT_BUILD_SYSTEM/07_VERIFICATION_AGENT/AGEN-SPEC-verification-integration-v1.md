# Verification Agent — Integration Specification

**Document ID:** AGEN-SPEC-verification-integration-v1
**Date:** 2026-05-22

---

## 1. Endpoint

| Field | Value |
|-------|-------|
| URL | `POST http://192.168.50.246:5678/webhook/verification-agent` |
| Transport | HTTP over LAN segment 192.168.50.0/24 (firewalled). Public exposure is **not supported**. |
| Auth | `httpHeaderAuth` n8n credential `APEX Webhook Token` (id `u96A7Xgxemar3STa`) — caller MUST send the bound header. |
| Auth failure | n8n returns `401 Unauthorized` with platform default body. Workflow nodes are NOT invoked. |
| Idempotency | `Idempotency-Key` HTTP header (string ≤ 200 chars). Same key replays the same `verification_id`. |
| Content-Type | `application/json` |
| Anthropic model | Server-side allowlist; default `claude-opus-4-7`. See §6. |
| Codex bridge URL | `APEX_CODEX_BRIDGE_URL` env var on the n8n host. If unset, the workflow records `codex_status="queued"` for offline pickup. |
| Codex callback auth | `X-Apex-Codex-Run-Token` HTTP header that matches `APEX_CODEX_RUN_TOKEN` env var. REQUIRED for `action=codex_callback` and for full-row `get_latest`. Without it, codex_callback returns 401 and get_latest returns the minimal projection only. See AR-V11 and AR-V12. |
| Smoke override auth | `X-Apex-Smoke-Token` HTTP header that matches `APEX_SMOKE_TOKEN` env var. REQUIRED to honor `?skip_codex=true` (used only by the smoke test). See AR-V13. |
| Doc-control URL | `APEX_DOC_CONTROL_URL` env var. When unset, document-control logging is skipped (no fallback URL). |
| n8n payload size | Operator MUST set `N8N_PAYLOAD_SIZE_MAX` on the n8n container (recommended `1mb`). See AR-V9. |

### 1.1 Threat model (LAN-only deployment)

Identical to the Spec Agent's deployment: plain HTTP is acceptable on the firewalled LAN because the host is not internet-reachable, the shared-secret token prevents accidental cross-tool calls, and PII is not present by policy. Two acceptance items remain open and tracked under §10:

- **TM-1.** When this workflow is exposed off-LAN (Tailscale, cloud), the URL MUST switch to HTTPS or mTLS.
- **TM-2.** The shared-secret token MUST be rotated every 90 days minimum.

---

## 2. Actions

### 2.1 `verify` (default action)

Performs a verification of one build artifact against one specification.

```json
{
  "action": "verify",
  "project_id":             "uuid — REQUIRED",
  "spec_id":                "uuid — REQUIRED — must reference an agent_specifications row in status reviewed or approved",
  "task_id":                "uuid — optional",
  "build_artifact_id":      "uuid — optional — references agent_build_artifacts (table not yet provisioned; see AR-V1)",
  "artifact": {
    "ref":     "string — e.g. AGEN-WKFL-foo-workflow-v1.json",
    "kind":    "string — workflow | script | prompt | sql | markdown | config | other",
    "content": "string — ≤ 256 KB; the artifact text/JSON"
  },
  "parent_verification_id": "uuid — optional — for re-verifications",
  "reasoning_effort":       "low | medium | high — optional, default 'high'; passed to codex bridge",
  "requested_by":           "string — optional, ≤ 200 chars; caller identity for audit",
  "notes":                  "string — optional, ≤ 1 KB; operator context"
}
```

**Validation rules (workflow):**

- `project_id` MUST exist in `agent_projects`. Missing → `404 missing_project`.
- `spec_id` MUST exist in `agent_specifications` AND match `project_id` AND have status `reviewed` or `approved`. Other statuses → `422 spec_not_reviewable`.
- `task_id`, if supplied, MUST exist in `agent_tasks` AND match `project_id` AND (if the spec is task-scoped) match the spec's `task_id`. Mismatch → `409 task_project_mismatch` / `spec_task_mismatch`.
- `artifact.content` ≤ 256 KB. Larger → `413 input_too_large`.
- `artifact.ref` must be present and ≤ 200 chars when `artifact` is provided.
- `parent_verification_id`, if supplied, MUST exist in `agent_verifications` with the same `project_id` and `spec_id`. Missing → `404 parent_not_found`. Mismatch → `409 parent_*_mismatch`.
- `Idempotency-Key` ≤ 200 chars. Same key replays the same verification row.

### 2.2 `get_latest`

Returns the most-relevant verification for a `(project_id, spec_id [, task_id])` tuple.

**Resolution: highest `version`, period.** Per AGEN-VRF-SHIP-002 (ship-gate pass 5 finding), `get_latest_verification` returns the highest-version row regardless of its `codex_status`. Consumers (PM Agent) then check `(row.status = 'pass' AND row.codex_status IN ('complete','skipped'))` themselves before advancing a task. This prevents a newer queued/running row from being shadowed by an older terminal row.

- Hit: return the highest-version row (caller inspects `codex_status` and `status` to decide whether the row is gateable).
- Miss: return `{ ok: true, verification_id: null, status: 'not_found' }`.

```json
{ "action": "get_latest", "project_id": "uuid", "spec_id": "uuid", "task_id": "uuid (optional)" }
```

### 2.3 `codex_callback` — owned by the codex async worker (out-of-process)

The codex review worker (running on the Windows host where `codex_bridge.py` lives) calls this action when it completes a queued review. The webhook updates the existing verification row with codex findings.

```json
{
  "action":          "codex_callback",
  "verification_id": "uuid — REQUIRED — the row to update",
  "codex_status":    "complete | failed | skipped — REQUIRED",
  "codex_run_id":    "string — REQUIRED when codex_status='complete'",
  "codex_findings":  "array — REQUIRED when codex_status='complete'; same schema as findings",
  "status_override": "fail | partial — optional; callbacks may ONLY DOWNGRADE the deterministic verdict when codex finds blocking issues (pass is reserved for the deterministic+codex consensus path; skipped/error are workflow-set, not caller-set)",
  "summary_append":  "string — optional, appended to the existing summary with a newline"
}
```

The codex worker authenticates with the same `APEX Webhook Token`. Callbacks for already-terminal rows return `409 codex_pipeline_terminal`.

---

## 3. Response shapes

All responses are JSON.

### 3.1 Successful `verify`

```json
{
  "ok": true,
  "verification_id": "uuid",
  "status":          "pass | fail | partial | skipped",
  "version":         1,
  "reviewer":        "workflow_deterministic",
  "codex_status":    "queued | not_started",
  "findings":        [ /* deterministic findings only — codex findings arrive via codex_callback */ ],
  "summary":         "...",
  "criteria_checked":     ["AC-001", "AC-002"],
  "criteria_unverifiable":["AC-003"],
  "replayed":        false
}
```

`codex_status="not_started"` is returned only when the caller passes `?skip_codex=true` (e.g., for the smoke test). Production callers always see `queued` unless `APEX_CODEX_BRIDGE_URL` returned findings synchronously (in which case `complete`).

### 3.2 `get_latest` hit / miss

Hit:

```json
{ "ok": true, "verification_id": "uuid", "status": "...", "codex_status": "...", "version": int, "verification": { /* row */ } }
```

Miss:

```json
{ "ok": true, "verification_id": null, "status": "not_found" }
```

### 3.3 `codex_callback` success

```json
{ "ok": true, "verification_id": "uuid", "status": "...", "codex_status": "complete | failed | skipped" }
```

### 3.4 Error

```json
{ "ok": false, "error": "<error_code>", "detail": "human-readable detail" }
```

---

## 4. HTTP status code map

| Status | Error code | Meaning |
|--------|-----------|---------|
| 200 | — | Success (including idempotent replay — check `replayed`) |
| 400 | `validation_failed`, `unknown_action` | Bad input shape, missing required field, malformed UUID, unknown action |
| 401 | (n8n default — non-JSON) | Missing/invalid `APEX Webhook Token`. Caller MUST handle non-JSON 401. |
| 404 | `missing_project`, `spec_not_found`, `task_not_found`, `parent_not_found`, `verification_not_found` | Referenced row absent |
| 409 | `spec_project_mismatch`, `task_project_mismatch`, `spec_task_mismatch`, `parent_project_mismatch`, `parent_spec_mismatch`, `codex_pipeline_terminal`, `unique_violation` | Constraint or state-machine violation |
| 413 | `input_too_large` | Artifact > 256 KB or notes > 1 KB |
| 422 | `spec_not_reviewable`, `invalid_status`, `invalid_reviewer`, `invalid_codex_status`, `invalid_reasoning_effort`, `findings_not_array` | Structurally valid input rejected by RPC-level rules |
| 502 | `model_unavailable`, `model_response_not_json`, `model_response_missing_text`, `codex_bridge_unreachable` (when sync mode required) | Anthropic call failed or codex bridge returned an error in sync mode |
| 503 | `db_unavailable` | Postgres unreachable / RPC returned no result |

Retry guidance:
- `502 codex_bridge_unreachable` — workflow auto-falls-back to `codex_status="queued"` and still returns 200 with the deterministic verdict. The 502 is only surfaced when the caller passes `?codex=sync` (smoke-test mode).
- `503 db_unavailable` — retry once after 5s, then fail.
- `4xx` — do not retry.

---

## 5. Database interactions

| Table | Operation | When |
|-------|-----------|------|
| `agent_verifications` | INSERT via `create_verification_record()` RPC | Every `verify` call that produces a non-replay row. |
| `agent_verifications` | UPDATE via `update_verification_codex_outcome()` RPC | Every `codex_callback` call. |
| `agent_verifications` | SELECT via `get_latest_verification()` RPC | `get_latest` action only. |
| `agent_specifications` | SELECT — `id, status, project_id, task_id, body_markdown, requirements, acceptance_criteria, constraints, dependencies, non_goals` | Pre-flight: fetched into the LLM context. Rejected at the door if `status NOT IN ('reviewed','approved')`. |
| `agent_projects` | SELECT count(*) | Existence check before LLM call. |
| `agent_tasks` | SELECT project_id (inside RPC) | When `task_id` is supplied. |
| `agent_memories` | INSERT | After successful verify. `agent_source='verification_agent'` (NOT `agent_name` — that column does not exist). `type='judgement'`. Best-effort: `continueOnFail`. |
| `agent_sessions` | INSERT (operator-driven) | At end of a verification-agent session, the build script writes one row. Not done by the webhook. |
| Document Control endpoint | POST | After successful verify. `continueOnFail`. URL via `APEX_DOC_CONTROL_URL` env (default `http://192.168.50.246:5678/webhook/log-entry`). |

### 5.1 Atomicity

- `create_verification_record()` runs in a single transaction: parent lock (`FOR UPDATE`), version compute, child insert.
- Memory write and Document Control POST are best-effort, post-transaction. Failure of either does not block the response.
- Codex review is async by default — the webhook does not block on it. The deterministic row is returned immediately; codex findings arrive later via `codex_callback`.

---

## 6. Model allowlist

| Model | Default? | Notes |
|-------|----------|-------|
| `claude-opus-4-7` | ✅ | Default for the deterministic-judgement LLM pass |
| `claude-sonnet-4-6` | | Faster, lower cost |
| `claude-haiku-4-5-20251001` | | Cheapest |

Caller-supplied `model` outside the allowlist is silently overridden to the default. Anthropic credential canonical name in n8n is `Anthropic - APEX Live` (id `nOIzouBGfJgCiAE6`); set `header: false` on the credential per ops convention.

Codex reasoning effort: `low | medium | high` (default `high`). Passed to `codex_bridge.py` via the `CODEX_REASONING` env override at invocation time.

---

## 7. Pipeline position

```
Builder Agent  →  Verification Agent  →  Project Manager Agent
                       ↑   ↓
                  Spec Agent / Codex Bridge (recursive review)
```

- The Verification Agent is **read-only** for `agent_projects`, `agent_tasks`, `agent_specifications`, `agent_build_artifacts` (when it exists).
- It is **write-mostly** for `agent_verifications` (insert via RPC; codex worker updates via RPC).
- It is **write-only** to `agent_memories` (best-effort, `agent_source='verification_agent'`).
- PM Agent consumes `agent_verifications` with `codex_status='complete'` AND `status='pass'` to advance a task to `complete`. Rows where `codex_status='skipped'` are NEVER auto-advanced (per AGEN-VRF-SHIP-001 pass-7 fix: any codex-skip callback that lands on a deterministic-pass row forces the row's status to `partial`, so PM Agent's `pass`-gate refuses to advance). Operator-attested skip with manual advancement is a separate, audited PM Agent path.

---

## 8. Prerequisites for activation

1. Migration `AGEN-SCRPT-verification-supabase-migration-v1.sql` applied (creates table + RPCs + RLS + grants).
2. n8n credentials present:
   - `APEX Webhook Token` (`httpHeaderAuth`, id `u96A7Xgxemar3STa`).
   - `Anthropic - APEX Live` (`anthropicApi`, id `nOIzouBGfJgCiAE6`, `header: false`).
   - `Supabase Novel Writer` (`postgres`, id `tk7Z3R3l1dUwRnmu`).
3. n8n workflow imported, `REPLACE_AT_IMPORT` placeholders bound to real credential IDs (the JSON ships the canonical ids inline where stable).
4. Workflow set **inactive** until smoke test §9 passes; activate after.
5. (Optional) `APEX_CODEX_BRIDGE_URL` env var set on the n8n host pointing at a sidecar HTTP service that wraps `codex_bridge.py`. Until that sidecar exists the workflow records `codex_status="queued"`. The deterministic row is still returned.
6. (Optional) Codex review worker running on the Windows codex host, polling Supabase for `codex_status="queued"` rows and calling `/webhook/verification-agent` with `action="codex_callback"`. Tracked as follow-on **F-V1** below.

---

## 9. Smoke test (required before activation)

| Step | Pass criterion |
|------|----------------|
| 9.1 | `POST /webhook/verification-agent` without auth header → HTTP 401. |
| 9.2 | `POST /webhook/verification-agent` with auth, body `{}` → HTTP 400 `validation_failed`. |
| 9.3 | `POST` with auth, body `{"action":"verify","project_id":"<AGEN-uuid>","spec_id":"50ca6d79-..."}` and `artifact={ref:"smoke-test",kind:"markdown",content:"# clean artifact passing all criteria"}` → HTTP 200, row visible in `agent_verifications`, `status ∈ {pass,partial,skipped}` (smoke test uses a known-good spec), `codex_status='queued'`. |
| 9.4 | Same body + `Idempotency-Key: verify-<project_id>-<spec_id>-smoke-9-4-<run-id>` (scope-prefixed per workflow validator) → HTTP 200 `replayed:false`. Resend → HTTP 200 `replayed:true` same `verification_id`. |
| 9.5 | `get_latest` for that `(project_id, spec_id)` → returns the row from 9.3. |
| 9.6 | `codex_callback` with `verification_id` from 9.3, `codex_status="complete"`, `codex_findings=[]` → HTTP 200, row's `codex_status="complete"`. |
| 9.7 | Second `codex_callback` for the same row → HTTP 409 `codex_pipeline_terminal`. |

Any 9.x failing → workflow stays inactive; investigate.

---

## 9.8 Accepted-risk register

| ID | Risk | Compensating control | Re-evaluate when |
|----|------|---------------------|------------------|
| AR-V1 | `build_artifact_id` has no FK because `agent_build_artifacts` is not yet provisioned. Stale or invalid uuids accepted. | Builder Agent build provisions the table and a follow-on migration adds the FK. Today's verification rows carry the uuid for forward compatibility. | Builder Agent build complete. |
| AR-V2 | Codex review is async; the deterministic webhook response can mark `pass` before codex has reviewed. PM Agent's contract is to wait for `codex_status IN ('complete','skipped')` before advancing tasks — but that contract is unenforced today. | PM Agent build will enforce. Until then, operators verify codex completion before manually advancing. | PM Agent build complete + integration tested. |
| AR-V3 | Idempotency key globally unique; cross-context replay possible if callers re-use a key. | Prefix keys with `verify-{project_id}-{spec_id}-{nonce}`. Documented in §2.1. | Move to composite (project_id, key) unique index when concrete cost observed. |
| AR-V4 | LAN-only HTTP token-bearer auth — same exposure profile as the Spec Agent. | Token rotation every 90 days; firewall isolation. | Off-LAN exposure required (TM-1). |
| AR-V5 | Verification Agent does NOT execute the spec's `binary_check` commands — it reasons about whether the artifact COULD pass them. False positives possible (artifact looks right but fails at runtime). | Codex adversarial review and downstream integration tests catch runtime failures. PM Agent's terminal pass gate is `codex_status="complete" AND status="pass"`. | Builder Agent integration tests cover the binary_check execution path. |
| AR-V6 | The Verification Agent reads spec content into the LLM context — large specs (close to 32 KB) plus large artifacts (256 KB cap) can push the LLM context near the Anthropic per-call limit. | Spec body capped at 32 KB by Spec Agent design; artifact cap at 256 KB. Combined ≤ 288 KB, well inside Claude's window. | Artifact cap raised. |
| AR-V7 | Codex bridge invocation is HTTP-async via a sidecar that does not yet exist. Workflow gracefully degrades to `codex_status="queued"` but the recursive verification REQUIREMENT (Doctrine A4) is not realised until the worker runs. | A1) `codex_status="queued"` is queryable, so a manual `codex_bridge.py adversarial-review` run + `codex_callback` POST satisfies the contract today. A2) Follow-on task **F-V1** stands up the sidecar. | F-V1 closed. |
| AR-V8 | The deterministic Claude pass on this agent is itself a Claude call — and Doctrine A4 forbids Claude self-review. Mitigation: the prompt explicitly forbids this Claude from marking `pass` without the codex sentence; the codex worker is the canonical reviewer and is always queued. | Documented in the system prompt Rule 11. The recursive codex review IS the adversary. | If Doctrine A4 is amended to require synchronous codex co-pass, switch the workflow to `?codex=sync` default and remove the queue path. |
| AR-V9 | Application-level total body size cap (320 KB) runs **after** n8n has parsed the JSON body, so it cannot protect the parser memory itself from oversized payloads. | Operator MUST set `N8N_PAYLOAD_SIZE_MAX` on the n8n container (recommended: `1mb`) to bound parser memory at ingress. Workflow-level cap stays as a defence-in-depth band. | n8n exposes pre-parse byte gate, OR ingress proxy enforces the limit. |
| AR-V10 | `Fire Codex Async (Optional)` is best-effort and `onError=continueRegularOutput`; a transient failure of the sidecar leaves the row in `codex_status='queued'` indefinitely. | The codex worker sidecar (F-V1) MUST poll Supabase for `codex_status='queued'` rows on a 60s cadence as the authoritative dispatch mechanism — Fire Codex is just an optimistic wake-up. `idx_agent_verifications_codex_status` partial index supports the queue scan. Operator alert is exposed when the queue scan returns rows older than the configured threshold. | Sidecar deployed (F-V1 closed). |
| AR-V11 | `get_latest` returns only the minimal projection (id, status, codex_status, version, finding count, timestamps) to callers presenting the shared webhook token. Callers wishing to retrieve `summary`/`findings`/full row MUST also present `X-Apex-Codex-Run-Token`. PM Agent is expected to operate on the minimal projection. | The codex-run token is the second-factor for substantive content reads, matching the codex_callback auth model. | Per-project authz lands (F-V4). |
| AR-V12 | `codex_callback` requires `X-Apex-Codex-Run-Token` header that matches env `APEX_CODEX_RUN_TOKEN`. Without it, callbacks return `401 codex_callback_unauthorized`. Operators must keep the env-set token and the sidecar-side configuration in sync. | Token rotation MUST be done atomically on both sides. If the env is unset, codex_callback is unreachable — the integration is intentionally fail-closed. | Sidecar adopts a per-run-id signed-payload model (F-V5, new). |
| AR-V13 | `?skip_codex=true` is honored ONLY when caller presents `X-Apex-Smoke-Token` header that matches env `APEX_SMOKE_TOKEN`. When the env is unset, skip_codex is unreachable — production traffic always queues codex review. | The smoke token is held only by the build/smoke-test runner. The codex-pending sentence and recursive review contract (Doctrine A4) are never weakened. | Smoke harness migrates to a separate dedicated webhook path with its own credentials. |

---

## 10. Known follow-on items

- **F-V1** Codex review worker sidecar (Windows host) — polls Supabase for `codex_status='queued'`, runs `codex_bridge.py adversarial-review`, posts `codex_callback`. Not built in this WO; tracked as a new AGEN task.
- **F-V2** Add FK on `build_artifact_id` once Builder Agent provisions `agent_build_artifacts`.
- **F-V3** PM Agent contract enforcement: PM may only advance a task when its latest verification has `codex_status='complete' AND status='pass'`.
- **F-V4** `agent_routing_logs` not yet provisioned — Router Agent build owns it. Verification calls are not logged there today.
- **F-V5** Memory writes use the canonical `agent_source` column (not the deprecated `agent_name`). If `agent_memories` schema is later normalised to include `agent_name`, the workflow's memory node must be updated atomically with that migration.
- **F-V6** The deterministic Claude pass currently uses the Anthropic credential `nOIzouBGfJgCiAE6`. If the operator's billing topup is exhausted mid-run, the workflow returns `502 model_unavailable` and the verification row is NOT created (caller retries). Add a circuit-breaker once outages are observed.
