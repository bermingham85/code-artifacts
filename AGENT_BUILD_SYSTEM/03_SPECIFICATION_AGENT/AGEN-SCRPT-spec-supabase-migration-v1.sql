-- AGEN-SCRPT-spec-supabase-migration-v1.sql
-- Specification Agent — Supabase schema
-- Date: 2026-05-05 (round 2 — adversarial review pass 1 closed)
-- Run on: Supabase project ylcepmvbjjnwmzvevxid
--
-- Pre-conditions verified by audit (2026-05-05):
--   - agent_projects exists, used as foreign-key target
--   - agent_tasks exists, used as foreign-key target
--   - agent_specifications does NOT exist (creating)
--
-- Idempotency strategy: every CREATE uses IF NOT EXISTS; every trigger DROP/CREATEs;
-- every policy is dropped before recreation. The migration is safe to run twice.
-- HOWEVER: it does NOT reconcile a pre-existing table with a different shape — operators
-- must verify the table is absent (audit step) before applying. A guard at the top
-- raises if the table already exists with a different column set, to fail fast.

-----------------------------------------------
-- 0. Pre-flight guard — verify ALL expected columns when table exists
-----------------------------------------------
DO $$
DECLARE
    v_table_exists boolean;
    v_expected text[] := ARRAY[
        'id','project_id','task_id','title','summary','body_markdown',
        'requirements','acceptance_criteria','constraints','dependencies',
        'non_goals','open_questions','notes','status','version',
        'parent_spec_id','root_spec_id','idempotency_key','approved_by','approved_at',
        'created_at','updated_at'
    ];
    v_missing text[];
BEGIN
    SELECT EXISTS (SELECT 1 FROM information_schema.tables
        WHERE table_schema='public' AND table_name='agent_specifications')
        INTO v_table_exists;

    IF v_table_exists THEN
        SELECT array_agg(c) INTO v_missing
        FROM unnest(v_expected) c
        WHERE NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema='public' AND table_name='agent_specifications'
              AND column_name = c
        );
        IF v_missing IS NOT NULL AND array_length(v_missing, 1) > 0 THEN
            RAISE EXCEPTION 'agent_specifications already exists but is missing expected columns: %. Manual reconciliation required.', v_missing;
        END IF;
    END IF;

    -- Drop the legacy upsert_specification if any prior migration created it.
    -- The replacement is create_specification_revision (different name, different signature).
    PERFORM 1 FROM pg_proc WHERE proname = 'upsert_specification';
    IF FOUND THEN
        EXECUTE 'DROP FUNCTION IF EXISTS upsert_specification(UUID,UUID,TEXT,TEXT,TEXT,JSONB,JSONB,JSONB,JSONB,TEXT,JSONB,TEXT,UUID)';
    END IF;
END $$;

