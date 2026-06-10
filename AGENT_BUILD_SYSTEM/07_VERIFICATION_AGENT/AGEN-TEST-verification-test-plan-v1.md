# Verification Agent — Test Plan

**Document ID:** AGEN-TEST-verification-test-plan-v1
**Date:** 2026-05-22

---

## 0. Conventions

- Each test has a deterministic, binary `pass_check` — a SQL query, a JSON-path assertion, or an exit code. No "looks reasonable" judgements.
- All tests run against Supabase project `ylcepmvbjjnwmzvevxid` and the n8n local instance on `192.168.50.246:5678`.
- Migration `AGEN-SCRPT-verification-supabase-migration-v1.sql` MUST have been applied.
- A unique-per-run test project + test spec is created so concurrent runs do not collide and cleanup never touches anything outside the run.
- Curl invocations use `--show-error --silent --max-time 90` (deliberately not `--fail` because several tests assert 4xx) and capture both body and status.
- All curl invocations send the auth header `-H "X-APEX-Webhook-Token: $APEX_TOKEN"` from the operator's env.
- LLM and codex behaviour is non-deterministic. Tests assert on **structural** outcomes — status enum, row presence, lineage shape, finding count parity. They do NOT assert on specific finding text.

## Setup helpers

```bash
RUN_ID=$(date +%s)-$RANDOM
TEST_CODE="AGEN-VTEST-$RUN_ID"
APEX_TOKEN=${APEX_TOKEN:?env var required}
WEBHOOK="http://192.168.50.246:5678/webhook/verification-agent"
PSQL="psql -h db.ylcepmvbjjnwmzvevxid.supabase.co -U postgres -d postgres -t -A"

post() {
  local body="$1"; local idem="${2:-}"
  local hdr=(-H "Content-Type: application/json" -H "X-APEX-Webhook-Token: $APEX_TOKEN")
  [[ -n "$idem" ]] && hdr+=(-H "Idempotency-Key: $idem")
  curl --show-error --silent --max-time 90 -w '\nHTTP_STATUS:%{http_code}\n' "${hdr[@]}" -d "$body" "$WEBHOOK"
}

# codex_callback path requires the codex-run token. Operator sets APEX_CODEX_RUN_TOKEN in
# the env that runs this test plan AND in the n8n host env (APEX_CODEX_RUN_TOKEN). Without
# it, codex_callback returns 401 codex_callback_unauthorized and T9 will fail (by design).
post_codex_callback() {
  local body="$1"
  : "${APEX_CODEX_RUN_TOKEN:?env var required for codex_callback tests}"
  curl --show-error --silent --max-time 90 -w '\nHTTP_STATUS:%{http_code}\n' \
    -H "Content-Type: application/json" \
    -H "X-APEX-Webhook-Token: $APEX_TOKEN" \
    -H "X-Apex-Codex-Run-Token: $APEX_CODEX_RUN_TOKEN" \
    -d "$body" "$WEBHOOK"
}

body_of()   { echo "$1" | sed '/^HTTP_STATUS:/d'; }
status_of() { echo "$1" | awk -F: '/^HTTP_STATUS:/{print $2}' | tr -d '\r\n '; }
```

## T0 — Setup: project + reviewed spec

```sql
-- 0.1 project
INSERT INTO agent_projects (code, name, status)
VALUES ('${TEST_CODE}', 'Verification Agent Test Project', 'planning')
RETURNING id;
-- save as $PROJECT_ID

-- 0.2 minimal reviewed spec with 3 acceptance criteria
SELECT create_specification_revision(
  '${PROJECT_ID}'::uuid, NULL,
  'VTEST spec',
  'Smoke spec for verification agent',
  '## Acceptance\n- AC-001 must pass\n- AC-002 must pass\n- AC-003 must pass',
  '[{"id":"REQ-001","description":"endpoint /ping returns 200","priority":"must","acceptance_criterion_id":"AC-001"},
    {"id":"REQ-002","description":"endpoint /pong returns 201","priority":"must","acceptance_criterion_id":"AC-002"},
    {"id":"REQ-003","description":"endpoint /ding returns 204","priority":"must","acceptance_criterion_id":"AC-003"}]'::jsonb,
  '[{"id":"AC-001","given":"server running","when":"GET /ping","then":"200 returned","binary_check":"curl -s -o /dev/null -w %{http_code} http://x/ping == 200"},
    {"id":"AC-002","given":"server running","when":"POST /pong","then":"201 returned","binary_check":"curl -s -o /dev/null -w %{http_code} -X POST http://x/pong == 201"},
    {"id":"AC-003","given":"server running","when":"GET /ding","then":"204 returned","binary_check":"curl -s -o /dev/null -w %{http_code} http://x/ding == 204"}]'::jsonb,
  '[]'::jsonb, '[]'::jsonb, '["No auth required for the test endpoints"]'::jsonb, '[]'::jsonb,
  NULL, 'reviewed', NULL, 'vtest-${RUN_ID}-spec', NULL
);
-- save returned spec.id as $SPEC_ID
```

