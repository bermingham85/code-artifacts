# Specification Agent — Test Plan

**Document ID:** AGEN-TEST-spec-test-plan-v1
**Date:** 2026-05-05 (round 2 — adversarial review pass 1 closed)

---

## 0. Conventions

- Each test has a deterministic, binary `pass_check` — a SQL query, a JSON-path assertion, or an exit code. No "looks reasonable" judgements.
- All tests run against Supabase project `ylcepmvbjjnwmzvevxid` and the n8n local instance on `192.168.50.246:5678`.
- Migration `AGEN-SCRPT-spec-supabase-migration-v1.sql` MUST have been applied.
- A **unique-per-run test project** is created so concurrent runs do not collide and cleanup never touches anything outside the run. The project code is `AGEN-TEST-{run_id}` where `run_id` is an opaque short token (UUIDv7 prefix or epoch+random).
- LLM behaviour is non-deterministic. The workflow's deterministic post-validation (banned-word regex, schema invariants, status downgrade rules) makes the test pass criteria robust to model variance, but tests assert on **structural** outcomes, not on specific generated text.
- All curl invocations use `--show-error --silent --max-time 90` and capture both response body and HTTP status. (We deliberately do NOT use `--fail` or `--fail-with-body` because several tests assert 4xx — `--fail` would make curl exit non-zero and abort `set -e` harnesses before the assertion runs.)
- All curl invocations include the auth header `-H "X-APEX-Webhook-Token: $APEX_TOKEN"`. `$APEX_TOKEN` is loaded from the operator's environment; no token literal appears in the test plan.

## Setup helpers (used by all tests)

```bash
RUN_ID=$(date +%s)-$RANDOM
TEST_CODE="AGEN-TEST-$RUN_ID"
APEX_TOKEN=${APEX_TOKEN:?env var required}
WEBHOOK="http://192.168.50.246:5678/webhook/specification-agent"
PSQL="psql -h db.ylcepmvbjjnwmzvevxid.supabase.co -U postgres -d postgres -t -A"

post() {
  local body="$1"; local idem="${2:-}"
  local hdr=(-H "Content-Type: application/json" -H "X-APEX-Webhook-Token: $APEX_TOKEN")
  [[ -n "$idem" ]] && hdr+=(-H "Idempotency-Key: $idem")
  # NOTE: do NOT use --fail because we expect 4xx in negative tests; capture status separately.
  curl --show-error --silent --max-time 90 -w '\nHTTP_STATUS:%{http_code}\n' "${hdr[@]}" -d "$body" "$WEBHOOK"
}

# Helpers to split the curl output into JSON body and HTTP status.
body_of()   { echo "$1" | sed '/^HTTP_STATUS:/d'; }
status_of() { echo "$1" | awk -F: '/^HTTP_STATUS:/{print $2}' | tr -d '\r\n '; }
```

## T0 — Setup

Create a fresh run-scoped project. The code is unique per run.

```sql
INSERT INTO agent_projects (code, name, status)
VALUES ('${TEST_CODE}', 'Specification Agent Test Project', 'planning')
RETURNING id;
```

Save the returned UUID as `$PROJECT_ID`. `pass_check`:

```sql
SELECT count(*) = 1 FROM agent_projects WHERE code = '${TEST_CODE}';
```

---

## T1 — Auth: missing token rejected

`pass_check`:
```bash
HTTP=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 -X POST "$WEBHOOK" \
  -H 'Content-Type: application/json' -d '{"action":"clarify_or_spec","project_id":"00000000-0000-0000-0000-000000000000","request":"x"}')
[[ "$HTTP" == "401" ]]
```

---

## T2 — Validation: empty JSON body rejected

```bash
RESP=$(post '{}')
[[ "$(status_of "$RESP")" == "400" ]]
body_of "$RESP" | jq -e '.ok == false and .error == "validation_failed"' >/dev/null
```