-----------------------------------------------
-- 1. agent_specifications
-- Notes:
--   - non_goals stored as JSONB array (was TEXT in v0; aligns with other list fields)
--   - status enum extended with 'blocked' to match agent prompt failure modes
--   - root_spec_id introduced for stable lineage queries (avoids the v0 ambiguity where
--     independent root specs all start at version 1)
--   - composite UNIQUE on (root_spec_id, version) prevents revision-race duplicates
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_specifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES agent_projects(id) ON DELETE RESTRICT,
    task_id UUID REFERENCES agent_tasks(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    summary TEXT,
    body_markdown TEXT NOT NULL,
    requirements JSONB NOT NULL DEFAULT '[]'::jsonb,
    acceptance_criteria JSONB NOT NULL DEFAULT '[]'::jsonb,
    constraints JSONB NOT NULL DEFAULT '[]'::jsonb,
    dependencies JSONB NOT NULL DEFAULT '[]'::jsonb,
    non_goals JSONB NOT NULL DEFAULT '[]'::jsonb,
    open_questions JSONB NOT NULL DEFAULT '[]'::jsonb,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft','needs_clarification','reviewed','approved','superseded','blocked')),
    version INT NOT NULL DEFAULT 1,
    parent_spec_id UUID REFERENCES agent_specifications(id) ON DELETE SET NULL,
    root_spec_id UUID REFERENCES agent_specifications(id) ON DELETE SET NULL,
    idempotency_key TEXT,
    approved_by TEXT,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT spec_version_positive CHECK (version >= 1),
    CONSTRAINT spec_no_self_parent CHECK (id <> parent_spec_id),
    CONSTRAINT spec_requirements_is_array CHECK (jsonb_typeof(requirements) = 'array'),
    CONSTRAINT spec_acceptance_is_array  CHECK (jsonb_typeof(acceptance_criteria) = 'array'),
    CONSTRAINT spec_constraints_is_array CHECK (jsonb_typeof(constraints) = 'array'),
    CONSTRAINT spec_dependencies_is_array CHECK (jsonb_typeof(dependencies) = 'array'),
    CONSTRAINT spec_non_goals_is_array   CHECK (jsonb_typeof(non_goals) = 'array'),
    CONSTRAINT spec_open_questions_is_array CHECK (jsonb_typeof(open_questions) = 'array'),
    -- Approval audit invariants: when status is 'approved', approver fields MUST be set.
    -- Once set, they are sticky — they remain on the row when status transitions to 'superseded'
    -- so we retain the historical "this row was approved by X at T". Non-approval statuses
    -- that were never approved have NULL approver fields.
    CONSTRAINT spec_approval_audit_consistent CHECK (
        (status = 'approved'   AND approved_by IS NOT NULL AND length(trim(approved_by)) > 0 AND approved_at IS NOT NULL)
        OR
        (status = 'superseded' AND ((approved_by IS NULL AND approved_at IS NULL) OR (approved_by IS NOT NULL AND approved_at IS NOT NULL)))
        OR
        (status NOT IN ('approved','superseded') AND approved_by IS NULL AND approved_at IS NULL)
    ),
    -- Title and body must be non-empty after trimming.
    CONSTRAINT spec_title_nonempty CHECK (length(trim(title)) > 0),
    CONSTRAINT spec_body_nonempty CHECK (length(trim(body_markdown)) > 0)
);

-- Lineage uniqueness: at most one row per (root_spec_id, version) — prevents revision races.
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_specifications_root_version
    ON agent_specifications (root_spec_id, version)
    WHERE root_spec_id IS NOT NULL;