`pass_check`:

```sql
SELECT (count(*) = 1)
FROM agent_specifications WHERE id = '${SPEC_ID}'
  AND status = 'reviewed'
  AND jsonb_array_length(acceptance_criteria) = 3;
```

---

## T1 — Auth: missing token rejected

```bash
HTTP=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -X POST "$WEBHOOK" \
  -H 'Content-Type: application/json' \
  -d '{"action":"verify","project_id":"00000000-0000-0000-0000-000000000000","spec_id":"00000000-0000-0000-0000-000000000000"}')
[[ "$HTTP" == "401" ]]
```

---

## T2 — Validation: empty JSON body rejected

```bash
RESP=$(post '{}')
[[ "$(status_of "$RESP")" == "400" ]]
body_of "$RESP" | jq -e '.ok == false and .error == "validation_failed"' >/dev/null
```

---

## T3 — Clean spec+artifact → pass (deterministic)

The artifact claims to implement all three endpoints with correct status codes; no placeholder markers.

```bash
ARTIFACT='# Clean implementation\n\n## GET /ping\nReturns HTTP 200 with body "pong".\n\n## POST /pong\nReturns HTTP 201 with body containing id of created resource.\n\n## GET /ding\nReturns HTTP 204 with empty body.\n\nNo TODOs. No placeholders. All three endpoints documented and implemented.'
BODY=$(jq -n --arg p "$PROJECT_ID" --arg s "$SPEC_ID" --arg a "$ARTIFACT" '{
  action: "verify", project_id: $p, spec_id: $s,
  artifact: { ref: "T3-clean-artifact", kind: "markdown", content: $a },
  requested_by: "vtest-T3"
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
T3_VID=$(echo "$BODY_JSON" | jq -r '.verification_id')
[[ "$(status_of "$RESP")" == "200" ]]
echo "$BODY_JSON" | jq -e '.ok==true and (.status=="pass" or .status=="partial") and (.codex_status=="queued" or .codex_status=="not_started" or .codex_status=="complete") and (.findings|type=="array")' >/dev/null
[[ -n "$T3_VID" && "$T3_VID" != "null" ]]
```

DB invariants:

```sql
SELECT 1 FROM agent_verifications
WHERE id = '${T3_VID}'
  AND spec_id = '${SPEC_ID}'
  AND project_id = '${PROJECT_ID}'
  AND status IN ('pass','partial')
  AND reviewer = 'workflow_deterministic'
  AND codex_status IN ('not_started','queued','complete')
  AND jsonb_typeof(findings) = 'array';
-- expect: 1 row
```

---

## T4 — Broken artifact → fail with structured findings

The artifact contains a `TODO` and is missing the third endpoint entirely.

```bash
ARTIFACT='# Broken implementation\n\n## GET /ping\nReturns 200 OK.\n\n## POST /pong\n// TODO: implement this — currently returns 500.\nreturn null;\n\n## GET /ding\n<insert handler here>'
BODY=$(jq -n --arg p "$PROJECT_ID" --arg s "$SPEC_ID" --arg a "$ARTIFACT" '{
  action: "verify", project_id: $p, spec_id: $s,
  artifact: { ref: "T4-broken-artifact", kind: "markdown", content: $a },
  requested_by: "vtest-T4"
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
T4_VID=$(echo "$BODY_JSON" | jq -r '.verification_id')
[[ "$(status_of "$RESP")" == "200" ]]
echo "$BODY_JSON" | jq -e '.ok==true and (.status=="fail" or .status=="partial") and (.findings|length>=1) and ([.findings[].severity] | any(. == "critical" or . == "high" or . == "medium"))' >/dev/null
```

DB:

```sql
SELECT 1 FROM agent_verifications
WHERE id = '${T4_VID}'
  AND status IN ('fail','partial')
  AND jsonb_array_length(findings) >= 1
  AND EXISTS (
    SELECT 1 FROM jsonb_array_elements(findings) f
    WHERE f->>'severity' IN ('critical','high','medium')
  );
-- expect: 1 row
```

---

## T5 — Partial coverage → status=partial

The artifact implements 2 of 3 endpoints correctly, with no placeholder markers, and explicitly notes the third is deferred.

