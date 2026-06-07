-- AGEN-SCRPT-verification-supabase-migration-v1.sql
-- Verification Agent — Supabase schema
-- Date: 2026-05-22
-- Run on: Supabase project ylcepmvbjjnwmzvevxid
--
-- Pre-conditions verified by audit (2026-05-22T23:09Z):
--   - agent_projects exists, FK target
--   - agent_tasks exists, FK target (task_id is optional on a verification row)
--   - agent_specifications exists, FK target (spec_id is REQUIRED)
--   - agent_build_artifacts DOES NOT EXIST yet — build_artifact_id is plain uuid, no FK
--     (Builder Agent build will introduce that table and a follow-on migration may add
--     the FK constraint; see Accepted-Risk register AR-V3 in integration spec.)
--   - agent_verifications DOES NOT EXIST (this migration creates it)
--   - Migration-coordinator task 73555d72 is still 'pending' — per current consolidation
--     plan each per-agent migration is bundled into its own build task; this file is that
--     bundle for Verification Agent.
--
-- Idempotency: safe to re-run. Pre-flight column guard fails fast if a shape-divergent
-- table is already present. No CREATE TABLE without IF NOT EXISTS, all policies dropped
-- before recreate, functions CREATE OR REPLACE.
--
-- IMPORTANT: This migration uses the canonical RLS pattern (service_role-only). The n8n
-- workflow connects via the postgres credential 'Supabase Novel Writer' (id
-- tk7Z3R3l1dUwRnmu) which is configured for service_role.

-----------------------------------------------
-- 0. Pre-flight column guard
-----------------------------------------------
DO $$
DECLARE
    v_table_exists boolean;
    v_expected text[] := ARRAY[
        'id','project_id','task_id','spec_id','build_artifact_id',
        'status','findings','summary','reviewer','reasoning_effort',
        'codex_run_id','codex_status','version','parent_verification_id',
        'root_verification_id','idempotency_key','requested_by','notes',
        'created_at','updated_at'
    ];
    v_missing text[];
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema='public' AND table_name='agent_verifications'
    ) INTO v_table_exists;

    IF v_table_exists THEN
        SELECT array_agg(c) INTO v_missing
        FROM unnest(v_expected) c
        WHERE NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='agent_verifications'
              AND column_name = c
        );
        IF v_missing IS NOT NULL AND array_length(v_missing, 1) > 0 THEN
            RAISE EXCEPTION
                'agent_verifications exists but is missing expected columns: %. Manual reconciliation required (likely the migration-coordinator landed a partial schema).',
                v_missing;
        END IF;
    END IF;
END $$;

-----------------------------------------------
-- 1. agent_verifications
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES agent_projects(id) ON DELETE RESTRICT,
    task_id UUID REFERENCES agent_tasks(id) ON DELETE SET NULL,
    spec_id UUID NOT NULL REFERENCES agent_specifications(id) ON DELETE RESTRICT,
    build_artifact_id UUID,  -- no FK yet; agent_build_artifacts is provisioned by Builder Agent task
    status TEXT NOT NULL DEFAULT 'pass'
        CHECK (status IN ('pass','fail','partial','skipped','error')),
    findings JSONB NOT NULL DEFAULT '[]'::jsonb,
    summary TEXT,
    reviewer TEXT NOT NULL DEFAULT 'workflow_deterministic'
        CHECK (reviewer IN ('workflow_deterministic','codex-bridge','claude','human')),
    reasoning_effort TEXT
        CHECK (reasoning_effort IS NULL OR reasoning_effort IN ('low','medium','high')),
    codex_run_id TEXT,
    codex_status TEXT NOT NULL DEFAULT 'not_started'
        CHECK (codex_status IN ('not_started','queued','running','complete','skipped','failed')),
    version INT NOT NULL DEFAULT 1,
    parent_verification_id UUID REFERENCES agent_verifications(id) ON DELETE SET NULL,
    root_verification_id UUID REFERENCES agent_verifications(id) ON DELETE SET NULL,
    idempotency_key TEXT,
    requested_by TEXT,  -- caller identity (agent name, operator email, etc.)
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT verif_version_positive CHECK (version >= 1),
    CONSTRAINT verif_no_self_parent CHECK (id <> parent_verification_id),
    CONSTRAINT verif_findings_is_array CHECK (jsonb_typeof(findings) = 'array'),
    CONSTRAINT verif_summary_not_too_large CHECK (summary IS NULL OR length(summary) <= 10000)
);

