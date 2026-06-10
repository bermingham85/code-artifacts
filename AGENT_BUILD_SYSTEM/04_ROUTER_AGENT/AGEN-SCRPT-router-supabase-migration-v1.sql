-- AGEN-SCRPT-router-supabase-migration-v1.sql
-- Router Agent — Supabase schema
-- Date: 2026-05-23
-- Run on: Supabase project ylcepmvbjjnwmzvevxid
--
-- Pre-conditions verified by audit (2026-05-23T04:31Z):
--   - agent_projects exists, FK target (NULLABLE on a routing-log row: the very first
--     turn of a conversation may have no project yet — router can be called with only
--     a free-form request).
--   - agent_specifications, agent_tasks exist (FK targets, both optional on a row).
--   - agent_routing_logs DOES NOT EXIST (this migration creates it).
--   - Migration coordinator task 73555d72 is in_progress.
--
-- Idempotency: every CREATE uses IF NOT EXISTS; trigger DROP/CREATEs; every policy is
-- dropped before recreation. The migration is safe to re-run.
--
-- Pre-flight column guard fails fast if a shape-divergent table already exists.

-----------------------------------------------
-- 0. Pre-flight shape guard
-- Validates columns AND their types + nullability against the expected schema. A
-- column-presence-only guard (the original v0 pattern) can let a shape-divergent table
-- survive CREATE TABLE IF NOT EXISTS — closed by codex pass 1 finding F5.
-----------------------------------------------
DO $$
DECLARE
    v_table_exists boolean;
    -- (column_name, data_type, is_nullable). is_nullable is 'YES'/'NO' to match
    -- information_schema.columns.
    v_expected RECORD;
    v_actual_type text;
    v_actual_nullable text;
    v_drift text[] := ARRAY[]::text[];
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema='public' AND table_name='agent_routing_logs'
    ) INTO v_table_exists;

    IF v_table_exists THEN
        FOR v_expected IN
            SELECT * FROM (VALUES
                ('id','uuid','NO'),
                ('project_id','uuid','YES'),
                ('task_id','uuid','YES'),
                ('spec_id','uuid','YES'),
                ('request_id','uuid','NO'),
                ('request_text','text','NO'),
                ('intent','text','NO'),
                ('confidence','numeric','NO'),
                ('routed_to','text','NO'),
                ('reason','text','YES'),
                ('phase_check','text','NO'),
                ('phase_blocker','text','YES'),
                ('agent_response','jsonb','YES'),
                ('llm_model','text','YES'),
                ('classification_latency_ms','integer','YES'),
                ('total_latency_ms','integer','YES'),
                ('outcome','text','NO'),
                ('error_code','text','YES'),
                ('error_message','text','YES'),
                ('idempotency_key','text','YES'),
                ('request_payload_hash','text','YES'),
                ('stored_response','jsonb','YES'),
                ('requested_by','text','YES'),
                ('session_id','uuid','YES'),
                ('notes','text','YES'),
                ('created_at','timestamp with time zone','NO'),
                ('updated_at','timestamp with time zone','NO')
            ) AS t(col, typ, nullable)
        LOOP
            SELECT data_type, is_nullable INTO v_actual_type, v_actual_nullable
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='agent_routing_logs'
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
                'agent_routing_logs exists with shape drift: %. Manual reconciliation required.',
                v_drift;
        END IF;
    END IF;
END $$;

