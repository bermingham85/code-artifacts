-- AGEN-SCRPT-architecture-supabase-migration-v1.sql
-- Architecture Agent — Supabase schema
-- Date: 2026-05-23
-- Run on: Supabase project ${SUPABASE_PROJECT_REF} (resolve concrete project ref from the ops config / secrets registry; never commit the concrete value here)
--
-- Pre-conditions verified by audit (2026-05-23T04:31Z):
--   - agent_projects exists, FK target
--   - agent_tasks exists, FK target (task_id optional on a row)
--   - agent_specifications exists, FK target (spec_id REQUIRED — every architecture
--     must point at an approved/reviewed spec)
--   - agent_architectures DOES NOT EXIST (this migration creates it)
--   - Migration coordinator task 73555d72 is in_progress
--
-- Contract honoured (per AGEN-HNDV-arch-v2):
--   - Revision scope = composite (project_id, spec_id). version starts at 1, monotonic
--     per scope, race-protected by FOR UPDATE on parent row inside RPC.
--   - At most ONE non-superseded row per (project_id, spec_id) — partial unique index.
--   - Composite uniqueness on (project_id, spec_id, version) — full unique index.
--   - Idempotency uniqueness on (project_id, spec_id, action, idempotency_key).
--   - Safe-retry replay: same key + same payload → stored response, no new revision.
--   - Conflict: same key + different payload → 409 (RPC returns
--     {error:'idempotency_conflict'}).
--   - get_latest is a non-idempotent live read — RPC implementation here, idempotency
--     store untouched.
--
-- Idempotency: safe to re-run. Pre-flight column guard fails fast on shape divergence.

-----------------------------------------------
-- 0. Pre-flight shape guard — column NAME + TYPE + NULLABILITY (closes codex pass 1 F4)
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
        WHERE table_schema='public' AND table_name='agent_architectures'
    ) INTO v_table_exists;

    IF v_table_exists THEN
        FOR v_expected IN
            SELECT * FROM (VALUES
                ('id','uuid','NO'),
                ('project_id','uuid','NO'),
                ('spec_id','uuid','NO'),
                ('task_id','uuid','YES'),
                ('action','text','NO'),
                ('components','jsonb','NO'),
                ('tasks','jsonb','NO'),
                ('build_order','jsonb','NO'),
                ('dependencies','jsonb','NO'),
                ('status','text','NO'),
                ('version','integer','NO'),
                ('parent_architecture_id','uuid','YES'),
                ('root_architecture_id','uuid','YES'),
                ('idempotency_key','text','YES'),
                ('request_payload_hash','text','YES'),
                ('stored_response','jsonb','YES'),
                ('summary','text','YES'),
                ('requested_by','text','YES'),
                ('notes','text','YES'),
                ('created_at','timestamp with time zone','NO'),
                ('updated_at','timestamp with time zone','NO')
            ) AS t(col, typ, nullable)
        LOOP
            SELECT data_type, is_nullable INTO v_actual_type, v_actual_nullable
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='agent_architectures'
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
                'agent_architectures exists with shape drift: %. Manual reconciliation required.',
                v_drift;
        END IF;
    END IF;
END $$;