```bash
ARTIFACT='# Partial implementation\n\n## GET /ping\nReturns HTTP 200 with body "pong". Implemented and tested.\n\n## POST /pong\nReturns HTTP 201 with body containing id. Implemented and tested.\n\n## GET /ding\nDEFERRED to next milestone — not in scope of this artifact.'
BODY=$(jq -n --arg p "$PROJECT_ID" --arg s "$SPEC_ID" --arg a "$ARTIFACT" '{
  action: "verify", project_id: $p, spec_id: $s,
  artifact: { ref: "T5-partial-artifact", kind: "markdown", content: $a },
  requested_by: "vtest-T5"
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
T5_VID=$(echo "$BODY_JSON" | jq -r '.verification_id')
[[ "$(status_of "$RESP")" == "200" ]]
# Either partial (criterion unverifiable for /ding) or fail (criterion observably unmet).
echo "$BODY_JSON" | jq -e '.ok==true and (.status=="partial" or .status=="fail")' >/dev/null
# At least AC-003 should appear in findings or in criteria_unverifiable.
echo "$BODY_JSON" | jq -e '((.criteria_unverifiable // []) | length > 0) or ([.findings[].criterion_id // ""] | any(. == "AC-003"))' >/dev/null
```

DB:

```sql
SELECT 1 FROM agent_verifications
WHERE id = '${T5_VID}'
  AND status IN ('partial','fail');
-- expect: 1 row
```

---

## T6 — Idempotency-Key replays the same verification_id

```bash
KEY="verify-${PROJECT_ID}-${SPEC_ID}-t6-${RUN_ID}"
ARTIFACT='# trivial idempotency check artifact — three endpoints, all implemented, no placeholders.'
BODY=$(jq -n --arg p "$PROJECT_ID" --arg s "$SPEC_ID" --arg a "$ARTIFACT" '{
  action: "verify", project_id: $p, spec_id: $s,
  artifact: { ref: "T6-idem-artifact", kind: "markdown", content: $a }
}')
R1=$(post "$BODY" "$KEY"); R2=$(post "$BODY" "$KEY")
[[ "$(status_of "$R1")" == "200" ]]
[[ "$(status_of "$R2")" == "200" ]]
ID1=$(body_of "$R1" | jq -r '.verification_id')
ID2=$(body_of "$R2" | jq -r '.verification_id')
REPLAYED2=$(body_of "$R2" | jq -r '.replayed')
[[ -n "$ID1" && "$ID1" != "null" ]]
[[ "$ID1" == "$ID2" && "$REPLAYED2" == "true" ]]
```

DB:

```sql
SELECT count(*) = 1 FROM agent_verifications WHERE idempotency_key = '${KEY}';
```

---

## T7 — Spec not reviewable → 422

Create a `needs_clarification` spec; verification must be rejected.

```sql
SELECT create_specification_revision(
  '${PROJECT_ID}'::uuid, NULL,
  'VTEST needs-clarification spec',
  'rejected by verifier',
  'TBD',
  '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb, '[]'::jsonb,
  '["what is the metric"]'::jsonb, NULL,
  'needs_clarification', NULL, 'vtest-${RUN_ID}-nc-spec', NULL
);
-- save as $NC_SPEC_ID
```

```bash
BODY=$(jq -n --arg p "$PROJECT_ID" --arg s "$NC_SPEC_ID" '{
  action:"verify", project_id:$p, spec_id:$s,
  artifact: { ref:"T7-nc", kind:"markdown", content:"anything" }
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
[[ "$(status_of "$RESP")" == "422" ]]
echo "$BODY_JSON" | jq -e '.ok==false and .error=="spec_not_reviewable"' >/dev/null
```

---

## T8 — Unknown project_id rejected, no row written

```bash
SENTINEL="00000000-0000-0000-0000-000000000000"
BODY=$(jq -n --arg p "$SENTINEL" --arg s "$SPEC_ID" '{
  action:"verify", project_id:$p, spec_id:$s,
  artifact: { ref:"T8", kind:"markdown", content:"x" }
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
[[ "$(status_of "$RESP")" == "404" ]]
echo "$BODY_JSON" | jq -e '.ok==false and .error=="missing_project"' >/dev/null
WROTE=$($PSQL -c "SELECT count(*) FROM agent_verifications WHERE project_id = '$SENTINEL';")
[[ "$WROTE" == "0" ]]
```

---

## T9 — `codex_callback` updates row and is idempotent-terminal

Reuse T3's verification id.

```bash
BODY=$(jq -n --arg v "$T3_VID" '{
  action:"codex_callback",
  verification_id:$v,
  codex_status:"complete",
  codex_run_id:"vtest-codex-T9",
  codex_findings:[]
}')
# codex_callback MUST carry X-Apex-Codex-Run-Token (codex AGEN-VRF-003); use the
# dedicated helper that wires APEX_CODEX_RUN_TOKEN from the operator env.
R1=$(post_codex_callback "$BODY")
[[ "$(status_of "$R1")" == "200" ]]
body_of "$R1" | jq -e '.ok==true and .codex_status=="complete"' >/dev/null

# Second callback for same row → 409 codex_pipeline_terminal
R2=$(post_codex_callback "$BODY")
[[ "$(status_of "$R2")" == "409" ]]
body_of "$R2" | jq -e '.ok==false and .error=="codex_pipeline_terminal"' >/dev/null
```