-----------------------------------------------
-- 1. agent_routing_logs
-- One row per /webhook/agent classification + downstream dispatch attempt.
-- project_id NULLable because the router is the entry point — first-turn requests
-- may not yet be bound to a project.
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_routing_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES agent_projects(id) ON DELETE SET NULL,
    task_id UUID REFERENCES agent_tasks(id) ON DELETE SET NULL,
    spec_id UUID REFERENCES agent_specifications(id) ON DELETE SET NULL,
    request_id UUID NOT NULL DEFAULT gen_random_uuid(),
    request_text TEXT NOT NULL,
    intent TEXT NOT NULL
        CHECK (intent IN (
            'new_project',
            'status_query',
            'memory_operation',
            'architecture_request',
            'build_request',
            'verification_request',
            'unclassified'
        )),
    confidence NUMERIC(3,2) NOT NULL DEFAULT 0.00
        CHECK (confidence >= 0.00 AND confidence <= 1.00),
    routed_to TEXT NOT NULL
        CHECK (routed_to IN (
            'specification_agent',
            'architecture_agent',
            'builder_agent',
            'verification_agent',
            'project_manager_agent',
            'memory_agent',
            'router_self',
            'none'
        )),
    reason TEXT,
    phase_check TEXT NOT NULL DEFAULT 'passed'
        CHECK (phase_check IN ('passed','blocked')),
    phase_blocker TEXT,
    agent_response JSONB,
    llm_model TEXT,
    classification_latency_ms INT
        CHECK (classification_latency_ms IS NULL OR classification_latency_ms >= 0),
    total_latency_ms INT
        CHECK (total_latency_ms IS NULL OR total_latency_ms >= 0),
    outcome TEXT NOT NULL DEFAULT 'dispatched'
        CHECK (outcome IN ('dispatched','blocked','failed','noop')),
    error_code TEXT,
    error_message TEXT,
    idempotency_key TEXT,
    request_payload_hash TEXT,  -- sha256 hex of canonical request payload; used for
                                -- same-key/different-payload conflict detection (F8)
    stored_response JSONB,      -- response returned for the first insert under this
                                -- idempotency_key; replayed on safe-retry
    requested_by TEXT,
    session_id UUID REFERENCES agent_sessions(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT routing_request_text_nonempty CHECK (length(trim(request_text)) > 0),
    CONSTRAINT routing_request_text_not_too_large CHECK (length(request_text) <= 65536),
    CONSTRAINT routing_blocker_implies_blocked CHECK (
        (phase_check = 'blocked' AND phase_blocker IS NOT NULL AND length(trim(phase_blocker)) > 0)
        OR
        (phase_check = 'passed' AND phase_blocker IS NULL)
    ),
    -- Bidirectional: failed iff error_code present; otherwise error fields MUST be null.
    -- Hardened by codex pass 1 finding F12.
    CONSTRAINT routing_error_fields_iff_failed CHECK (
        (outcome = 'failed' AND error_code IS NOT NULL AND length(trim(error_code)) > 0)
        OR
        (outcome <> 'failed' AND error_code IS NULL AND error_message IS NULL)
    ),
    -- Idempotency triple consistency: key, hash, response are all-or-nothing.
    -- Hash MUST be sha256 hex (64 chars). Hardened by codex pass 1 finding F8.
    CONSTRAINT routing_idem_triple_consistent CHECK (
        (idempotency_key IS NULL AND request_payload_hash IS NULL AND stored_response IS NULL)
        OR
        (idempotency_key IS NOT NULL AND length(trim(idempotency_key)) > 0
         AND request_payload_hash IS NOT NULL AND length(request_payload_hash) = 64
         AND stored_response IS NOT NULL)
    ),
    CONSTRAINT routing_unclassified_is_noop CHECK (
        (intent = 'unclassified' AND routed_to IN ('router_self','none') AND outcome IN ('noop','failed','blocked'))
        OR
        (intent <> 'unclassified')
    )
);

