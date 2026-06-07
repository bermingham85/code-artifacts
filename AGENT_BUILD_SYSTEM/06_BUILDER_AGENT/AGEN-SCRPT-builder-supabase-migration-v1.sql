-- AGEN-SCRPT-builder-supabase-migration-v1.sql
-- Builder Agent — Supabase schema
-- Date: 2026-05-23
-- Run on: Supabase project ylcepmvbjjnwmzvevxid
--
-- Pre-conditions verified by audit (2026-05-23T04:31Z):
--   - agent_projects exists, FK target
--   - agent_tasks exists, FK target (task_id REQUIRED — Builder accepts ONE task at a
--     time per HANDOVER, so every artifact ties to a task)
--   - agent_architectures was just created by the architecture migration in this same
--     coordinator session; FK to it is optional (architecture_id may be NULL for
--     ad-hoc builds that bypass the formal pipeline, e.g. infra fixes)
--   - agent_verifications exists; this migration adds the deferred FK constraint
--     agent_verifications.build_artifact_id → agent_build_artifacts(id) that AR-V1
--     in the verification migration left out by necessity
--   - agent_build_artifacts DOES NOT EXIST (this migration creates it)
--   - Migration coordinator task 73555d72 is in_progress
--
-- Idempotency: safe to re-run. Pre-flight column guard fails fast on shape divergence.
-- FK addition uses ALTER TABLE ... IF NOT EXISTS via a constraint-presence DO block.

-----------------------------------------------
-- 0. Pre-flight shape guard — column NAME + TYPE + NULLABILITY (closes codex pass 1 F3)
-----------------------------------------------
DO $$
DECLARE
    v_table_exists boolean;
    v_expected RECORD;
    v_actual_type text;
    v_actual_nullable text;
    v_drift text[] := ARRAY[]::text[];
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema='public' AND table_name='agent_build_artifacts'
    ) INTO v_table_exists;

    IF v_table_exists THEN
        FOR v_expected IN
            SELECT * FROM (VALUES
                ('id','uuid','NO'),
                ('project_id','uuid','NO'),
                ('task_id','uuid','NO'),
                ('architecture_id','uuid','YES'),
                ('spec_id','uuid','YES'),
                ('type','text','NO'),
                ('name','text','NO'),
                ('content','text','NO'),
                ('content_hash','text','NO'),
                ('content_bytes','integer','NO'),
                ('deploy_instructions','text','YES'),
                ('status','text','NO'),
                ('rejection_reason','text','YES'),
                ('version','integer','NO'),
                ('parent_artifact_id','uuid','YES'),
                ('root_artifact_id','uuid','YES'),
                ('idempotency_key','text','YES'),
                ('request_payload_hash','text','YES'),
                ('stored_response','jsonb','YES'),
                ('requested_by','text','YES'),
                ('notes','text','YES'),
                ('created_at','timestamp with time zone','NO'),
                ('updated_at','timestamp with time zone','NO')
            ) AS t(col, typ, nullable)
        LOOP
            SELECT data_type, is_nullable INTO v_actual_type, v_actual_nullable
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='agent_build_artifacts'
              AND column_name = v_expected.col;
            IF v_actual_type IS NULL THEN
                v_drift := v_drift || (v_expected.col || ' (missing)');
            ELSIF v_actual_type <> v_expected.typ OR v_actual_nullable <> v_expected.nullable THEN
                v_drift := v_drift || (v_expected.col || ' (expected ' || v_expected.typ ||
                    ' ' || v_expected.nullable || ', got ' || v_actual_type ||
                    ' ' || v_actual_nullable || ')');
            END IF;
        END LOOP;
        IF array_length(v_drift, 1) > 0 THEN
            RAISE EXCEPTION
                'agent_build_artifacts exists with shape drift: %. Manual reconciliation required.',
                v_drift;
        END IF;
    END IF;
END $$;