DB:

```sql
SELECT 1 FROM agent_verifications
WHERE id = '${T3_VID}'
  AND codex_status = 'complete'
  AND codex_run_id = 'vtest-codex-T9';
-- expect: 1 row
```

---

## T10 — `get_latest` returns the highest-version row regardless of codex_status

Per AGEN-VRF-SHIP-002 (ship-gate finding) `get_latest_verification` returns the highest-version row irrespective of codex terminal state, so the test asserts on the actual most-recent row created during this run rather than the T3 row. The test captures the most-recent verification id created by this script and asserts equality.

```bash
LATEST_VID=$($PSQL -c "SELECT id FROM agent_verifications WHERE project_id = '$PROJECT_ID' AND spec_id = '$SPEC_ID' ORDER BY version DESC, created_at DESC LIMIT 1;")
BODY=$(jq -n --arg p "$PROJECT_ID" --arg s "$SPEC_ID" '{
  action:"get_latest", project_id:$p, spec_id:$s
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
[[ "$(status_of "$RESP")" == "200" ]]
echo "$BODY_JSON" | jq -e ".ok==true and .verification_id==\"$LATEST_VID\"" >/dev/null
```

---

## T11 — Oversized artifact rejected

```bash
BIG=$(head -c 300000 /dev/urandom | base64 | head -c 300000)  # > 256 KB cap
BEFORE=$($PSQL -c "SELECT count(*) FROM agent_verifications WHERE project_id = '$PROJECT_ID';")
BODY=$(jq -n --arg p "$PROJECT_ID" --arg s "$SPEC_ID" --arg a "$BIG" '{
  action:"verify", project_id:$p, spec_id:$s,
  artifact: { ref:"T11-big", kind:"other", content:$a }
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
HTTP=$(status_of "$RESP")
[[ "$HTTP" == "413" || "$HTTP" == "400" ]]
echo "$BODY_JSON" | jq -e '.ok==false and (.error=="input_too_large" or .error=="validation_failed")' >/dev/null
AFTER=$($PSQL -c "SELECT count(*) FROM agent_verifications WHERE project_id = '$PROJECT_ID';")
[[ "$BEFORE" == "$AFTER" ]]
```

---

## Cleanup (per-run, never touches other runs)

Memory cleanup uses `project_id` (codex AGEN-VRF-SHIP-002 pass-8 fix) because the workflow's memory content does NOT include `TEST_CODE` — the older content-substring delete would leave residue and could block project cleanup via FK.

```sql
DELETE FROM agent_memories
WHERE agent_source = 'verification_agent'
  AND project_id IN (SELECT id FROM agent_projects WHERE code = '${TEST_CODE}');

DELETE FROM agent_verifications
WHERE project_id IN (SELECT id FROM agent_projects WHERE code = '${TEST_CODE}');

DELETE FROM agent_specifications
WHERE project_id IN (SELECT id FROM agent_projects WHERE code = '${TEST_CODE}');

DELETE FROM agent_projects WHERE code = '${TEST_CODE}';
```

To handle abnormal exits (memory delete is project-scoped too):

```bash
trap "$PSQL -c \"DELETE FROM agent_memories WHERE agent_source = 'verification_agent' AND project_id IN (SELECT id FROM agent_projects WHERE code = '$TEST_CODE'); DELETE FROM agent_verifications WHERE project_id IN (SELECT id FROM agent_projects WHERE code = '$TEST_CODE'); DELETE FROM agent_specifications WHERE project_id IN (SELECT id FROM agent_projects WHERE code = '$TEST_CODE'); DELETE FROM agent_projects WHERE code = '$TEST_CODE';\"" EXIT
```

## Exit criteria

- T0–T11 all pass against the live n8n instance with auth + migration in place.
- Cleanup leaves no residue under the `$TEST_CODE` project.
- Test results captured in Notion Document Control entry for ref `AGEN-MB-DOC-00005`.

## Required (in-session) smoke

T1, T2, T3, T6, T9 must run successfully during the build session before the agent_tasks row is marked complete. The remaining tests (T4, T5, T7, T8, T10, T11) are deferred to the codex review worker's CI run (F-V1).

## Known limitation

T3–T5 outcomes are LLM-judgement-dependent (Anthropic call). Re-running may produce subtly different finding counts; the assertions deliberately test structural invariants (status enum, finding-array shape) rather than text matches. The codex async review (F-V1) is the canonical ground-truth; deterministic-pass-with-no-findings is provisional until codex confirms.