-- Idempotency uniqueness — global on idempotency_key (callers should prefix with
-- request scope to avoid cross-context replay, per AR-V3 pattern in verification).
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_routing_logs_idempotency
    ON agent_routing_logs (idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_project ON agent_routing_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_task ON agent_routing_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_intent ON agent_routing_logs(intent);
CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_routed_to ON agent_routing_logs(routed_to);
CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_outcome ON agent_routing_logs(outcome);
CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_created ON agent_routing_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_request ON agent_routing_logs(request_id);
CREATE INDEX IF NOT EXISTS idx_agent_routing_logs_session ON agent_routing_logs(session_id);

-----------------------------------------------
-- 2. updated_at trigger — no-op-safe
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_agent_routing_logs_updated_at()
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

DROP TRIGGER IF EXISTS trg_agent_routing_logs_updated ON agent_routing_logs;
CREATE TRIGGER trg_agent_routing_logs_updated
    BEFORE UPDATE ON agent_routing_logs
    FOR EACH ROW EXECUTE FUNCTION update_agent_routing_logs_updated_at();

-----------------------------------------------
-- 3. RLS — service_role only
-----------------------------------------------
ALTER TABLE agent_routing_logs ENABLE ROW LEVEL SECURITY;

DO $$
DECLARE r record;
BEGIN
    FOR r IN
        SELECT polname FROM pg_policy WHERE polrelid = 'public.agent_routing_logs'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.agent_routing_logs', r.polname);
    END LOOP;
END $$;

CREATE POLICY "service_role_full" ON agent_routing_logs
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-----------------------------------------------
-- 4. RPC: record_routing_decision
-- Inserts a routing-log row. Validates project/task/spec lineage when supplied.
-- Idempotency-safe with payload-hash conflict detection (closes codex pass 1 F8):
--   - Same key + same payload hash → stored_response replayed.
--   - Same key + different payload hash → {error:'idempotency_conflict'}.
-- p_request_payload_hash and p_stored_response are REQUIRED whenever
-- p_idempotency_key is supplied (matches the triple-consistency CHECK on the table).
-----------------------------------------------
CREATE OR REPLACE FUNCTION record_routing_decision(
    p_project_id UUID,
    p_task_id UUID,
    p_spec_id UUID,
    p_request_id UUID,
    p_request_text TEXT,
    p_intent TEXT,
    p_confidence NUMERIC,
    p_routed_to TEXT,
    p_reason TEXT,
    p_phase_check TEXT,
    p_phase_blocker TEXT,
    p_agent_response JSONB,
    p_llm_model TEXT,
    p_classification_latency_ms INT,
    p_total_latency_ms INT,
    p_outcome TEXT,
    p_error_code TEXT,
    p_error_message TEXT,
    p_idempotency_key TEXT,
    p_request_payload_hash TEXT,
    p_stored_response JSONB,
    p_requested_by TEXT,
    p_session_id UUID,
    p_notes TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_new_id UUID;
    v_existing_row agent_routing_logs%ROWTYPE;
    v_existing_row_json JSONB;
    v_task_project_id UUID;
    v_spec_project_id UUID;
    v_allowed_intents TEXT[] := ARRAY['new_project','status_query','memory_operation',
        'architecture_request','build_request','verification_request','unclassified'];
    v_allowed_routes TEXT[] := ARRAY['specification_agent','architecture_agent',
        'builder_agent','verification_agent','project_manager_agent','memory_agent',
        'router_self','none'];
    v_allowed_outcomes TEXT[] := ARRAY['dispatched','blocked','failed','noop'];
    v_allowed_phase TEXT[] := ARRAY['passed','blocked'];
BEGIN
    -- Argument validation.
    IF NOT (COALESCE(p_intent,'unclassified') = ANY (v_allowed_intents)) THEN
        RETURN jsonb_build_object('error', 'invalid_intent', 'detail', p_intent);
    END IF;
    IF NOT (COALESCE(p_routed_to,'none') = ANY (v_allowed_routes)) THEN
        RETURN jsonb_build_object('error', 'invalid_routed_to', 'detail', p_routed_to);
    END IF;
    IF NOT (COALESCE(p_outcome,'dispatched') = ANY (v_allowed_outcomes)) THEN
        RETURN jsonb_build_object('error', 'invalid_outcome', 'detail', p_outcome);
    END IF;
    IF NOT (COALESCE(p_phase_check,'passed') = ANY (v_allowed_phase)) THEN
        RETURN jsonb_build_object('error', 'invalid_phase_check', 'detail', p_phase_check);
    END IF;
    IF p_confidence IS NOT NULL AND (p_confidence < 0 OR p_confidence > 1) THEN
        RETURN jsonb_build_object('error', 'invalid_confidence', 'detail', p_confidence::text);
    END IF;
    IF p_request_text IS NULL OR length(trim(p_request_text)) = 0 THEN
        RETURN jsonb_build_object('error', 'request_text_required');
    END IF;
    -- Idempotency-triple parameter validation. Must be all-or-nothing.
    IF p_idempotency_key IS NOT NULL THEN
        IF p_request_payload_hash IS NULL OR length(p_request_payload_hash) <> 64 THEN
            RETURN jsonb_build_object('error', 'invalid_payload_hash');
        END IF;
        IF p_stored_response IS NULL THEN
            RETURN jsonb_build_object('error', 'stored_response_required');
        END IF;
    END IF;

    -- Idempotency replay/conflict fast-path.
    IF p_idempotency_key IS NOT NULL THEN
        SELECT * INTO v_existing_row
        FROM agent_routing_logs r
        WHERE r.idempotency_key = p_idempotency_key
        LIMIT 1;
        IF v_existing_row.id IS NOT NULL THEN
            IF v_existing_row.request_payload_hash = p_request_payload_hash THEN
                RETURN jsonb_build_object(
                    'replayed', true,
                    'routing_log_id', v_existing_row.id,
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

    -- Cross-row lineage validation (when supplied). FOR SHARE pins the parent row
    -- so a concurrent admin path cannot move it to a different project between
    -- validation and our INSERT (closes codex pass 4 router TOCTOU finding).
    IF p_task_id IS NOT NULL THEN
        SELECT project_id INTO v_task_project_id FROM agent_tasks WHERE id = p_task_id FOR SHARE;
        IF v_task_project_id IS NULL THEN
            RETURN jsonb_build_object('error', 'task_not_found');
        END IF;
        IF p_project_id IS NOT NULL AND v_task_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'task_project_mismatch');
        END IF;
    END IF;
    IF p_spec_id IS NOT NULL THEN
        SELECT project_id INTO v_spec_project_id FROM agent_specifications WHERE id = p_spec_id FOR SHARE;
        IF v_spec_project_id IS NULL THEN
            RETURN jsonb_build_object('error', 'spec_not_found');
        END IF;
        IF p_project_id IS NOT NULL AND v_spec_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'spec_project_mismatch');
        END IF;
    END IF;

    BEGIN
        INSERT INTO agent_routing_logs (
            project_id, task_id, spec_id, request_id, request_text,
            intent, confidence, routed_to, reason,
            phase_check, phase_blocker, agent_response, llm_model,
            classification_latency_ms, total_latency_ms,
            outcome, error_code, error_message,
            idempotency_key, request_payload_hash, stored_response,
            requested_by, session_id, notes
        ) VALUES (
            p_project_id, p_task_id, p_spec_id,
            COALESCE(p_request_id, gen_random_uuid()),
            p_request_text,
            COALESCE(p_intent, 'unclassified'),
            COALESCE(p_confidence, 0.00),
            COALESCE(p_routed_to, 'none'),
            p_reason,
            COALESCE(p_phase_check, 'passed'),
            p_phase_blocker,
            p_agent_response,
            p_llm_model,
            p_classification_latency_ms,
            p_total_latency_ms,
            COALESCE(p_outcome, 'dispatched'),
            p_error_code,
            p_error_message,
            p_idempotency_key,
            p_request_payload_hash,
            p_stored_response,
            p_requested_by,
            p_session_id,
            p_notes
        )
        RETURNING id INTO v_new_id;
    EXCEPTION WHEN unique_violation THEN
        IF SQLERRM ILIKE '%uq_agent_routing_logs_idempotency%'
           AND p_idempotency_key IS NOT NULL THEN
            -- Concurrent insert won — reconcile with hash check.
            SELECT * INTO v_existing_row
            FROM agent_routing_logs r
            WHERE r.idempotency_key = p_idempotency_key
            LIMIT 1;
            IF v_existing_row.id IS NOT NULL THEN
                IF v_existing_row.request_payload_hash = p_request_payload_hash THEN
                    RETURN jsonb_build_object(
                        'replayed', true,
                        'routing_log_id', v_existing_row.id,
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
        RETURN jsonb_build_object('error', 'unique_violation', 'detail', SQLERRM);
    END;

    RETURN jsonb_build_object('replayed', false,
        'routing_log', (SELECT row_to_json(r)::jsonb FROM agent_routing_logs r WHERE r.id = v_new_id));
END;
$$;

-----------------------------------------------
-- 5. Grants — least privilege
-----------------------------------------------
REVOKE ALL ON FUNCTION record_routing_decision(
    UUID,UUID,UUID,UUID,TEXT,TEXT,NUMERIC,TEXT,TEXT,TEXT,TEXT,JSONB,TEXT,
    INT,INT,TEXT,TEXT,TEXT,TEXT,TEXT,JSONB,TEXT,UUID,TEXT
) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION record_routing_decision(
    UUID,UUID,UUID,UUID,TEXT,TEXT,NUMERIC,TEXT,TEXT,TEXT,TEXT,JSONB,TEXT,
    INT,INT,TEXT,TEXT,TEXT,TEXT,TEXT,JSONB,TEXT,UUID,TEXT
) TO service_role;

-----------------------------------------------
-- 6. Accepted-risk register
-----------------------------------------------
COMMENT ON TABLE agent_routing_logs IS
    'Router Agent canonical store. Accepted residual risks:
     • AR-R1: project_id is NULLable because the router is the system entry point — first-turn requests may have no project context yet. Cross-row validation kicks in only when project_id is supplied alongside task_id/spec_id.
     • AR-R2: agent_response stored as JSONB without size cap. Callers SHOULD truncate downstream responses above ~100KB before logging; future versions may add a length CHECK if abuse appears.
     • AR-R3: idempotency_key is globally unique, not project-scoped. Callers should prefix keys with request scope (route-{request_id}) to avoid cross-context replay. Same-key/different-payload conflicts return idempotency_conflict (see request_payload_hash + stored_response).
     • AR-R4: LAN-only HTTP transport for the /webhook/agent endpoint; token + firewall are the compensating control until HTTPS migration.';

COMMENT ON FUNCTION record_routing_decision(
    UUID,UUID,UUID,UUID,TEXT,TEXT,NUMERIC,TEXT,TEXT,TEXT,TEXT,JSONB,TEXT,
    INT,INT,TEXT,TEXT,TEXT,TEXT,TEXT,JSONB,TEXT,UUID,TEXT
) IS
    'Records a routing decision row with full classification + dispatch context. Idempotency-safe via (idempotency_key, request_payload_hash, stored_response): same key + same hash → stored_response replayed; same key + different hash → idempotency_conflict. Validates project/task/spec lineage when supplied.';