-- Idempotency uniqueness: same key replays the same spec.
CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_specifications_idempotency
    ON agent_specifications (idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_agent_specifications_project ON agent_specifications(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_specifications_task ON agent_specifications(task_id);
CREATE INDEX IF NOT EXISTS idx_agent_specifications_status ON agent_specifications(status);
CREATE INDEX IF NOT EXISTS idx_agent_specifications_root ON agent_specifications(root_spec_id);
CREATE INDEX IF NOT EXISTS idx_agent_specifications_parent ON agent_specifications(parent_spec_id);

-- GIN indexes deliberately omitted in v1: payloads are small, write-mostly, and querying
-- by JSONB content is not required by current call paths. Add later if needed.

-----------------------------------------------
-- 2. updated_at trigger — only fires when meaningful columns change
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_agent_specifications_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
    -- Skip no-op updates so audit signals stay clean.
    IF (NEW.* IS DISTINCT FROM OLD.*) THEN
        NEW.updated_at = now();
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_agent_specifications_updated ON agent_specifications;
CREATE TRIGGER trg_agent_specifications_updated
    BEFORE UPDATE ON agent_specifications
    FOR EACH ROW EXECUTE FUNCTION update_agent_specifications_updated_at();

-----------------------------------------------
-- 3. RLS — service_role only.
-- Authenticated reads removed in v1: there is no per-project access model yet,
-- so blanket-read would expose all specs to all logged-in users. Reads currently
-- go through the n8n workflow (server-side) which uses service_role.
-- When per-project authorization is built (Router/PM Agent work), an authenticated
-- read policy can be re-added with project membership checks.
-----------------------------------------------
ALTER TABLE agent_specifications ENABLE ROW LEVEL SECURITY;

-- Drop EVERY pre-existing policy. We re-create only service_role_full.
-- Using a DO block so that policies created by older migrations under different
-- names are also removed.
DO $$
DECLARE r record;
BEGIN
    FOR r IN
        SELECT polname FROM pg_policy WHERE polrelid = 'public.agent_specifications'::regclass
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.agent_specifications', r.polname);
    END LOOP;
END $$;

CREATE POLICY "service_role_full" ON agent_specifications
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-----------------------------------------------
-- 4. Helper: create_specification_revision
-- (renamed from upsert_specification — it always inserts a new row;
-- "upsert" was misleading. Idempotency now lives in idempotency_key uniqueness.)
--
-- Returns the inserted row as JSONB, OR the pre-existing row if idempotency_key matches.
-- Concurrency-safe: locks the parent row FOR UPDATE before computing the next version.
-- Lineage-safe: validates parent project/task match before inserting.
-----------------------------------------------
CREATE OR REPLACE FUNCTION create_specification_revision(
    p_project_id UUID,
    p_task_id UUID,
    p_title TEXT,
    p_summary TEXT,
    p_body_markdown TEXT,
    p_requirements JSONB,
    p_acceptance_criteria JSONB,
    p_constraints JSONB,
    p_dependencies JSONB,
    p_non_goals JSONB,
    p_open_questions JSONB,
    p_notes TEXT,
    p_status TEXT,
    p_parent_spec_id UUID,
    p_idempotency_key TEXT,
    p_approved_by TEXT DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_new_id UUID;
    v_version INT := 1;
    v_root_spec_id UUID;
    v_existing_row JSONB;
    v_parent_project_id UUID;
    v_parent_task_id UUID;
    v_task_project_id UUID;
    v_allowed_status TEXT[] := ARRAY['draft','needs_clarification','reviewed','approved','blocked'];
    v_now TIMESTAMPTZ := now();
BEGIN
    -- Disallow inserting rows already in terminal lineage states (superseded must come
    -- via the parent supersede update below; not as an initial INSERT status).
    IF NOT (COALESCE(p_status, 'draft') = ANY (v_allowed_status)) THEN
        RETURN jsonb_build_object('error', 'invalid_status', 'detail', p_status);
    END IF;

    -- Approval audit: status='approved' requires p_approved_by. Otherwise refuse to write.
    IF COALESCE(p_status,'draft') = 'approved' AND (p_approved_by IS NULL OR length(trim(p_approved_by)) = 0) THEN
        RETURN jsonb_build_object('error', 'approver_required_for_approved');
    END IF;

    -- task_id must belong to the project_id.
    IF p_task_id IS NOT NULL THEN
        SELECT project_id INTO v_task_project_id FROM agent_tasks WHERE id = p_task_id;
        IF v_task_project_id IS NULL THEN
            RETURN jsonb_build_object('error', 'task_not_found');
        END IF;
        IF v_task_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'task_project_mismatch');
        END IF;
    END IF;

    -- Idempotency replay: scoped uniqueness lives on (idempotency_key) globally; any caller
    -- using a duplicate key gets the existing row back. Race-safe via unique index +
    -- INSERT … ON CONFLICT below; this fast-path lookup avoids the work when a hit exists.
    IF p_idempotency_key IS NOT NULL THEN
        SELECT row_to_json(s)::jsonb INTO v_existing_row
        FROM agent_specifications s
        WHERE s.idempotency_key = p_idempotency_key
        LIMIT 1;
        IF v_existing_row IS NOT NULL THEN
            RETURN jsonb_build_object('replayed', true, 'spec', v_existing_row);
        END IF;
    END IF;

    IF p_parent_spec_id IS NOT NULL THEN
        -- Lock the parent row first to serialize concurrent revisions.
        SELECT version, root_spec_id, project_id, task_id
          INTO v_version, v_root_spec_id, v_parent_project_id, v_parent_task_id
        FROM agent_specifications
        WHERE id = p_parent_spec_id
        FOR UPDATE;

        IF v_version IS NULL THEN
            RETURN jsonb_build_object('error', 'parent_not_found');
        END IF;

        IF v_parent_project_id <> p_project_id THEN
            RETURN jsonb_build_object('error', 'parent_project_mismatch');
        END IF;

        -- Tighter task-lineage check: NULL on either side is a mismatch (not "skip").
        IF v_parent_task_id IS DISTINCT FROM p_task_id THEN
            RETURN jsonb_build_object('error', 'parent_task_mismatch');
        END IF;

        -- Inherit root_spec_id; if parent had none, parent itself is the root.
        IF v_root_spec_id IS NULL THEN
            v_root_spec_id := p_parent_spec_id;
            UPDATE agent_specifications SET root_spec_id = p_parent_spec_id
            WHERE id = p_parent_spec_id;
        END IF;

        -- Compute next version from the lineage MAX, not parent.version+1, so that
        -- branching from older parents doesn't collide with later linear versions.
        SELECT COALESCE(MAX(version), 0) + 1 INTO v_version
        FROM agent_specifications
        WHERE root_spec_id = v_root_spec_id OR id = v_root_spec_id;

        -- Note on approved-parent revisions: a reviewed child of an approved parent IS allowed
        -- to land. The approved parent stays approved (sticky); supersede only happens when
        -- the PM Agent later calls approve_specification(child) — see RPC #6. This means there
        -- can briefly be both an approved parent AND a reviewed child in the lineage; that is
        -- the documented "in flight, not yet promoted" state. Architecture/Builder must consume
        -- the approved row (not the reviewed child) until PM approves the child.
        NULL;
    END IF;

    -- Race-safe insert with idempotency conflict resolution.
    -- The parent supersede happens AFTER successful insert (so a failed insert leaves
    -- the parent untouched).
    BEGIN
        INSERT INTO agent_specifications (
            project_id, task_id, title, summary, body_markdown,
            requirements, acceptance_criteria, constraints, dependencies,
            non_goals, open_questions, notes, status, version,
            parent_spec_id, root_spec_id, idempotency_key,
            approved_by, approved_at
        ) VALUES (
            p_project_id, p_task_id, p_title, p_summary, p_body_markdown,
            COALESCE(p_requirements, '[]'::jsonb),
            COALESCE(p_acceptance_criteria, '[]'::jsonb),
            COALESCE(p_constraints, '[]'::jsonb),
            COALESCE(p_dependencies, '[]'::jsonb),
            COALESCE(p_non_goals, '[]'::jsonb),
            COALESCE(p_open_questions, '[]'::jsonb),
            p_notes,
            COALESCE(p_status, 'draft'),
            v_version,
            p_parent_spec_id,
            v_root_spec_id,
            p_idempotency_key,
            CASE WHEN COALESCE(p_status,'draft') = 'approved' THEN p_approved_by ELSE NULL END,
            CASE WHEN COALESCE(p_status,'draft') = 'approved' THEN v_now ELSE NULL END
        )
        RETURNING id INTO v_new_id;
    EXCEPTION WHEN unique_violation THEN
        -- Distinguish idempotency-key collision (returnable replay) from other unique
        -- violations (lineage version race, etc.) by checking the constraint name.
        IF SQLERRM ILIKE '%uq_agent_specifications_idempotency%'
           AND p_idempotency_key IS NOT NULL THEN
            SELECT row_to_json(s)::jsonb INTO v_existing_row
            FROM agent_specifications s
            WHERE s.idempotency_key = p_idempotency_key
            LIMIT 1;
            IF v_existing_row IS NOT NULL THEN
                RETURN jsonb_build_object('replayed', true, 'spec', v_existing_row);
            END IF;
        END IF;
        IF SQLERRM ILIKE '%uq_agent_specifications_root_version%' THEN
            RETURN jsonb_build_object('error', 'lineage_version_race', 'detail', 'concurrent revision collision; retry');
        END IF;
        RETURN jsonb_build_object('error', 'unique_violation', 'detail', SQLERRM);
    END;

    -- Self-rooted: a fresh revision lineage roots at itself.
    IF v_root_spec_id IS NULL THEN
        UPDATE agent_specifications SET root_spec_id = id WHERE id = v_new_id;
    END IF;

    -- Parent supersede policy after successful insert:
    --   reviewed child → supersedes a REVIEWED parent (linear refinement).
    --                    DOES NOT supersede an APPROVED parent — approved is sticky until PM
    --                    explicitly approves the child via approve_specification (which then
    --                    cascades the supersede). Multiple non-superseded specs can briefly
    --                    coexist in this case; downstream agents must consume the approved row.
    --   approved child  → supersedes ANY non-superseded parent (approved or reviewed).
    IF p_parent_spec_id IS NOT NULL THEN
        IF p_status = 'approved' THEN
            UPDATE agent_specifications SET status = 'superseded'
            WHERE id = p_parent_spec_id AND status IN ('reviewed','approved');
        ELSIF p_status = 'reviewed' THEN
            UPDATE agent_specifications SET status = 'superseded'
            WHERE id = p_parent_spec_id AND status = 'reviewed';
        END IF;
    END IF;

    RETURN jsonb_build_object('replayed', false,
        'spec', (SELECT row_to_json(s)::jsonb FROM agent_specifications s WHERE s.id = v_new_id));
END;
$$;

-----------------------------------------------
-- 5. Helper: get_latest_specification
-- Resolves the highest-version non-superseded spec in a lineage.
-- Filter rules:
--   - status IN ('reviewed','approved')      → if any exists in the lineage, return the highest
--   - else status = 'needs_clarification'    → return the most recent
--   - else                                    → NULL
-- Scope: by (project_id, optional task_id, optional root_spec_id).
-----------------------------------------------
CREATE OR REPLACE FUNCTION get_latest_specification(
    p_project_id UUID,
    p_task_id UUID DEFAULT NULL,
    p_root_spec_id UUID DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_row agent_specifications%ROWTYPE;
BEGIN
    -- Reviewed/approved first.
    SELECT * INTO v_row
    FROM agent_specifications s
    WHERE s.project_id = p_project_id
      AND (p_task_id IS NULL OR s.task_id = p_task_id)
      AND (p_root_spec_id IS NULL OR s.root_spec_id = p_root_spec_id)
      AND s.status IN ('reviewed','approved')
    ORDER BY s.version DESC, s.created_at DESC
    LIMIT 1;

    IF v_row.id IS NOT NULL THEN
        RETURN row_to_json(v_row)::jsonb;
    END IF;

    -- Fall back to most recent clarification round.
    SELECT * INTO v_row
    FROM agent_specifications s
    WHERE s.project_id = p_project_id
      AND (p_task_id IS NULL OR s.task_id = p_task_id)
      AND (p_root_spec_id IS NULL OR s.root_spec_id = p_root_spec_id)
      AND s.status = 'needs_clarification'
    ORDER BY s.created_at DESC
    LIMIT 1;

    IF v_row.id IS NOT NULL THEN
        RETURN row_to_json(v_row)::jsonb;
    END IF;

    RETURN NULL;
END;
$$;

-----------------------------------------------
-- 6. Helper: approve_specification
-- Lifts a reviewed spec to approved. Records approver and timestamp.
-- This RPC is owned by the PM Agent contractually, but the function lives here
-- so that the schema knows about approval state transitions.
-----------------------------------------------
CREATE OR REPLACE FUNCTION approve_specification(
    p_spec_id UUID,
    p_approver TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_status TEXT;
    v_root UUID;
    v_version INT;
    v_newer_count INT;
BEGIN
    IF p_approver IS NULL OR length(trim(p_approver)) = 0 THEN
        RETURN jsonb_build_object('error', 'approver_required');
    END IF;

    SELECT status, root_spec_id, version
      INTO v_status, v_root, v_version
    FROM agent_specifications WHERE id = p_spec_id FOR UPDATE;

    IF v_status IS NULL THEN
        RETURN jsonb_build_object('error', 'spec_not_found');
    END IF;
    IF v_status <> 'reviewed' THEN
        RETURN jsonb_build_object('error', 'not_in_reviewed_state', 'current_status', v_status);
    END IF;

    -- Reject approval if a newer reviewed/approved spec exists in the same lineage.
    SELECT count(*)::int INTO v_newer_count
    FROM agent_specifications
    WHERE (root_spec_id = v_root OR id = v_root)
      AND id <> p_spec_id
      AND status IN ('reviewed','approved')
      AND version > v_version;
    IF v_newer_count > 0 THEN
        RETURN jsonb_build_object('error', 'newer_revision_exists',
            'detail', 'a higher-version reviewed/approved revision exists in this lineage');
    END IF;

    UPDATE agent_specifications
    SET status = 'approved',
        approved_by = trim(p_approver),
        approved_at = now()
    WHERE id = p_spec_id;

    -- Supersede the immediate parent if it was reviewed/approved — the new approval
    -- is now the canonical lineage head. Defensive guard `p.id <> p_spec_id` ensures
    -- the just-approved child is never targeted (also implied by the spec_no_self_parent
    -- CHECK constraint, but explicit here for clarity).
    UPDATE agent_specifications p
    SET status = 'superseded'
    FROM agent_specifications c
    WHERE c.id = p_spec_id
      AND p.id = c.parent_spec_id
      AND p.id <> p_spec_id
      AND p.status IN ('reviewed','approved');

    RETURN (SELECT row_to_json(s)::jsonb FROM agent_specifications s WHERE s.id = p_spec_id);
END;
$$;

-----------------------------------------------
-- 7. Grants — least privilege
-- Only service_role may execute these RPCs. The n8n workflow uses the
-- "Postgres - Agent System" credential which connects as a Supabase service role
-- via direct Postgres. anon and authenticated are explicitly denied.
-----------------------------------------------
REVOKE ALL ON FUNCTION create_specification_revision(UUID,UUID,TEXT,TEXT,TEXT,JSONB,JSONB,JSONB,JSONB,JSONB,JSONB,TEXT,TEXT,UUID,TEXT,TEXT) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION get_latest_specification(UUID,UUID,UUID)             FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION approve_specification(UUID,TEXT)                     FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION create_specification_revision(UUID,UUID,TEXT,TEXT,TEXT,JSONB,JSONB,JSONB,JSONB,JSONB,JSONB,TEXT,TEXT,UUID,TEXT,TEXT) TO service_role;
GRANT EXECUTE ON FUNCTION get_latest_specification(UUID,UUID,UUID) TO service_role;
GRANT EXECUTE ON FUNCTION approve_specification(UUID,TEXT) TO service_role;

-----------------------------------------------
-- 8. Accepted-risk register (documentation, not enforced)
-----------------------------------------------
COMMENT ON TABLE agent_specifications IS
    'Specification Agent canonical store. Accepted residual risks (tracked in AGEN-SPEC-spec-integration-v1.md):
     • LAN-only HTTP transport — token + firewall is the compensating control until HTTPS migration (TM-1).
     • No per-project authorization yet — service_role-only RLS is the compensating control (F7).
     • parent_spec_id ON DELETE SET NULL preserves children when ancestor is administratively removed; lineage is reconstructible via root_spec_id.
     • Lineage integrity for direct service_role writes is enforced only inside create_specification_revision; ad-hoc INSERT/UPDATE bypasses validation by design (operators).';