-- Unique idempotency
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_verifications_idempotency
    ON agent_verifications (idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_agent_verifications_project ON agent_verifications(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_verifications_task ON agent_verifications(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_verifications_spec ON agent_verifications(spec_id);
CREATE INDEX IF NOT EXISTS idx_agent_verifications_status ON agent_verifications(status);
CREATE INDEX IF NOT EXISTS idx_agent_verifications_codex_status ON agent_verifications(codex_status)
    WHERE codex_status IN ('queued','running');
CREATE INDEX IF NOT EXISTS idx_agent_verifications_root ON agent_verifications(root_verification_id);

-----------------------------------------------
-- 2. updated_at trigger
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_agent_verifications_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
    IF (NEW.* IS DISTINCT FROM OLD.*) THEN
        NEW.updated_at = now();
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_agent_verifications_updated ON agent_verifications;
CREATE TRIGGER trg_agent_verifications_updated
    BEFORE UPDATE ON agent_verifications
    FOR EACH ROW EXECUTE FUNCTION update_agent_verifications_updated_at();

-----------------------------------------------
-- 3. RLS — service_role only
-----------------------------------------------
ALTER TABLE agent_verifications ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE r record;
BEGIN
    FOR r IN
        SELECT polname FROM pg_policy WHERE polrelid = 'public.agent_verifications'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.agent_verifications', r.polname);
    END LOOP;
END $$;

CREATE POLICY "service_role_full" ON agent_verifications
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-----------------------------------------------
-- 4. RPC: create_verification_record
-- Inserts a new verification row.
-- Lineage-safe: validates project_id<->spec_id and (when task_id supplied) project<->task.
-- Idempotency-safe: replays the row when idempotency_key matches.
-- Concurrency-safe: parent row locked FOR UPDATE before version compute.
-----------------------------------------------
CREATE OR REPLACE FUNCTION create_verification_record(
    p_project_id UUID,
    p_task_id UUID,
    p_spec_id UUID,
    p_build_artifact_id UUID,
    p_status TEXT,
    p_findings JSONB,
    p_summary TEXT,
    p_reviewer TEXT,
    p_reasoning_effort TEXT,
    p_codex_run_id TEXT,
    p_codex_status TEXT,
    p_parent_verification_id UUID,
    p_idempotency_key TEXT,
    p_requested_by TEXT,
    p_notes TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_new_id UUID;
    v_version INT := 1;
    v_root_verification_id UUID;
    v_existing_row JSONB;
    v_spec_project_id UUID;
    v_spec_task_id UUID;
    v_task_project_id UUID;
    v_parent_project_id UUID;
    v_parent_spec_id UUID;
    v_allowed_status TEXT[] := ARRAY['pass','fail','partial','skipped','error'];
    v_allowed_reviewer TEXT[] := ARRAY['workflow_deterministic','codex-bridge','claude','human'];
    v_allowed_codex_status TEXT[] := ARRAY['not_started','queued','running','complete','skipped','failed'];
BEGIN
    -- Argument validation.
    IF NOT (COALESCE(p_status,'pass') = ANY (v_allowed_status)) THEN
        RETURN jsonb_build_object('error', 'invalid_status', 'detail', p_status);
    END IF;
    IF NOT (COALESCE(p_reviewer,'workflow_deterministic') = ANY (v_allowed_reviewer)) THEN
        RETURN jsonb_build_object('error', 'invalid_reviewer', 'detail', p_reviewer);
    END IF;
    IF NOT (COALESCE(p_codex_status,'not_started') = ANY (v_allowed_codex_status)) THEN
        RETURN jsonb_build_object('error', 'invalid_codex_status', 'detail', p_codex_status);
    END IF;
    IF p_reasoning_effort IS NOT NULL AND p_reasoning_effort NOT IN ('low','medium','high') THEN
        RETURN jsonb_build_object('error', 'invalid_reasoning_effort', 'detail', p_reasoning_effort);
    END IF;
    IF p_findings IS NOT NULL AND jsonb_typeof(p_findings) <> 'array' THEN
        RETURN jsonb_build_object('error', 'findings_not_array');
    END IF;

    -- Idempotency replay fast-path.
    IF p_idempotency_key IS NOT NULL THEN
        SELECT row_to_json(v)::jsonb INTO v_existing_row
        FROM agent_verifications v
        WHERE v.idempotency_key = p_idempotency_key
        LIMIT 1;
        IF v_existing_row IS NOT NULL THEN
            RETURN jsonb_build_object('replayed', true, 'verification', v_existing_row);
        END IF;
    END IF;

    -- spec_id must exist and belong to p_project_id.
    SELECT project_id, task_id INTO v_spec_project_id, v_spec_task_id
    FROM agent_specifications WHERE id = p_spec_id;
    IF v_spec_project_id IS NULL THEN
        RETURN jsonb_build_object('error', 'spec_not_found');
    END IF;
    IF v_spec_project_id <> p_project_id THEN
        RETURN jsonb_build_object('error', 'spec_project_mismatch');
    END IF;

    -- task_id (if supplied) must exist and belong to the same project, and (if the spec
    -- is task-scoped) it must match the spec's task_id.
    IF p_task_id IS NOT NULL THEN
        SELECT project_id INTO v_task_project_id FROM agent_tasks WHERE id = p_task_id;
        IF v_task_project_id IS NULL THEN
            RETURN jsonb_build_object('error', 'task_not_found');
        END IF;
        IF v_task_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'task_project_mismatch');
        END IF;
        IF v_spec_task_id IS NOT NULL AND v_spec_task_id <> p_task_id THEN
            RETURN jsonb_build_object('error', 'spec_task_mismatch');
        END IF;
    END IF;

    -- Parent lineage validation.
    IF p_parent_verification_id IS NOT NULL THEN
        SELECT version, root_verification_id, project_id, spec_id
          INTO v_version, v_root_verification_id, v_parent_project_id, v_parent_spec_id
        FROM agent_verifications
        WHERE id = p_parent_verification_id
        FOR UPDATE;
        IF v_version IS NULL THEN
            RETURN jsonb_build_object('error', 'parent_not_found');
        END IF;
        IF v_parent_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'parent_project_mismatch');
        END IF;
        IF v_parent_spec_id <> p_spec_id THEN
            RETURN jsonb_build_object('error', 'parent_spec_mismatch');
        END IF;

        IF v_root_verification_id IS NULL THEN
            v_root_verification_id := p_parent_verification_id;
            UPDATE agent_verifications SET root_verification_id = p_parent_verification_id
            WHERE id = p_parent_verification_id;
        END IF;

        SELECT COALESCE(MAX(version), 0) + 1 INTO v_version
        FROM agent_verifications
        WHERE root_verification_id = v_root_verification_id OR id = v_root_verification_id;
    END IF;

    BEGIN
        INSERT INTO agent_verifications (
            project_id, task_id, spec_id, build_artifact_id,
            status, findings, summary, reviewer, reasoning_effort,
            codex_run_id, codex_status, version, parent_verification_id,
            root_verification_id, idempotency_key, requested_by, notes
        ) VALUES (
            p_project_id, p_task_id, p_spec_id, p_build_artifact_id,
            COALESCE(p_status,'pass'),
            COALESCE(p_findings, '[]'::jsonb),
            p_summary,
            COALESCE(p_reviewer,'workflow_deterministic'),
            p_reasoning_effort,
            p_codex_run_id,
            COALESCE(p_codex_status,'not_started'),
            v_version,
            p_parent_verification_id,
            v_root_verification_id,
            p_idempotency_key,
            p_requested_by,
            p_notes
        )
        RETURNING id INTO v_new_id;
    EXCEPTION WHEN unique_violation THEN
        IF SQLERRM ILIKE '%uq_agent_verifications_idempotency%'
           AND p_idempotency_key IS NOT NULL THEN
            SELECT row_to_json(v)::jsonb INTO v_existing_row
            FROM agent_verifications v
            WHERE v.idempotency_key = p_idempotency_key
            LIMIT 1;
            IF v_existing_row IS NOT NULL THEN
                RETURN jsonb_build_object('replayed', true, 'verification', v_existing_row);
            END IF;
        END IF;
        RETURN jsonb_build_object('error', 'unique_violation', 'detail', SQLERRM);
    END;

    -- Self-root a fresh lineage.
    IF v_root_verification_id IS NULL THEN
        UPDATE agent_verifications SET root_verification_id = id WHERE id = v_new_id;
    END IF;

    RETURN jsonb_build_object('replayed', false,
        'verification', (SELECT row_to_json(v)::jsonb FROM agent_verifications v WHERE v.id = v_new_id));
END;
$$;

-----------------------------------------------
-- 5. RPC: update_verification_codex_outcome
-- The async codex worker (out-of-process) writes back its findings via this RPC.
-- Status transitions enforced:
--   not_started/queued/running → complete | failed | skipped
-- 'complete' allows updating findings and (optionally) escalating overall status.
-- Failed/complete rows are terminal in the codex pipeline; further updates rejected.
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_verification_codex_outcome(
    p_verification_id UUID,
    p_codex_status TEXT,
    p_codex_run_id TEXT,
    p_codex_findings JSONB,
    p_status_override TEXT,
    p_summary_append TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_current_codex TEXT;
    v_current_findings JSONB;
    v_current_status TEXT;
    v_current_summary TEXT;
    v_allowed_codex_status TEXT[] := ARRAY['queued','running','complete','failed','skipped'];
    -- codex AGEN-VRF-SHIP-001 (pass 8) hardening: callbacks may only downgrade. pass is the
    -- consensus-gated terminal that the deterministic Claude pass produces; skipped/error
    -- are workflow-set states, not caller-set. Reject anything else.
    v_allowed_override TEXT[] := ARRAY['fail','partial'];
BEGIN
    IF NOT (p_codex_status = ANY (v_allowed_codex_status)) THEN
        RETURN jsonb_build_object('error', 'invalid_codex_status', 'detail', p_codex_status);
    END IF;
    IF p_status_override IS NOT NULL AND NOT (p_status_override = ANY (v_allowed_override)) THEN
        RETURN jsonb_build_object('error', 'invalid_status_override', 'detail', p_status_override);
    END IF;
    IF p_codex_findings IS NOT NULL AND jsonb_typeof(p_codex_findings) <> 'array' THEN
        RETURN jsonb_build_object('error', 'findings_not_array');
    END IF;

    SELECT codex_status, findings, status, summary
      INTO v_current_codex, v_current_findings, v_current_status, v_current_summary
    FROM agent_verifications WHERE id = p_verification_id
    FOR UPDATE;
    IF v_current_codex IS NULL THEN
        RETURN jsonb_build_object('error', 'verification_not_found');
    END IF;
    IF v_current_codex IN ('complete','failed','skipped') THEN
        RETURN jsonb_build_object('error', 'codex_pipeline_terminal', 'current', v_current_codex);
    END IF;

    -- codex AGEN-VRF-SHIP-001 hardening: derive an effective status server-side. If the
    -- caller-supplied codex findings contain any critical/high/medium severity, the row's
    -- status MUST move off 'pass'. Without this, codex_callback could append a damning
    -- finding while leaving status='pass', allowing PM Agent to advance on a row that
    -- the codex review actually rejected.
    DECLARE
        v_codex_blocking BOOLEAN := FALSE;
        v_codex_critical_high BOOLEAN := FALSE;
        v_effective_status TEXT;
    BEGIN
        IF p_codex_findings IS NOT NULL AND jsonb_array_length(p_codex_findings) > 0 THEN
            SELECT
                bool_or(f.severity IN ('critical','high','medium')),
                bool_or(f.severity IN ('critical','high'))
            INTO v_codex_blocking, v_codex_critical_high
            FROM jsonb_to_recordset(p_codex_findings) AS f(severity text);
        END IF;
        v_effective_status := COALESCE(p_status_override, v_current_status);
        IF v_codex_critical_high THEN
            v_effective_status := 'fail';
        ELSIF v_codex_blocking AND v_effective_status = 'pass' THEN
            v_effective_status := 'partial';
        END IF;
        -- codex AGEN-VRF-SHIP-001 (pass 7) hardening: codex_status='skipped' CANNOT leave a
        -- deterministic pass terminal. Skipped means codex did not actually adversarially
        -- review, so the row is provisional — downgrade pass → partial so PM Agent's gate
        -- does not auto-advance. Operator-attested skip (with rationale in summary_append)
        -- is still recorded; the operator can advance manually if policy permits.
        IF p_codex_status = 'skipped' AND v_effective_status = 'pass' THEN
            v_effective_status := 'partial';
        END IF;

    UPDATE agent_verifications
    SET codex_status = p_codex_status,
        codex_run_id = COALESCE(p_codex_run_id, codex_run_id),
        findings = CASE
            WHEN p_codex_findings IS NOT NULL THEN v_current_findings || p_codex_findings
            ELSE v_current_findings
        END,
        status = v_effective_status,
        summary = CASE
            WHEN p_summary_append IS NOT NULL
                THEN COALESCE(v_current_summary,'') ||
                     CASE WHEN v_current_summary IS NULL OR length(v_current_summary)=0 THEN '' ELSE E'\n' END ||
                     p_summary_append
            ELSE v_current_summary
        END
    WHERE id = p_verification_id;
    END;

    RETURN (SELECT row_to_json(v)::jsonb FROM agent_verifications v WHERE v.id = p_verification_id);
END;
$$;

-----------------------------------------------
-- 6. RPC: get_latest_verification
-- Resolves the highest-version verification for (project_id, spec_id, optional task_id).
-- Prefers terminal-codex rows (complete/skipped/failed). Falls back to the latest row.
-----------------------------------------------
CREATE OR REPLACE FUNCTION get_latest_verification(
    p_project_id UUID,
    p_spec_id UUID,
    p_task_id UUID DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_row agent_verifications%ROWTYPE;
BEGIN
    -- codex AGEN-VRF-SHIP-002 hardening: return the HIGHEST-VERSION row, regardless of
    -- codex_status. Consumers (PM Agent) then check codex_status themselves before acting.
    -- This prevents a newer queued/running row from being shadowed by an older terminal
    -- 'complete' or 'failed' row. The caller's gate is the pair (status='pass',
    -- codex_status IN ('complete','skipped')) — never a stale-by-version fallback.
    SELECT * INTO v_row
    FROM agent_verifications v
    WHERE v.project_id = p_project_id
      AND v.spec_id = p_spec_id
      AND (p_task_id IS NULL OR v.task_id = p_task_id)
    ORDER BY v.version DESC, v.created_at DESC
    LIMIT 1;
    IF v_row.id IS NOT NULL THEN
        RETURN row_to_json(v_row)::jsonb;
    END IF;

    RETURN NULL;
END;
$$;

-----------------------------------------------
-- 7. Grants — least privilege
-----------------------------------------------
REVOKE ALL ON FUNCTION create_verification_record(UUID,UUID,UUID,UUID,TEXT,JSONB,TEXT,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,TEXT,TEXT) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION update_verification_codex_outcome(UUID,TEXT,TEXT,JSONB,TEXT,TEXT) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION get_latest_verification(UUID,UUID,UUID) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION create_verification_record(UUID,UUID,UUID,UUID,TEXT,JSONB,TEXT,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,TEXT,TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION update_verification_codex_outcome(UUID,TEXT,TEXT,JSONB,TEXT,TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION get_latest_verification(UUID,UUID,UUID) TO service_role;

-----------------------------------------------
-- 8. Accepted-risk register (documentation)
-----------------------------------------------
COMMENT ON TABLE agent_verifications IS
    'Verification Agent canonical store. Accepted residual risks (tracked in AGEN-SPEC-verification-integration-v1.md):
     • AR-V1: build_artifact_id has no FK because agent_build_artifacts is not yet provisioned (Builder Agent task). FK will be added in a follow-on migration once that table exists.
     • AR-V2: codex review is invoked async via APEX_CODEX_BRIDGE_URL HTTP wrapper (out-of-process worker on the Windows codex host). When the URL is unset or unreachable the workflow records codex_status=queued for offline pickup; the deterministic pass/fail row is still returned immediately so callers are not blocked. Doctrine A4 "no Claude self-review" still holds — Claude never reviews its own outputs; codex remains the canonical reviewer when it eventually runs.
     • AR-V3: idempotency_key is globally unique, not project-scoped. Callers should prefix keys with project/operation context (e.g. verify-{project_id}-{spec_id}-{nonce}) to avoid cross-context replay.
     • AR-V4: LAN-only HTTP transport for the webhook; token + firewall are the compensating control until HTTPS migration.';

COMMENT ON FUNCTION create_verification_record(UUID,UUID,UUID,UUID,TEXT,JSONB,TEXT,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,TEXT,TEXT) IS
    'Inserts an initial verification row with the workflow''s deterministic outcome. The codex async pipeline updates the row later via update_verification_codex_outcome.';
COMMENT ON FUNCTION update_verification_codex_outcome(UUID,TEXT,TEXT,JSONB,TEXT,TEXT) IS
    'Called by the codex review worker once codex_bridge.py completes. Appends codex findings to the existing array, optionally promotes status, and locks codex_status to a terminal value.';
COMMENT ON FUNCTION get_latest_verification(UUID,UUID,UUID) IS
    'Returns the highest-version verification row for a (project, spec [, task]) tuple regardless of codex_status (ORDER BY version DESC, created_at DESC; LIMIT 1). Consumers (PM Agent) inspect codex_status and status themselves before acting � the terminal advancement gate is (row.status=''pass'' AND row.codex_status IN (''complete'',''skipped'')). This prevents a newer queued/running row from being shadowed by an older terminal row (codex AGEN-VRF-SHIP-002; matches �2.2 of AGEN-SPEC-verification-integration-v1.md).';