-----------------------------------------------
-- 1. agent_build_artifacts
-- One row per artifact emitted by the Builder Agent. type CHECK list matches the
-- system-prompt enum. status starts at 'draft', flips to 'complete' once Builder
-- finishes, then to 'verified' when Verification Agent's row points at this one and
-- passes (or 'rejected' if not).
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_build_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES agent_projects(id) ON DELETE RESTRICT,
    task_id UUID NOT NULL REFERENCES agent_tasks(id) ON DELETE RESTRICT,
    architecture_id UUID REFERENCES agent_architectures(id) ON DELETE SET NULL,
    spec_id UUID REFERENCES agent_specifications(id) ON DELETE SET NULL,
    type TEXT NOT NULL
        CHECK (type IN ('supabase_sql','n8n_workflow','prompt','edge_function','script','config','doc')),
    name TEXT NOT NULL,
    content TEXT NOT NULL,
    content_hash TEXT NOT NULL,  -- sha256 hex of content; used by Verification Agent
                                 -- to detect drift between artifact and verified body
    content_bytes INT NOT NULL,
    deploy_instructions TEXT,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','complete','verified','rejected')),
    rejection_reason TEXT,
    version INT NOT NULL DEFAULT 1
        CHECK (version >= 1),
    parent_artifact_id UUID REFERENCES agent_build_artifacts(id) ON DELETE SET NULL,
    root_artifact_id UUID REFERENCES agent_build_artifacts(id) ON DELETE SET NULL,
    idempotency_key TEXT,
    request_payload_hash TEXT,  -- sha256 hex of canonical request payload; used for
                                -- same-key/different-payload conflict detection (F7)
    stored_response JSONB,      -- response returned for the first insert under this
                                -- idempotency_key; replayed on safe-retry
    requested_by TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT bld_no_self_parent CHECK (id <> parent_artifact_id),
    CONSTRAINT bld_name_nonempty CHECK (length(trim(name)) > 0),
    CONSTRAINT bld_content_nonempty CHECK (length(content) > 0),
    CONSTRAINT bld_content_hash_format CHECK (length(content_hash) = 64),
    -- Use octet_length (byte count) not length (character count) — content_bytes is
    -- a BYTE count by name and contract. Closed by codex pass 1 F6.
    CONSTRAINT bld_content_bytes_matches CHECK (content_bytes = octet_length(content)),
    CONSTRAINT bld_rejected_has_reason CHECK (
        (status = 'rejected' AND rejection_reason IS NOT NULL AND length(trim(rejection_reason)) > 0)
        OR
        (status <> 'rejected')
    ),
    -- Idempotency triple consistency: key, hash, response are all-or-nothing.
    -- Hash MUST be sha256 hex (64 chars). Hardened by codex pass 1 finding F7.
    CONSTRAINT bld_idem_triple_consistent CHECK (
        (idempotency_key IS NULL AND request_payload_hash IS NULL AND stored_response IS NULL)
        OR
        (idempotency_key IS NOT NULL AND length(trim(idempotency_key)) > 0
         AND request_payload_hash IS NOT NULL AND length(request_payload_hash) = 64
         AND stored_response IS NOT NULL)
    )
);

-- Idempotency uniqueness — global on idempotency_key.
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_build_artifacts_idempotency
    ON agent_build_artifacts (idempotency_key)
    WHERE idempotency_key IS NOT NULL;

-- Lineage uniqueness: at most one row per (task_id, version) — prevents revision races
-- within a single task.
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_build_artifacts_task_version
    ON agent_build_artifacts (task_id, version);

CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_project ON agent_build_artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_task ON agent_build_artifacts(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_architecture ON agent_build_artifacts(architecture_id);
CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_spec ON agent_build_artifacts(spec_id);
CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_type ON agent_build_artifacts(type);
CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_status ON agent_build_artifacts(status);
CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_hash ON agent_build_artifacts(content_hash);
CREATE INDEX IF NOT EXISTS idx_agent_build_artifacts_root ON agent_build_artifacts(root_artifact_id);

-----------------------------------------------
-- 2. updated_at trigger — no-op-safe
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_agent_build_artifacts_updated_at()
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

DROP TRIGGER IF EXISTS trg_agent_build_artifacts_updated ON agent_build_artifacts;
CREATE TRIGGER trg_agent_build_artifacts_updated
    BEFORE UPDATE ON agent_build_artifacts
    FOR EACH ROW EXECUTE FUNCTION update_agent_build_artifacts_updated_at();

-----------------------------------------------
-- 3. RLS — service_role only
-----------------------------------------------
ALTER TABLE agent_build_artifacts ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE r record;
BEGIN
    FOR r IN
        SELECT polname FROM pg_policy WHERE polrelid = 'public.agent_build_artifacts'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.agent_build_artifacts', r.polname);
    END LOOP;
END $$;

CREATE POLICY "service_role_full" ON agent_build_artifacts
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-----------------------------------------------
-- 4. Late-added FK from agent_verifications.build_artifact_id → agent_build_artifacts(id).
--    The verification migration left this out (AR-V1) because agent_build_artifacts
--    did not exist yet. This block installs it now. Idempotent (skips if present).
--    NOT Postgres-DEFERRABLE — constraint validates at row write time. Verification
--    workflow inserts the artifact BEFORE the verification row, so immediate
--    enforcement is the correct semantics (closes codex pass 1 F9 wording).
--    ON DELETE SET NULL so administrative artifact removal does not cascade-delete
--    verification history.
-----------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'agent_verifications_build_artifact_id_fkey'
          AND conrelid = 'public.agent_verifications'::regclass
    ) THEN
        ALTER TABLE agent_verifications
        ADD CONSTRAINT agent_verifications_build_artifact_id_fkey
        FOREIGN KEY (build_artifact_id)
        REFERENCES agent_build_artifacts(id)
        ON DELETE SET NULL;
    END IF;