-----------------------------------------------
-- 1. agent_architectures
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_architectures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES agent_projects(id) ON DELETE RESTRICT,
    spec_id UUID NOT NULL REFERENCES agent_specifications(id) ON DELETE RESTRICT,
    task_id UUID REFERENCES agent_tasks(id) ON DELETE SET NULL,
    action TEXT NOT NULL DEFAULT 'decompose'
        CHECK (action IN ('decompose','refine')),
    components JSONB NOT NULL DEFAULT '[]'::jsonb,
    tasks JSONB NOT NULL DEFAULT '[]'::jsonb,
    build_order JSONB NOT NULL DEFAULT '[]'::jsonb,
    dependencies JSONB NOT NULL DEFAULT '{}'::jsonb,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','reviewed','superseded')),
    version INT NOT NULL DEFAULT 1
        CHECK (version >= 1),
    parent_architecture_id UUID REFERENCES agent_architectures(id) ON DELETE SET NULL,
    root_architecture_id UUID REFERENCES agent_architectures(id) ON DELETE SET NULL,
    idempotency_key TEXT,
    request_payload_hash TEXT,  -- sha256 hex of the canonical request payload; used for
                                -- 409 same-key/different-payload detection
    stored_response JSONB,      -- the response returned for the FIRST insert under this
                                -- idempotency_key; replayed on safe-retry
    summary TEXT,
    requested_by TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT arch_no_self_parent CHECK (id <> parent_architecture_id),
    CONSTRAINT arch_components_is_array CHECK (jsonb_typeof(components) = 'array'),
    CONSTRAINT arch_tasks_is_array CHECK (jsonb_typeof(tasks) = 'array'),
    CONSTRAINT arch_build_order_is_array CHECK (jsonb_typeof(build_order) = 'array'),
    CONSTRAINT arch_dependencies_is_object CHECK (jsonb_typeof(dependencies) = 'object'),
    CONSTRAINT arch_idem_hash_iff_key CHECK (
        (idempotency_key IS NULL AND request_payload_hash IS NULL AND stored_response IS NULL)
        OR
        (idempotency_key IS NOT NULL AND length(trim(idempotency_key)) > 0
         AND request_payload_hash IS NOT NULL AND length(request_payload_hash) = 64
         AND stored_response IS NOT NULL)
    ),
    CONSTRAINT arch_summary_not_too_large CHECK (summary IS NULL OR length(summary) <= 10000)
);

-- Composite versioning uniqueness: at most one row per (project_id, spec_id, version).
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_architectures_scope_version
    ON agent_architectures (project_id, spec_id, version);

-- At most one non-superseded row per (project_id, spec_id) — enforces the
-- single-active-architecture invariant from the contract.
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_architectures_active_per_scope
    ON agent_architectures (project_id, spec_id)
    WHERE status <> 'superseded';

