# Specification Agent — Integration Specification

**Document ID:** AGEN-SPEC-spec-integration-v1
**Date:** 2026-05-05 (round 2 — adversarial review pass 1 closed)

---

## 1. Endpoint

| Field | Value |
|-------|-------|
| URL | `POST http://192.168.50.246:5678/webhook/specification-agent` |
| Transport | HTTP over LAN segment 192.168.50.0/24 (firewalled). Public exposure is **not supported**. |
| Auth | `httpHeaderAuth` n8n credential `APEX Webhook Token` — caller MUST send the bound header. |
| Auth failure | n8n returns `401 Unauthorized` with platform default body. The workflow nodes are NOT invoked. |
| Idempotency | `Idempotency-Key` HTTP header (string ≤ 200 chars). Same key replays the same `spec_id` for the lifetime of the row. |
| Content-Type | `application/json` |
| Anthropic model | Server-side allowlist (see §6). Caller-supplied `model` field is ignored unless in the allowlist. |
| n8n Workflow ID | TBD on import. Operators record the assigned ID in this file at v1.1. |
| Default Anthropic model | `claude-opus-4-7` |

The PM Agent uses webhook path `/project-manager` with workflow ID `fbsjuiji61RErVfJ` (canonical, per `AGEN-SPEC-pm-integration-v1.md`). The duplicate workflow `e5iHgzesGAHIEsPd` is **non-canonical** and should be archived in a follow-up housekeeping task.

### 1.1 Threat model (LAN-only deployment)

Plain HTTP is acceptable on the firewalled LAN because (a) the host is not internet-reachable, (b) the shared-secret token prevents accidental cross-tool calls, (c) PII is not present in spec inputs by policy. Two acceptance items remain open:

- **TM-1.** When the workflow is moved off-LAN (Tailscale, cloud), the URL MUST switch to HTTPS or mTLS. Builder Agent owns this transition.
- **TM-2.** The shared-secret token MUST be rotated whenever a contributor leaves the project. Rotation cadence: every 90 days minimum.

---

## 2. Actions

### 2.1 `clarify_or_spec` (default action)

Produces a spec or a clarification round.

```json
{
  "action": "clarify_or_spec",
  "request":         "string — REQUIRED unless answers is supplied",
  "project_id":      "uuid — REQUIRED",
  "task_id":         "uuid — optional",
  "answers":         "string|object — optional, supplies answers to a previous question_set",
  "parent_spec_id":  "uuid — optional, supplied when revising an existing spec",
  "notes":           "string — optional, max 1 KB; operator context"
}
```

**Validation rules (workflow):**

- `project_id` MUST exist in `agent_projects`. Missing → `404 missing_project`.
- `task_id`, if supplied, MUST exist in `agent_tasks` AND its `project_id` MUST match the request's `project_id`. Missing task → `404 task_not_found`. Project mismatch → `409 task_project_mismatch`. (Enforced inside the RPC.)
- `parent_spec_id`, if supplied, MUST exist and have the same `project_id` AND the same `task_id` (NULL on either side counts as a mismatch). Mismatches → `409 parent_project_mismatch` / `parent_task_mismatch`. Missing parent → `404 parent_not_found`.
- `request + answers` combined byte length ≤ 32 KB. Larger inputs → `413 input_too_large`.
- `notes`, if supplied, ≤ 1 KB.
- `model` field, if supplied, is silently overridden when not in the allowlist (§6).
- `Idempotency-Key` header ≤ 200 chars. Same key replays the same `spec_id`. The key is **globally unique** (not project-scoped); choose keys that include a project/run/operation prefix to avoid accidental cross-context collisions (e.g., `proj-{uuid}-{op}-{nonce}`).

### 2.2 `get_latest`

Returns the most-relevant current spec for a `(project_id, task_id?, root_spec_id?)` lineage. Resolution order:

1. Highest `version` row with `status IN ('reviewed','approved')` — this is the canonical "current spec" for downstream agents.
2. If none exists, the most recent `status='needs_clarification'` row — this signals to the caller that the spec is in flight, not stable.
3. Otherwise `not_found`.