END $$;

-----------------------------------------------
-- 5. RPC: create_build_artifact
-- Inserts a new artifact row. Validates task/project/architecture/spec lineage.
-- Idempotency-safe: replays existing row when idempotency_key matches.
-- Version-safe: locks the task's prior artifact rows FOR UPDATE before computing
-- the next version.
-----------------------------------------------
CREATE OR REPLACE FUNCTION create_build_artifact(
    p_project_id UUID,
    p_task_id UUID,
    p_architecture_id UUID,
    p_spec_id UUID,
    p_type TEXT,
    p_name TEXT,
    p_content TEXT,
    p_content_hash TEXT,
    p_deploy_instructions TEXT,
    p_status TEXT,
    p_rejection_reason TEXT,
    p_parent_artifact_id UUID,
    p_idempotency_key TEXT,
    p_request_payload_hash TEXT,
    p_stored_response JSONB,
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
    v_root_id UUID;
    v_existing_row agent_build_artifacts%ROWTYPE;
    v_task_project_id UUID;
    v_arch_project_id UUID;
    v_arch_spec_id UUID;
    v_spec_project_id UUID;
    v_parent_task_id UUID;
    v_parent_project_id UUID;
    v_allowed_type TEXT[] := ARRAY['supabase_sql','n8n_workflow','prompt','edge_function','script','config','doc'];
    v_allowed_status TEXT[] := ARRAY['draft','complete','verified','rejected'];
    v_content_bytes INT;
BEGIN
    -- Argument validation.
    IF NOT (COALESCE(p_type,'') = ANY (v_allowed_type)) THEN
        RETURN jsonb_build_object('error', 'invalid_type', 'detail', p_type);
    END IF;
    IF NOT (COALESCE(p_status,'draft') = ANY (v_allowed_status)) THEN
        RETURN jsonb_build_object('error', 'invalid_status', 'detail', p_status);
    END IF;
    IF p_name IS NULL OR length(trim(p_name)) = 0 THEN
        RETURN jsonb_build_object('error', 'name_required');
    END IF;
    IF p_content IS NULL OR length(p_content) = 0 THEN
        RETURN jsonb_build_object('error', 'content_required');
    END IF;
    IF p_content_hash IS NULL OR length(p_content_hash) <> 64 THEN
        RETURN jsonb_build_object('error', 'invalid_content_hash');
    END IF;
    IF COALESCE(p_status,'draft') = 'rejected'
       AND (p_rejection_reason IS NULL OR length(trim(p_rejection_reason)) = 0) THEN
        RETURN jsonb_build_object('error', 'rejection_reason_required');
    END IF;
    -- Idempotency-triple parameter validation. Must be all-or-nothing (closes F7).
    IF p_idempotency_key IS NOT NULL THEN
        IF p_request_payload_hash IS NULL OR length(p_request_payload_hash) <> 64 THEN
            RETURN jsonb_build_object('error', 'invalid_payload_hash');
        END IF;
        IF p_stored_response IS NULL THEN
            RETURN jsonb_build_object('error', 'stored_response_required');
        END IF;
    END IF;
    -- Byte length (not character length) — matches the BYTE semantics of content_bytes
    -- and the bld_content_bytes_matches CHECK (closes F6).
    v_content_bytes := octet_length(p_content);

    -- Reject NULL scope inputs BEFORE taking the advisory lock — hashtextextended on
    -- a NULL key raises before the function can return a structured error response
    -- (closes codex pass 2 P2-F3).
    IF p_task_id IS NULL THEN
        RETURN jsonb_build_object('error', 'task_id_required');
    END IF;
    IF p_project_id IS NULL THEN
        RETURN jsonb_build_object('error', 'project_id_required');
    END IF;

    -- Serialize all create-revisions for this task. Without this, concurrent retries
    -- compute the same MAX(version) and race on uq_agent_build_artifacts_task_version.
    -- Closes codex pass 1 F2. Lock order: advisory lock FIRST, then row locks (so
    -- update_artifact_verification_outcome must follow the same order — closed by
    -- pass 2 P2-F1).
    PERFORM pg_advisory_xact_lock(
        hashtextextended('agent_build_artifacts:' || p_task_id::text, 0)
    );

    -- Idempotency replay/conflict resolution (closes F7).
    IF p_idempotency_key IS NOT NULL THEN
        SELECT * INTO v_existing_row
        FROM agent_build_artifacts b
        WHERE b.idempotency_key = p_idempotency_key
        LIMIT 1;
        IF v_existing_row.id IS NOT NULL THEN
            IF v_existing_row.request_payload_hash = p_request_payload_hash THEN
                RETURN jsonb_build_object(
                    'replayed', true,
                    'artifact_id', v_existing_row.id,
                    'response', v_existing_row.stored_response
                );
            ELSE
                RETURN jsonb_build_object(
                    'error', 'idempotency_conflict',
                    'detail', 'same idempotency_key, different request payload'
                );
            END IF;
        END IF;
    END IF;

    -- TOCTOU-safe parent-row validation (closes codex pass 4 finding). FOR SHARE
    -- prevents admin paths from mutating these rows between validation and our
    -- artifact INSERT. The locks auto-release at commit/rollback.

    -- Task gate: task must exist and belong to project.
    SELECT project_id INTO v_task_project_id FROM agent_tasks WHERE id = p_task_id FOR SHARE;
    IF v_task_project_id IS NULL THEN
        RETURN jsonb_build_object('error', 'task_not_found');
    END IF;
    IF v_task_project_id <> p_project_id THEN
        RETURN jsonb_build_object('error', 'task_project_mismatch');
    END IF;

    -- Architecture (optional): must exist and belong to project; spec must match if both supplied.
    IF p_architecture_id IS NOT NULL THEN
        SELECT project_id, spec_id INTO v_arch_project_id, v_arch_spec_id
        FROM agent_architectures WHERE id = p_architecture_id FOR SHARE;
        IF v_arch_project_id IS NULL THEN
            RETURN jsonb_build_object('error', 'architecture_not_found');
        END IF;
        IF v_arch_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'architecture_project_mismatch');
        END IF;
        IF p_spec_id IS NOT NULL AND v_arch_spec_id <> p_spec_id THEN
            RETURN jsonb_build_object('error', 'architecture_spec_mismatch');
        END IF;
    END IF;

    -- Spec (optional): must exist and belong to project.
    IF p_spec_id IS NOT NULL THEN
        SELECT project_id INTO v_spec_project_id FROM agent_specifications WHERE id = p_spec_id FOR SHARE;
        IF v_spec_project_id IS NULL THEN
            RETURN jsonb_build_object('error', 'spec_not_found');
        END IF;
        IF v_spec_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'spec_project_mismatch');
        END IF;
    END IF;

    -- Parent lineage validation.
    IF p_parent_artifact_id IS NOT NULL THEN
        SELECT task_id, project_id, root_artifact_id
          INTO v_parent_task_id, v_parent_project_id, v_root_id
        FROM agent_build_artifacts
        WHERE id = p_parent_artifact_id
        FOR UPDATE;
        IF v_parent_task_id IS NULL THEN
            RETURN jsonb_build_object('error', 'parent_not_found');
        END IF;
        IF v_parent_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'parent_project_mismatch');
        END IF;
        IF v_parent_task_id <> p_task_id THEN
            RETURN jsonb_build_object('error', 'parent_task_mismatch');
        END IF;
        IF v_root_id IS NULL THEN
            v_root_id := p_parent_artifact_id;
            UPDATE agent_build_artifacts SET root_artifact_id = p_parent_artifact_id
            WHERE id = p_parent_artifact_id;
        END IF;
    END IF;

    -- Compute next version. Race-free under the advisory lock taken above.
    SELECT COALESCE(MAX(version), 0) + 1 INTO v_version
    FROM agent_build_artifacts
    WHERE task_id = p_task_id;

    BEGIN
        INSERT INTO agent_build_artifacts (
            project_id, task_id, architecture_id, spec_id,
            type, name, content, content_hash, content_bytes,
            deploy_instructions, status, rejection_reason,
            version, parent_artifact_id, root_artifact_id,
            idempotency_key, request_payload_hash, stored_response,
            requested_by, notes
        ) VALUES (
            p_project_id, p_task_id, p_architecture_id, p_spec_id,
            p_type, p_name, p_content, p_content_hash, v_content_bytes,
            p_deploy_instructions,
            COALESCE(p_status, 'draft'),
            p_rejection_reason,
            v_version,
            p_parent_artifact_id,
            v_root_id,
            p_idempotency_key,
            p_request_payload_hash,
            p_stored_response,
            p_requested_by,
            p_notes
        )
        RETURNING id INTO v_new_id;
    EXCEPTION
        WHEN unique_violation THEN
            IF SQLERRM ILIKE '%uq_agent_build_artifacts_idempotency%'
               AND p_idempotency_key IS NOT NULL THEN
                -- Concurrent insert won — reconcile with payload-hash check.
                SELECT * INTO v_existing_row
                FROM agent_build_artifacts b
                WHERE b.idempotency_key = p_idempotency_key
                LIMIT 1;
                IF v_existing_row.id IS NOT NULL THEN
                    IF v_existing_row.request_payload_hash = p_request_payload_hash THEN
                        RETURN jsonb_build_object(
                            'replayed', true,
                            'artifact_id', v_existing_row.id,
                            'response', v_existing_row.stored_response
                        );
                    ELSE
                        RETURN jsonb_build_object(
                            'error', 'idempotency_conflict',
                            'detail', 'concurrent insert with different payload'
                        );
                    END IF;
                END IF;
            END IF;
            IF SQLERRM ILIKE '%uq_agent_build_artifacts_task_version%' THEN
                RETURN jsonb_build_object('error', 'version_race',
                    'detail', 'concurrent revision collision on (task_id, version); retry');
            END IF;
            RETURN jsonb_build_object('error', 'unique_violation', 'detail', SQLERRM);
    END;

    -- Self-root a fresh lineage.
    IF v_root_id IS NULL THEN
        UPDATE agent_build_artifacts SET root_artifact_id = id WHERE id = v_new_id;
    END IF;

    RETURN jsonb_build_object('replayed', false,
        'artifact', (SELECT row_to_json(b)::jsonb FROM agent_build_artifacts b WHERE b.id = v_new_id));