-- Idempotency uniqueness: (project_id, spec_id, action, idempotency_key) — decompose
-- and refine keys are independent because action is part of the tuple.
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_architectures_idempotency
    ON agent_architectures (project_id, spec_id, action, idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_agent_architectures_project ON agent_architectures(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_architectures_spec ON agent_architectures(spec_id);
CREATE INDEX IF NOT EXISTS idx_agent_architectures_task ON agent_architectures(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_architectures_status ON agent_architectures(status);
CREATE INDEX IF NOT EXISTS idx_agent_architectures_root ON agent_architectures(root_architecture_id);
CREATE INDEX IF NOT EXISTS idx_agent_architectures_parent ON agent_architectures(parent_architecture_id);

-----------------------------------------------
-- 2. updated_at trigger — no-op-safe
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_agent_architectures_updated_at()
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

DROP TRIGGER IF EXISTS trg_agent_architectures_updated ON agent_architectures;
CREATE TRIGGER trg_agent_architectures_updated
    BEFORE UPDATE ON agent_architectures
    FOR EACH ROW EXECUTE FUNCTION update_agent_architectures_updated_at();

-----------------------------------------------
-- 3. RLS — service_role only
-----------------------------------------------
ALTER TABLE agent_architectures ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE r record;
BEGIN
    FOR r IN
        SELECT polname FROM pg_policy WHERE polrelid = 'public.agent_architectures'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.agent_architectures', r.polname);
    END LOOP;
END $$;

CREATE POLICY "service_role_full" ON agent_architectures
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-----------------------------------------------
-- 4. RPC: create_architecture_revision
-- Creates a new (decompose | refine) row under composite scope (project_id, spec_id).
--   - decompose: only allowed when no non-superseded row exists for the scope.
--   - refine:    requires at least one row in the scope; supersedes prior non-superseded
--                rows atomically. Version computed under FOR UPDATE on parent row.
-- Idempotency semantics (per HANDOVER):
--   - Same key + same payload hash → return stored response, no new row.
--   - Same key + different payload hash → return {error:'idempotency_conflict'}.
-- Spec gate: agent_specifications.status MUST be in {reviewed, approved}.
-----------------------------------------------
CREATE OR REPLACE FUNCTION create_architecture_revision(
    p_action TEXT,
    p_project_id UUID,
    p_spec_id UUID,
    p_task_id UUID,
    p_components JSONB,
    p_tasks JSONB,
    p_build_order JSONB,
    p_dependencies JSONB,
    p_status TEXT,
    p_idempotency_key TEXT,
    p_request_payload_hash TEXT,
    p_stored_response JSONB,
    p_summary TEXT,
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
    v_parent_id UUID;
    v_existing_row agent_architectures%ROWTYPE;
    v_existing_active_id UUID;
    v_spec_project_id UUID;
    v_spec_status TEXT;
    v_task_project_id UUID;
    v_allowed_action TEXT[] := ARRAY['decompose','refine'];
    v_allowed_insert_status TEXT[] := ARRAY['draft','reviewed'];
BEGIN
    -- Argument validation.
    IF NOT (COALESCE(p_action,'decompose') = ANY (v_allowed_action)) THEN
        RETURN jsonb_build_object('error', 'invalid_action', 'detail', p_action);
    END IF;
    IF NOT (COALESCE(p_status,'draft') = ANY (v_allowed_insert_status)) THEN
        RETURN jsonb_build_object('error', 'invalid_status', 'detail', p_status);
    END IF;
    IF p_idempotency_key IS NULL OR length(trim(p_idempotency_key)) = 0 THEN
        RETURN jsonb_build_object('error', 'idempotency_key_required');
    END IF;
    IF p_request_payload_hash IS NULL OR length(p_request_payload_hash) <> 64 THEN
        RETURN jsonb_build_object('error', 'invalid_payload_hash');
    END IF;
    IF p_stored_response IS NULL THEN
        RETURN jsonb_build_object('error', 'stored_response_required');
    END IF;
    IF p_components IS NOT NULL AND jsonb_typeof(p_components) <> 'array' THEN
        RETURN jsonb_build_object('error', 'components_not_array');
    END IF;
    IF p_tasks IS NOT NULL AND jsonb_typeof(p_tasks) <> 'array' THEN
        RETURN jsonb_build_object('error', 'tasks_not_array');
    END IF;
    IF p_build_order IS NOT NULL AND jsonb_typeof(p_build_order) <> 'array' THEN
        RETURN jsonb_build_object('error', 'build_order_not_array');
    END IF;
    IF p_dependencies IS NOT NULL AND jsonb_typeof(p_dependencies) <> 'object' THEN
        RETURN jsonb_build_object('error', 'dependencies_not_object');
    END IF;

    -- Reject NULL scope inputs BEFORE taking the advisory lock — pg_advisory_xact_lock
    -- on a NULL key raises a runtime error, which would mask the structured
    -- {error:'...required'} response (analogous to codex pass 2 P2-F3 for builder).
    IF p_project_id IS NULL THEN
        RETURN jsonb_build_object('error', 'project_id_required');
    END IF;
    IF p_spec_id IS NULL THEN
        RETURN jsonb_build_object('error', 'spec_id_required');
    END IF;

    -- Serialize all writes against the composite scope. Without this, concurrent
    -- decompose calls race on the MAX(version) compute (codex pass 1 F10) and
    -- concurrent refines can collide with each other before the supersede commits.
    -- hashtextextended is xact-scoped so the lock auto-releases at commit/rollback.
    PERFORM pg_advisory_xact_lock(
        hashtextextended('agent_architectures:' || p_project_id::text || ':' || p_spec_id::text, 0)
    );

    -- Spec gate (TOCTOU-safe — closes codex pass 3 finding): re-read the spec row
    -- under FOR SHARE AFTER the advisory lock. This prevents an admin path from
    -- demoting the spec (e.g. 'reviewed' → 'superseded' via approve_specification of
    -- a sibling) between validation and insert. FOR SHARE permits concurrent readers
    -- but blocks rewrites of the spec row until this transaction commits.
    SELECT project_id, status INTO v_spec_project_id, v_spec_status
    FROM agent_specifications WHERE id = p_spec_id FOR SHARE;
    IF v_spec_project_id IS NULL THEN
        RETURN jsonb_build_object('error', 'spec_not_found');
    END IF;
    IF v_spec_project_id <> p_project_id THEN
        RETURN jsonb_build_object('error', 'spec_project_mismatch');
    END IF;
    IF v_spec_status NOT IN ('reviewed','approved') THEN
        RETURN jsonb_build_object('error', 'spec_not_reviewable', 'detail', v_spec_status);
    END IF;

    -- task_id (if supplied) must exist and belong to the same project. Same FOR SHARE
    -- semantics — a concurrent admin path cannot move the task to a different project
    -- between validation and insert.
    IF p_task_id IS NOT NULL THEN
        SELECT project_id INTO v_task_project_id FROM agent_tasks WHERE id = p_task_id FOR SHARE;
        IF v_task_project_id IS NULL THEN
            RETURN jsonb_build_object('error', 'task_not_found');
        END IF;
        IF v_task_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'task_project_mismatch');
        END IF;
    END IF;

    -- Idempotency replay/conflict resolution.
    -- The (project_id, spec_id, action, idempotency_key) index ensures uniqueness.
    SELECT * INTO v_existing_row
    FROM agent_architectures a
    WHERE a.project_id = p_project_id
      AND a.spec_id = p_spec_id
      AND a.action = p_action
      AND a.idempotency_key = p_idempotency_key
    LIMIT 1;
    IF v_existing_row.id IS NOT NULL THEN
        IF v_existing_row.request_payload_hash = p_request_payload_hash THEN
            RETURN jsonb_build_object(
                'replayed', true,
                'architecture_id', v_existing_row.id,
                'response', v_existing_row.stored_response
            );
        ELSE
            RETURN jsonb_build_object(
                'error', 'idempotency_conflict',
                'detail', 'same idempotency_key, different request payload'
            );
        END IF;
    END IF;

    -- Lock the scope's active row (if any).
    SELECT id, version, root_architecture_id INTO v_existing_active_id, v_version, v_root_id
    FROM agent_architectures
    WHERE project_id = p_project_id AND spec_id = p_spec_id AND status <> 'superseded'
    FOR UPDATE;

    IF p_action = 'decompose' THEN
        IF v_existing_active_id IS NOT NULL THEN
            RETURN jsonb_build_object(
                'error', 'architecture_exists',
                'detail', 'use action=refine to create a new revision'
            );
        END IF;
        v_parent_id := NULL;
        v_root_id := NULL;  -- self-root after insert
    ELSE  -- refine
        IF v_existing_active_id IS NULL THEN
            RETURN jsonb_build_object(
                'error', 'architecture_not_found',
                'detail', 'no non-superseded architecture to refine'
            );
        END IF;
        v_parent_id := v_existing_active_id;
        -- supersede happens INSIDE the EXCEPTION-protected block below so the
        -- BEGIN/EXCEPTION savepoint rolls back the supersede if the INSERT errors
        -- (closes codex pass 2 P2-F2). DO NOT supersede here — only set the parent.
    END IF;

    -- Compute the next version. Under the advisory lock taken at the top of the RPC
    -- this is race-free for both decompose and refine in the same scope.
    SELECT COALESCE(MAX(version), 0) + 1 INTO v_version
    FROM agent_architectures
    WHERE project_id = p_project_id AND spec_id = p_spec_id;

    -- BEGIN/EXCEPTION establishes an implicit savepoint — any error inside rolls back
    -- both the supersede and the insert as one unit. This is what makes
    -- "supersede-then-insert" safe (closes codex pass 2 P2-F2). The partial
    -- single-active index permits supersede + insert in the same statement order
    -- because partial unique indexes are evaluated at statement boundary.
    BEGIN
        IF p_action = 'refine' THEN
            -- Supersede the prior active row. The row was locked FOR UPDATE above so
            -- no concurrent writer can intervene. If the subsequent INSERT raises,
            -- this UPDATE rolls back with the savepoint.
            UPDATE agent_architectures
            SET status = 'superseded'
            WHERE id = v_existing_active_id;
        END IF;

        INSERT INTO agent_architectures (
            project_id, spec_id, task_id, action,
            components, tasks, build_order, dependencies,
            status, version, parent_architecture_id, root_architecture_id,
            idempotency_key, request_payload_hash, stored_response,
            summary, requested_by, notes
        ) VALUES (
            p_project_id, p_spec_id, p_task_id, p_action,
            COALESCE(p_components, '[]'::jsonb),
            COALESCE(p_tasks, '[]'::jsonb),
            COALESCE(p_build_order, '[]'::jsonb),
            COALESCE(p_dependencies, '{}'::jsonb),
            COALESCE(p_status, 'draft'),
            v_version,
            v_parent_id,
            v_root_id,
            p_idempotency_key,
            p_request_payload_hash,
            p_stored_response,
            p_summary,
            p_requested_by,
            p_notes
        )
        RETURNING id INTO v_new_id;
    EXCEPTION
        WHEN unique_violation THEN
            -- The supersede UPDATE rolled back with this savepoint, so the prior
            -- active row remains active. Safe to return JSON.
            IF SQLERRM ILIKE '%uq_agent_architectures_idempotency%' THEN
                -- Race lost to a concurrent same-key insert — re-read and reconcile.
                SELECT * INTO v_existing_row
                FROM agent_architectures a
                WHERE a.project_id = p_project_id
                  AND a.spec_id = p_spec_id
                  AND a.action = p_action
                  AND a.idempotency_key = p_idempotency_key
                LIMIT 1;
                IF v_existing_row.request_payload_hash = p_request_payload_hash THEN
                    RETURN jsonb_build_object(
                        'replayed', true,
                        'architecture_id', v_existing_row.id,
                        'response', v_existing_row.stored_response
                    );
                ELSE
                    RETURN jsonb_build_object(
                        'error', 'idempotency_conflict',
                        'detail', 'concurrent insert with different payload'
                    );
                END IF;
            ELSIF SQLERRM ILIKE '%uq_agent_architectures_active_per_scope%' THEN
                RETURN jsonb_build_object(
                    'error', 'concurrent_active_revision',
                    'detail', 'another non-superseded row exists for this scope; serialization invariant breached'
                );
            ELSIF SQLERRM ILIKE '%uq_agent_architectures_scope_version%' THEN
                RETURN jsonb_build_object(
                    'error', 'version_race',
                    'detail', 'concurrent revision collision; retry'
                );
            ELSE
                RETURN jsonb_build_object('error', 'unique_violation', 'detail', SQLERRM);
            END IF;
    END;

    -- Self-root a fresh lineage.
    IF v_root_id IS NULL THEN
        UPDATE agent_architectures SET root_architecture_id = id WHERE id = v_new_id;
    END IF;

    RETURN jsonb_build_object(
        'replayed', false,
        'architecture_id', v_new_id,
        'architecture', (SELECT row_to_json(a)::jsonb FROM agent_architectures a WHERE a.id = v_new_id)
    );
END;
$$;

-----------------------------------------------
-- 5. RPC: get_latest_architecture
-- Non-idempotent live read. Returns highest-version non-superseded row for
-- (project_id, spec_id) — cross-project rows are NEVER returned even if the
-- spec_id collides (per Versioning rules in the integration contract).
-----------------------------------------------
CREATE OR REPLACE FUNCTION get_latest_architecture(
    p_project_id UUID,
    p_spec_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_row agent_architectures%ROWTYPE;
BEGIN
    SELECT * INTO v_row
    FROM agent_architectures a
    WHERE a.project_id = p_project_id
      AND a.spec_id = p_spec_id
      AND a.status <> 'superseded'
    ORDER BY a.version DESC, a.created_at DESC
    LIMIT 1;

    IF v_row.id IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN row_to_json(v_row)::jsonb;
END;
$$;

-----------------------------------------------
-- 6. RPC: mark_architecture_reviewed
-- Promotes a draft row to 'reviewed' after codex adversarial review closes clean
-- (no fresh CRITICAL/HIGH — enforced by caller). Refuses to promote a superseded row.
-----------------------------------------------
CREATE OR REPLACE FUNCTION mark_architecture_reviewed(
    p_architecture_id UUID,
    p_reviewer TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_status TEXT;
BEGIN
    IF p_reviewer IS NULL OR length(trim(p_reviewer)) = 0 THEN
        RETURN jsonb_build_object('error', 'reviewer_required');
    END IF;
    SELECT status INTO v_status FROM agent_architectures
    WHERE id = p_architecture_id FOR UPDATE;
    IF v_status IS NULL THEN
        RETURN jsonb_build_object('error', 'architecture_not_found');
    END IF;
    IF v_status = 'superseded' THEN
        RETURN jsonb_build_object('error', 'cannot_promote_superseded');
    END IF;
    IF v_status = 'reviewed' THEN
        RETURN jsonb_build_object('error', 'already_reviewed');
    END IF;
    UPDATE agent_architectures
    SET status = 'reviewed',
        notes = COALESCE(notes, '') ||
                CASE WHEN notes IS NULL OR length(notes) = 0 THEN '' ELSE E'\n' END ||
                '[reviewed by ' || p_reviewer || ' at ' || now()::text || ']'
    WHERE id = p_architecture_id;
    RETURN (SELECT row_to_json(a)::jsonb FROM agent_architectures a WHERE a.id = p_architecture_id);
END;
$$;

-----------------------------------------------
-- 7. Grants — least privilege
-----------------------------------------------
REVOKE ALL ON FUNCTION create_architecture_revision(
    TEXT,UUID,UUID,UUID,JSONB,JSONB,JSONB,JSONB,TEXT,TEXT,TEXT,JSONB,TEXT,TEXT,TEXT
) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION get_latest_architecture(UUID,UUID) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION mark_architecture_reviewed(UUID,TEXT) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION create_architecture_revision(
    TEXT,UUID,UUID,UUID,JSONB,JSONB,JSONB,JSONB,TEXT,TEXT,TEXT,JSONB,TEXT,TEXT,TEXT
) TO service_role;
GRANT EXECUTE ON FUNCTION get_latest_architecture(UUID,UUID) TO service_role;
GRANT EXECUTE ON FUNCTION mark_architecture_reviewed(UUID,TEXT) TO service_role;

-----------------------------------------------
-- 8. Accepted-risk register
-----------------------------------------------
COMMENT ON TABLE agent_architectures IS
    'Architecture Agent canonical store. Accepted residual risks:
     • AR-A1: tasks JSONB array carries decomposed task descriptors with estimated_hours ∈ [0.5, 2.0]; the range CHECK is enforced in the n8n workflow validation layer, not in SQL (the array is heterogeneous and SQL CHECK on JSONB array elements is brittle).
     • AR-A2: dependencies JSONB object validated for type=object only; cycle detection is the workflow''s responsibility.
     • AR-A3: get_latest is a non-idempotent live read by design — see HANDOVER §Idempotency rules.
     • AR-A4: cross-project spec_id collisions are NEVER returned by get_latest; the composite scope (project_id, spec_id) is the canonical key.
     • AR-A5: superseded is terminal; further changes require a new refine revision.
     • AR-A6: LAN-only HTTP transport — token + firewall is the compensating control.';

COMMENT ON FUNCTION create_architecture_revision(
    TEXT,UUID,UUID,UUID,JSONB,JSONB,JSONB,JSONB,TEXT,TEXT,TEXT,JSONB,TEXT,TEXT,TEXT
) IS
    'Creates a decompose (v1) or refine (v>=2) revision. Idempotency replay/conflict, version race, and active-row uniqueness are all enforced server-side. Spec gate: spec.status ∈ {reviewed, approved}.';
COMMENT ON FUNCTION get_latest_architecture(UUID,UUID) IS
    'Returns the highest-version non-superseded row for (project_id, spec_id), or NULL. Live read, never replayed.';
COMMENT ON FUNCTION mark_architecture_reviewed(UUID,TEXT) IS
    'Promotes draft → reviewed after codex adversarial review closes clean. Refuses superseded rows.';