**Important caller contract:** Architecture and Builder agents MUST consume only `reviewed` or `approved` results. If `get_latest` returns `needs_clarification`, downstream agents MUST refuse to act and instead route the user back to the Spec Agent. Failure to honour this contract is a Verification Agent finding.

```json
{ "action": "get_latest", "project_id": "uuid", "task_id": "uuid (optional)", "root_spec_id": "uuid (optional)" }
```

`task_id` and `root_spec_id` may be supplied together. If they conflict (e.g., the requested root spec belongs to a different task), the result reflects whichever filter is more restrictive — the function ANDs all supplied filters; no error is returned for "incompatible" filters because the empty result IS the contract.

### 2.3 Approval — owned by Project Manager Agent (NOT this endpoint)

The Spec Agent does NOT expose an `approve` action. Approval is a PM-only state transition. To approve a spec:

```
POST /webhook/project-manager  { "action": "approve_spec", "spec_id": "...", "approver_session_id": "..." }
```

The PM Agent calls the `approve_specification(spec_id, approver)` Postgres RPC (defined in this migration) after verifying the approver's PM-role permission. The Spec Agent's webhook will return `400` `unknown_action` if `action="approve"` is sent here.

---

## 3. Response shapes

All responses are JSON. HTTP status codes are stable (see §4).

### 3.1 Successful spec produced (`clarify_or_spec` → reviewed/needs_clarification)

```json
{
  "ok": true,
  "spec_id": "uuid",
  "status": "reviewed | needs_clarification",
  "version": 1,
  "title": "...",
  "spec": { "...full spec document — see system prompt..." },
  "questions": ["..."],
  "validation_issues": [],
  "memory_id": "uuid|null",
  "replayed": false
}
```

`replayed=true` indicates the row was returned via `idempotency_key` match — no new write, no new memory.

### 3.2 `get_latest` hit / miss

Hit:

```json
{ "ok": true, "spec_id": "uuid", "status": "reviewed|approved|needs_clarification", "version": int, "title": "...", "spec": { /* row */ } }
```

Miss:

```json
{ "ok": true, "spec_id": null, "status": "not_found" }
```

### 3.3 Error

```json
{ "ok": false, "error": "<error_code>", "detail": "human-readable detail" }
```

---

## 4. HTTP status code map

| Status | Error code | Meaning |
|--------|-----------|---------|
| 200 | — | Success (including idempotent replay; check `replayed` field) |
| 400 | `validation_failed`, `unknown_action` | Bad input shape, missing required field, malformed UUID, unknown action |
| 401 | (n8n default — non-JSON) | Missing/invalid `APEX Webhook Token`. Note: this 401 body comes from n8n's webhook auth and does NOT match the standard JSON envelope. Callers must handle 401 specially. |
| 404 | `missing_project`, `task_not_found`, `parent_not_found` | A referenced row does not exist |
| 409 | `task_project_mismatch`, `parent_project_mismatch`, `parent_task_mismatch`, `parent_approved_requires_pm_supersede`, `lineage_version_race`, `unique_violation` | Constraint or lineage violation |
| 413 | `input_too_large` | request + answers > 32 KB |
| 422 | `invalid_status`, `approver_required_for_approved` | RPC-level rejection of a structurally valid request |
| 502 | `model_unavailable`, `model_response_not_json`, `model_response_missing_text` | Anthropic call failed or returned malformed output |
| 503 | `db_unavailable` | Postgres unreachable / RPC threw a non-result error |

The model-allowlist policy is **silent override**, not rejection — disallowed `model` values are replaced with the server default and processing continues. There is no `400 banned_model` error.

Retry guidance:
- `502 model_unavailable` — exponential backoff, max 3 retries, surface to user after.
- `503 db_unavailable` — retry once after 5s; then fail.
- `4xx` — do NOT retry; fix the request.

---

## 5. Database interactions