Pass = both checks return 0. (Title says "empty JSON body" — tests an empty JSON object specifically; an empty HTTP body is a separate test that n8n's webhook node handles before our validate runs.)

---

## T3 — Clear brief produces a clean reviewed spec

**Scenario.** Caller submits a fully-formed brief with measurable acceptance criteria.

```bash
BODY=$(jq -n --arg p "$PROJECT_ID" '{
  action: "clarify_or_spec",
  project_id: $p,
  request: "Build a webhook that accepts a POST with {amount: number, currency: string} and stores a row in expense_log with the amount, currency, and current timestamp. Currency must be ISO 4217. amount must be > 0. Return 400 on invalid input, 201 on success."
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
T3_SPEC_ID=$(echo "$BODY_JSON" | jq -r '.spec_id')
[[ "$(status_of "$RESP")" == "200" ]]
echo "$BODY_JSON" | jq -e '.ok==true and .status=="reviewed" and .version==1 and (.spec.requirements|length>0) and (.spec.acceptance_criteria|length>0) and (.spec.non_goals|length>0) and (.spec.open_questions|length==0)' >/dev/null
[[ -n "$T3_SPEC_ID" && "$T3_SPEC_ID" != "null" ]]
```

Plus DB state for the exact returned id (no "latest row" lookups):

```sql
SELECT 1 FROM agent_specifications
WHERE id = '${T3_SPEC_ID}'
  AND status = 'reviewed' AND version = 1
  AND jsonb_array_length(requirements) > 0
  AND jsonb_array_length(acceptance_criteria) > 0
  AND jsonb_array_length(open_questions) = 0
  AND jsonb_array_length(non_goals) > 0;
```
Pass = exactly 1 row.

---

## T4 — Ambiguous brief returns clarification, not a reviewed spec

```bash
BODY=$(jq -n --arg p "$PROJECT_ID" '{
  action:"clarify_or_spec", project_id:$p,
  request:"We want a fast and intuitive dashboard for the team. Make it nice."
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
T4_SPEC_ID=$(echo "$BODY_JSON" | jq -r '.spec_id')
[[ "$(status_of "$RESP")" == "200" ]]
[[ -n "$T4_SPEC_ID" && "$T4_SPEC_ID" != "null" ]]
echo "$BODY_JSON" | jq -e '.ok==true and .status=="needs_clarification" and (.questions|length>=1) and (.questions|length<=6) and (.spec.acceptance_criteria|length==0)' >/dev/null
```

DB:

```sql
SELECT status, jsonb_array_length(open_questions) AS oq, jsonb_array_length(acceptance_criteria) AS ac
FROM agent_specifications WHERE id = '${T4_SPEC_ID}';
-- expect: status='needs_clarification', oq BETWEEN 1 AND 6, ac=0
-- (6 covers the optional "[meta] N more deferred" marker entry per the prompt rules.)
```

The deterministic post-validator MUST downgrade to `needs_clarification` even if the LLM somehow returns `reviewed` — because the brief contains banned vague words (`fast`, `intuitive`, `nice`) that hit the regex.

---

## T5 — Refining a spec produces a v2 child and supersedes the parent

```bash
BODY=$(jq -n --arg p "$PROJECT_ID" --arg parent "$T3_SPEC_ID" '{
  action:"clarify_or_spec", project_id:$p, parent_spec_id:$parent,
  request:"Same as before, plus: also store the request source IP in expense_log.source_ip. Add an acceptance criterion that source_ip is captured (binary_check: \"SELECT (count(*) = 0) AS pass FROM expense_log WHERE source_ip IS NULL\")."
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
T5_SPEC_ID=$(echo "$BODY_JSON" | jq -r '.spec_id')
[[ "$(status_of "$RESP")" == "200" ]]
[[ -n "$T5_SPEC_ID" && "$T5_SPEC_ID" != "null" && "$T5_SPEC_ID" != "$T3_SPEC_ID" ]]
echo "$BODY_JSON" | jq -e ".ok==true and .status==\"reviewed\" and .version==2" >/dev/null
```

DB lineage assertions, scoped to the specific child id:

```sql
SELECT
  (SELECT version           FROM agent_specifications WHERE id = '${T5_SPEC_ID}') = 2,
  (SELECT status            FROM agent_specifications WHERE id = '${T5_SPEC_ID}') = 'reviewed',
  (SELECT parent_spec_id    FROM agent_specifications WHERE id = '${T5_SPEC_ID}') = '${T3_SPEC_ID}'::uuid,
  (SELECT root_spec_id      FROM agent_specifications WHERE id = '${T5_SPEC_ID}') = '${T3_SPEC_ID}'::uuid,
  (SELECT project_id        FROM agent_specifications WHERE id = '${T5_SPEC_ID}') = '${PROJECT_ID}'::uuid,
  (SELECT status            FROM agent_specifications WHERE id = '${T3_SPEC_ID}') = 'superseded',
  EXISTS(SELECT 1 FROM agent_specifications WHERE id = '${T5_SPEC_ID}'
    AND body_markdown ILIKE '%source_ip%');
-- expect: all 7 columns true
```

---

## T6 — Cross-project parent rejected (lineage validation)

A second test project + an attempt to claim a parent from project A while inserting into project B.

```sql
INSERT INTO agent_projects (code, name, status) VALUES ('${TEST_CODE}-X', 'Cross-Project Test', 'planning') RETURNING id;
-- save as $OTHER_PROJECT_ID
```

```bash
BODY=$(jq -n --arg p "$OTHER_PROJECT_ID" --arg parent "$T3_SPEC_ID" '{
  action:"clarify_or_spec", project_id:$p, parent_spec_id:$parent,
  request:"trying to attach a parent from a different project — should be rejected"
}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
[[ "$(status_of "$RESP")" == "409" ]]
echo "$BODY_JSON" | jq -e '.ok==false and .error=="parent_project_mismatch"' >/dev/null
```

DB: count of specifications under `$OTHER_PROJECT_ID` MUST be 0.

```sql
SELECT count(*) = 0 FROM agent_specifications WHERE project_id = '${OTHER_PROJECT_ID}';
```

---

## T7 — Unknown project_id rejected, no row written

The all-zero UUID is used as a sentinel "definitely not present" project. We first prove it does not exist, then assert no rows are written under it (avoiding flaky global-count comparisons).

```bash
SENTINEL_PROJECT="00000000-0000-0000-0000-000000000000"
EXISTS=$($PSQL -c "SELECT count(*) FROM agent_projects WHERE id = '$SENTINEL_PROJECT';")
[[ "$EXISTS" == "0" ]]   # precondition

BODY=$(jq -n --arg p "$SENTINEL_PROJECT" '{action:"clarify_or_spec", project_id:$p, request:"anything"}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
[[ "$(status_of "$RESP")" == "404" ]]
echo "$BODY_JSON" | jq -e '.ok==false and .error=="missing_project"' >/dev/null

# No rows written under the sentinel project (precise, not global count).
WROTE=$($PSQL -c "SELECT count(*) FROM agent_specifications WHERE project_id = '$SENTINEL_PROJECT';")
[[ "$WROTE" == "0" ]]
```

---

## T8 — Idempotency-Key replays the same spec_id

```bash
KEY="proj-${PROJECT_ID}-t8-${RUN_ID}"
BODY=$(jq -n --arg p "$PROJECT_ID" '{action:"clarify_or_spec", project_id:$p, request:"Build a webhook accepting POST {x:int} where x>0; reject 400 on x<=0; respond 201 on success; p95 latency < 200ms over 1k req."}')
R1=$(post "$BODY" "$KEY"); R2=$(post "$BODY" "$KEY")
[[ "$(status_of "$R1")" == "200" ]]
[[ "$(status_of "$R2")" == "200" ]]
ID1=$(body_of "$R1" | jq -r '.spec_id')
ID2=$(body_of "$R2" | jq -r '.spec_id')
REPLAYED2=$(body_of "$R2" | jq -r '.replayed')
[[ -n "$ID1" && "$ID1" != "null" ]]
[[ "$ID1" == "$ID2" && "$REPLAYED2" == "true" ]]
```

DB:

```sql
SELECT count(*) = 1 FROM agent_specifications WHERE idempotency_key = '${KEY}';
```

---

## T9 — `get_latest` resolution within the T3/T5 lineage

T8 created an unrelated reviewed spec under the same project, so `get_latest` scoped only by `project_id` is ambiguous in a multi-root project. We scope T9 to the T3/T5 lineage explicitly via `root_spec_id`.

```bash
BODY=$(jq -n --arg p "$PROJECT_ID" --arg r "$T3_SPEC_ID" \
  '{action:"get_latest", project_id:$p, root_spec_id:$r}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
[[ "$(status_of "$RESP")" == "200" ]]
echo "$BODY_JSON" | jq -e ".ok==true and .spec_id==\"$T5_SPEC_ID\" and .version==2" >/dev/null
```

---

## T10 — Memory rows written with correct content + metadata

```sql
SELECT 1 FROM agent_memories
WHERE agent_name='specification_agent'
  AND memory_type='decision'
  AND metadata->>'spec_id' = '${T3_SPEC_ID}';
-- expect: 1 row

SELECT 1 FROM agent_memories
WHERE agent_name='specification_agent'
  AND memory_type='question_set'
  AND metadata->>'spec_id' = '${T4_SPEC_ID}';
-- expect: 1 row
```

---

## T11 — Oversized payload rejected

```bash
BIG=$(head -c 50000 /dev/urandom | base64 | head -c 50000)  # > 32 KB cap
BEFORE=$($PSQL -c "SELECT count(*) FROM agent_specifications WHERE project_id = '$PROJECT_ID';")
BODY=$(jq -n --arg p "$PROJECT_ID" --arg req "$BIG" '{action:"clarify_or_spec", project_id:$p, request:$req}')
RESP=$(post "$BODY"); BODY_JSON=$(body_of "$RESP")
HTTP=$(status_of "$RESP")
[[ "$HTTP" == "413" || "$HTTP" == "400" ]]
echo "$BODY_JSON" | jq -e '.ok==false and (.error=="input_too_large" or .error=="validation_failed")' >/dev/null
AFTER=$($PSQL -c "SELECT count(*) FROM agent_specifications WHERE project_id = '$PROJECT_ID';")
[[ "$BEFORE" == "$AFTER" ]]
```

---

## Cleanup (per-run, never touches other runs)

Order matters: delete memories FIRST (by `metadata.spec_id`), then specifications, then projects. If specs go first the memories table has no way to map back to the project.

```sql
-- 1. Memories first, joined via metadata.spec_id while specs still exist.
DELETE FROM agent_memories
WHERE agent_name = 'specification_agent'
  AND metadata->>'spec_id' IN (
    SELECT id::text FROM agent_specifications
    WHERE project_id IN (
      SELECT id FROM agent_projects WHERE code LIKE '${TEST_CODE}%'
    )
  );

-- 2. Specifications.
DELETE FROM agent_specifications
WHERE project_id IN (SELECT id FROM agent_projects WHERE code LIKE '${TEST_CODE}%');

-- 3. Projects.
DELETE FROM agent_projects WHERE code LIKE '${TEST_CODE}%';
```

The `${TEST_CODE}%` LIKE matches both `${TEST_CODE}` and `${TEST_CODE}-X`. This is safe because the run id is unique per run.

A future revision should add `metadata.run_id` to the workflow's memory writes so cleanup can use a single key for memory-row identification, decoupling cleanup from spec lifetime.

To handle abnormal exits, run the cleanup inside a trap:

```bash
cleanup() { $PSQL -f - <<SQL
DELETE FROM agent_memories WHERE ...;  -- as above
DELETE FROM agent_specifications WHERE ...;
DELETE FROM agent_projects WHERE code LIKE '${TEST_CODE}%';
SQL
}
trap cleanup EXIT
```

## Exit criteria

- T0–T11 all pass against the live n8n instance with auth + migration in place.
- Cleanup leaves no residue under any `${TEST_CODE}*` project.
- Test results captured in Notion Document Control entry for ref `AGEN-MB-DOC-00002`.

## Known limitation

These tests cannot be executed during this build session unless the operator runs them post-import-and-activation. The Verification Agent (build step 7) is the canonical owner of executing this plan automatically as part of its CI duties.