END;
$$;

-----------------------------------------------
-- 6. RPC: update_artifact_verification_outcome
-- Called by the Verification Agent (or its workflow) when a verification row's
-- terminal codex status is reached. Sets agent_build_artifacts.status to one of
-- {verified, rejected} based on the verification outcome.
-- Refuses to demote a 'verified' row; refuses to operate on a row whose latest
-- version is NOT this artifact (operators must update the latest).
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_artifact_verification_outcome(
    p_artifact_id UUID,
    p_outcome TEXT,
    p_rejection_reason TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_current_status TEXT;
    v_task_id UUID;
    v_version INT;
    v_latest_version INT;
    v_allowed TEXT[] := ARRAY['verified','rejected'];
BEGIN
    IF NOT (p_outcome = ANY (v_allowed)) THEN
        RETURN jsonb_build_object('error', 'invalid_outcome', 'detail', p_outcome);
    END IF;
    IF p_outcome = 'rejected'
       AND (p_rejection_reason IS NULL OR length(trim(p_rejection_reason)) = 0) THEN
        RETURN jsonb_build_object('error', 'rejection_reason_required');
    END IF;
    IF p_artifact_id IS NULL THEN
        RETURN jsonb_build_object('error', 'artifact_id_required');
    END IF;

    -- Read task_id WITHOUT a row lock so we can compute the advisory-lock key first.
    -- Lock-order rule (closes codex pass 2 P2-F1): advisory lock BEFORE any
    -- agent_build_artifacts row lock, matching create_build_artifact's order.
    SELECT task_id INTO v_task_id
    FROM agent_build_artifacts WHERE id = p_artifact_id;
    IF v_task_id IS NULL THEN
        RETURN jsonb_build_object('error', 'artifact_not_found');
    END IF;

    -- Serialize against create_build_artifact for the SAME task. Taking the advisory
    -- lock BEFORE FOR UPDATE means concurrent create/update for the same task always
    -- queue on the advisory lock and never deadlock on opposing row locks.
    PERFORM pg_advisory_xact_lock(
        hashtextextended('agent_build_artifacts:' || v_task_id::text, 0)
    );

    -- Re-read under the advisory lock with FOR UPDATE — this is now the authoritative
    -- view of the row's status/version. Anything we observed earlier (without lock)
    -- could already be stale.
    SELECT status, version INTO v_current_status, v_version
    FROM agent_build_artifacts WHERE id = p_artifact_id FOR UPDATE;
    IF v_current_status IS NULL THEN
        -- Row deleted between the unlocked read and the locked re-read.
        RETURN jsonb_build_object('error', 'artifact_not_found');
    END IF;
    IF v_current_status = 'verified' THEN
        RETURN jsonb_build_object('error', 'already_verified');
    END IF;
    IF v_current_status = 'rejected' AND p_outcome = 'verified' THEN
        RETURN jsonb_build_object('error', 'cannot_verify_rejected',
            'detail', 'create a new artifact revision instead');
    END IF;

    -- Refuse to update a non-latest artifact for the task. Under the advisory lock,
    -- create_build_artifact cannot insert a newer-version row between this MAX
    -- compute and the UPDATE commit.
    SELECT MAX(version) INTO v_latest_version
    FROM agent_build_artifacts WHERE task_id = v_task_id;
    IF v_latest_version IS NOT NULL AND v_latest_version > v_version THEN
        RETURN jsonb_build_object('error', 'not_latest_version',
            'detail', 'a newer revision exists for this task; update that instead');
    END IF;

    UPDATE agent_build_artifacts
    SET status = p_outcome,
        rejection_reason = CASE WHEN p_outcome = 'rejected' THEN p_rejection_reason ELSE NULL END
    WHERE id = p_artifact_id;

    RETURN (SELECT row_to_json(b)::jsonb FROM agent_build_artifacts b WHERE b.id = p_artifact_id);
END;
$$;

-----------------------------------------------
-- 7. Grants — least privilege
-----------------------------------------------
REVOKE ALL ON FUNCTION create_build_artifact(
    UUID,UUID,UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,TEXT,JSONB,TEXT,TEXT
) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION update_artifact_verification_outcome(UUID,TEXT,TEXT)
    FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION create_build_artifact(
    UUID,UUID,UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,TEXT,JSONB,TEXT,TEXT
) TO service_role;
GRANT EXECUTE ON FUNCTION update_artifact_verification_outcome(UUID,TEXT,TEXT) TO service_role;

-----------------------------------------------
-- 8. Accepted-risk register
-----------------------------------------------
COMMENT ON TABLE agent_build_artifacts IS
    'Builder Agent canonical store. Accepted residual risks:
     • AR-B1: content stored verbatim in a TEXT column with no size cap. Callers SHOULD store oversized artifacts (>1 MiB) in Supabase Storage and put a reference in content. A length CHECK can be added in v2 once we have a stable budget.
     • AR-B2: content_hash is the canonical drift detector — Verification Agent compares against this on every verification. Callers MUST supply sha256 hex over the exact content bytes.
     • AR-B3: status=verified is sticky; rejected → verified requires a new revision via parent_artifact_id.
     • AR-B4: architecture_id is optional because ad-hoc infra-fix tasks may not flow through Architecture Agent. Validation kicks in only when supplied.
     • AR-B5: LAN-only HTTP transport — token + firewall is the compensating control.';

COMMENT ON FUNCTION create_build_artifact(
    UUID,UUID,UUID,UUID,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,TEXT,UUID,TEXT,TEXT,JSONB,TEXT,TEXT
) IS
    'Creates a new build artifact row. Validates task/architecture/spec lineage. Computes the next version per task scope under a per-task pg_advisory_xact_lock so concurrent creates serialize cleanly. Idempotency-safe via (idempotency_key, request_payload_hash, stored_response): same key + same hash → stored_response replayed; same key + different hash → idempotency_conflict.';
COMMENT ON FUNCTION update_artifact_verification_outcome(UUID,TEXT,TEXT) IS
    'Transitions an artifact to verified or rejected based on Verification Agent outcome. Refuses to demote a verified row, refuses non-latest updates, requires rejection_reason on rejected.';