| Table | Operation | When |
|-------|-----------|------|
| `agent_specifications` | INSERT via `create_specification_revision()` RPC | Every `clarify_or_spec` call that produces a non-replay row. |
| `agent_specifications` | UPDATE … `status='superseded'` | Inside the RPC, when a `reviewed`/`approved` revision lands and parent is held under `FOR UPDATE`. |
| `agent_specifications` | SELECT via `get_latest_specification()` RPC | `get_latest` action only. |
| `agent_specifications` | UPDATE … `status='approved', approved_by, approved_at` | Owned by PM Agent's webhook only. Spec Agent never calls `approve_specification()`. |
| `agent_projects` | SELECT count(*) | Existence check before LLM call; refuses if not found. |
| `agent_tasks` | SELECT project_id (inside RPC) | When `task_id` is supplied, the RPC verifies the task exists and its `project_id` matches. |
| `agent_memories` | INSERT | After successful spec write. `memory_type='decision'` for `reviewed`, `'question_set'` for `needs_clarification`. Best-effort: `continueOnFail` so a memory failure does not block the response. |
| `agent_routing_logs` | (no write) | **Deferred** — table not yet provisioned. Router Agent build owns it. |
| Document Control endpoint | POST | After successful spec write. `continueOnFail` because `agent_logs` is not yet provisioned. Endpoint URL is configurable via env `APEX_DOC_CONTROL_URL`. |

### 5.1 Atomicity

- The `create_specification_revision()` RPC runs in a single transaction: parent lock (`FOR UPDATE`), version compute, parent supersede (if applicable), child insert.
- Memory write and Document Control POST are **best-effort, post-transaction**. If they fail, the spec row is still returned. The response includes `memory_id: null` to signal partial completion. Operators reconcile via the agent_specifications row + (eventually) agent_logs.

---

## 6. Model allowlist

| Model | Default? | Notes |
|-------|----------|-------|
| `claude-opus-4-7` | ✅ | Strongest reasoning, slowest, highest cost |
| `claude-sonnet-4-6` | | Faster, lower cost |
| `claude-haiku-4-5-20251001` | | Cheapest, weakest reasoning |

Caller-supplied `model` outside this list is silently ignored — the default is used. Anthropic credential canonical name in n8n is `Anthropic account` (Builder Agent: confirm and pin id in `GOVERNANCE.md` Rule 9).

---

## 7. Pipeline position

```
Router Agent  →  Specification Agent  →  Architecture Agent
                       ↑   ↓
                Memory Agent  /  Project Manager
```

- The Spec Agent is **read-only** for `agent_projects` / `agent_tasks` (validation only).
- It is **write-mostly** for `agent_specifications` (insert + supersede via RPC).
- It is **write-only** to `agent_memories` (decision / question_set rows). Memory reads, when added, will be filtered by project_id.
- Architecture Agent consumes specs in status `reviewed` or `approved`. Specs in `needs_clarification` / `draft` / `blocked` MUST NOT be consumed by Architecture; the workflow does not enforce this — it's a contract Architecture Agent must obey.

---

## 8. Prerequisites for activation

1. Migration `AGEN-SCRPT-spec-supabase-migration-v1.sql` applied successfully (creates table, RPCs, RLS, grants, trigger).
2. n8n credentials present:
   - `APEX Webhook Token` (`httpHeaderAuth`) — for Webhook node.
   - `Anthropic account` (`anthropicApi`) — for Anthropic Claude node.
   - `Postgres - Agent System` (`postgres`, id `1Prz5GUFcAMM2Dv1`) — for all DB nodes.
3. n8n workflow imported, `REPLACE_AT_IMPORT` placeholders bound to real credential IDs.
4. Workflow set **inactive** until smoke test (§9) passes; only then activate.
5. `agent_logs` table or alternative log sink — silent-fail tolerated until Builder Agent provisions it. Operational risk acceptance recorded under task `f9aa8008-aa3f-4627-976f-ae8783d12783`.

---

## 9. Smoke test (required before activation)

| Step | Pass criterion |
|------|----------------|
| 9.1 | `POST /webhook/specification-agent` without auth header → HTTP 401. |
| 9.2 | `POST /webhook/specification-agent` with auth, body `{}` → HTTP 400 `validation_failed`. |
| 9.3 | `POST` with auth, body `{"action":"clarify_or_spec","project_id":"<test-uuid>","request":"build a webhook returning 200 to GET /ping with a 50ms p95"}` → HTTP 200, `status` ∈ {`reviewed`,`needs_clarification`}, row visible in `agent_specifications`. |
| 9.4 | Same body with `Idempotency-Key: smoke-9-4` → HTTP 200, `replayed: false`. Resend → HTTP 200, `replayed: true`, same `spec_id`. |
| 9.5 | `POST` with auth + `{"action":"get_latest","project_id":"<test-uuid>"}` → returns the 9.3 row. |

Any 9.x failing → workflow stays inactive; Builder Agent investigates.

---

## 9.6 Accepted-risk register

These risks are **known and accepted** for the v1 LAN-only deployment of this workflow. They are not bugs to be re-flagged in adversarial review — they are documented residuals with named compensating controls. Migration to a public-facing or off-LAN deployment requires re-evaluating each.

| ID | Risk | Compensating control | Re-evaluate when |
|----|------|---------------------|------------------|
| AR-1 | Plain HTTP transport on LAN exposes token + body to compromised hosts on the same segment. | Webhook segment is firewalled (no inbound from internet); n8n host hardened by Builder Agent. Token rotation every 90 days. | Workflow exposed via Tailscale, cloud, or off-LAN — switch to HTTPS / mTLS at that point (TM-1). |
| AR-2 | Token bearer can call any project — no per-project authz. | Token is operator-distributed (not user-distributed) and held only by trusted automation services (PM Agent, Architecture Agent, Verification Agent). | Per-project authentication model exists (Router/PM milestone) — add project-membership check (F7). |
| AR-3 | Architecture Agent's "consume only reviewed/approved" rule is a contract, not enforced by the Spec workflow. | Verification Agent will assert this contract in its build (Step 7). | Verification Agent build complete. |
| AR-4 | Document Control logger 500s silently because `agent_logs` table absent. | `continueOnFail` keeps spec creation flowing; reconciliation via `agent_specifications` itself. | Builder Agent provisions `agent_logs` (task `f9aa8008-…`). |
| AR-5 | Idempotency key is globally unique — accidental cross-context reuse returns the wrong row. | Caller responsibility to use prefixed keys (e.g. `proj-{uuid}-{op}-{nonce}`). Documented in §2.1. | Move idempotency_key to a composite (project_id, key) unique index when concrete cost is observed. |
| AR-6 | Highest-cost model (`claude-opus-4-7`) is default; no rate limit at the workflow level. | n8n's per-workflow execution timeout (60s on the LLM call) caps single-call cost. Anthropic's account-level rate limits cap aggregate. Token-leak detection happens at rotation. | Concurrent workflow execution > 5/min observed sustained. Add explicit rate limit at that point. |
| AR-7 | Migration's pre-flight column check verifies schema names but not types/nullability — drift in types passes. | The RPCs use explicit `::uuid`/`::jsonb` casts and the JSONB CHECK constraints catch shape errors at write time. | Periodic migration audit (every minor version bump) compares live schema to the migration file. |
| AR-8 | Revision requests with `parent_spec_id` do not pre-fetch the parent's content into the LLM context. The model receives only the parent UUID, so any "diff vs parent" summary may be incomplete. | Caller convention: include the relevant parent excerpt in `answers` when refining; the system prompt's revision rule explicitly states this expectation. | Architecture Agent or a workflow update that fetches parent body before the LLM call (cost-aware — parent body is currently up to ~32 KB). |

## 10. Known follow-on items

- **F1** `agent_routing_logs` table missing — Router Agent build creates it.
- **F2** Duplicate PM Agent workflow `e5iHgzesGAHIEsPd` should be archived; canonical is `fbsjuiji61RErVfJ`.
- **F3** `agent_logs` table missing — task `f9aa8008-…`.
- **F4** Anthropic credential id is `REPLACE_AT_IMPORT` placeholder; bind on import; pin in GOVERNANCE.md Rule 9 once stable.
- **F5** `doc_controller.py` (`APEX-MB-PY-00000`) needs `--bump` after `VALID_PROJECTS` expansion.
- **F6** `claudex-plan-loop` muscle absorption (project GOVN) — once registered, future builds prefer Path A.
- **F7** Per-project authentication for `agent_specifications` reads — currently service_role only. Enable when project membership model exists.
- **F8** TM-1 / TM-2 (see §1.1) — HTTPS migration + token rotation cadence.
