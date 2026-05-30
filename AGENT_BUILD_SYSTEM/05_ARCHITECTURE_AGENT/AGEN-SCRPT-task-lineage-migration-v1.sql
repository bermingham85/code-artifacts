-- AGEN task-lineage migration v1 - LOCAL DRAFT ONLY
--
-- Purpose:
--   Add future-only task lineage from agent_tasks to agent_architectures.tasks[*].
--
-- Production boundary:
--   - Do not run until backup/export evidence and operator approval exist.
--   - Existing rows remain valid with NULL lineage.
--   - No heuristic backfill is performed.
--   - JESS is protected by policy and is not valid migration test material.

BEGIN;

DO $$
DECLARE
    v_missing TEXT[];
BEGIN
    SELECT array_agg(table_name::text ORDER BY table_name)
    INTO v_missing
    FROM (
        VALUES
            ('agent_projects'),
            ('agent_tasks'),
            ('agent_architectures'),
            ('agent_task_dependencies')
    ) AS required(table_name)
    WHERE NOT EXISTS (
        SELECT 1
        FROM information_schema.tables t
        WHERE t.table_schema = 'public'
          AND t.table_name = required.table_name
    );

    IF v_missing IS NOT NULL THEN
        RAISE EXCEPTION 'Missing required table(s): %', array_to_string(v_missing, ', ');
    END IF;
END $$;

ALTER TABLE agent_tasks
    ADD COLUMN IF NOT EXISTS architecture_id UUID
        REFERENCES agent_architectures(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS decomposition_task_id UUID,
    ADD COLUMN IF NOT EXISTS inputs JSONB,
    ADD COLUMN IF NOT EXISTS outputs JSONB,
    ADD COLUMN IF NOT EXISTS dependencies JSONB,
    ADD COLUMN IF NOT EXISTS component TEXT,
    ADD COLUMN IF NOT EXISTS estimated_hours NUMERIC;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_agent_tasks_inputs_is_array'
          AND conrelid = 'public.agent_tasks'::regclass
    ) THEN
        ALTER TABLE agent_tasks
            ADD CONSTRAINT chk_agent_tasks_inputs_is_array
            CHECK (inputs IS NULL OR jsonb_typeof(inputs) = 'array');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_agent_tasks_outputs_is_array'
          AND conrelid = 'public.agent_tasks'::regclass
    ) THEN
        ALTER TABLE agent_tasks
            ADD CONSTRAINT chk_agent_tasks_outputs_is_array
            CHECK (outputs IS NULL OR jsonb_typeof(outputs) = 'array');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_agent_tasks_dependencies_is_array'
          AND conrelid = 'public.agent_tasks'::regclass
    ) THEN
        ALTER TABLE agent_tasks
            ADD CONSTRAINT chk_agent_tasks_dependencies_is_array
            CHECK (dependencies IS NULL OR jsonb_typeof(dependencies) = 'array');
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'chk_agent_tasks_estimated_hours_nonnegative'
          AND conrelid = 'public.agent_tasks'::regclass
    ) THEN
        ALTER TABLE agent_tasks
            ADD CONSTRAINT chk_agent_tasks_estimated_hours_nonnegative
            CHECK (estimated_hours IS NULL OR estimated_hours >= 0);
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_agent_tasks_architecture
    ON agent_tasks(architecture_id)
    WHERE architecture_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_agent_tasks_decomposition_task
    ON agent_tasks(decomposition_task_id)
    WHERE decomposition_task_id IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_agent_tasks_arch_decomp
    ON agent_tasks(architecture_id, decomposition_task_id)
    WHERE architecture_id IS NOT NULL AND decomposition_task_id IS NOT NULL;

CREATE OR REPLACE FUNCTION materialize_architecture_tasks(
    p_architecture_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
DECLARE
    v_arch agent_architectures%ROWTYPE;
    v_project_code TEXT;
    v_materialized_count INT := 0;
    v_dependency_count INT := 0;
BEGIN
    IF p_architecture_id IS NULL THEN
        RAISE EXCEPTION 'architecture_id_required';
    END IF;

    SELECT * INTO v_arch
    FROM agent_architectures
    WHERE id = p_architecture_id
    FOR SHARE;

    IF v_arch.id IS NULL THEN
        RAISE EXCEPTION 'architecture_not_found: %', p_architecture_id;
    END IF;

    SELECT code INTO v_project_code
    FROM agent_projects
    WHERE id = v_arch.project_id
    FOR SHARE;

    IF v_project_code = 'JESS' THEN
        RAISE EXCEPTION 'protected_project_refuses_task_materialization: %', v_project_code;
    END IF;

    IF v_arch.tasks IS NOT NULL AND jsonb_typeof(v_arch.tasks) <> 'array' THEN
        RAISE EXCEPTION 'architecture_tasks_not_array: %', p_architecture_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM jsonb_array_elements(COALESCE(v_arch.tasks, '[]'::jsonb)) AS elem(task_doc)
        WHERE NULLIF(elem.task_doc ->> 'task_id', '') IS NULL
           OR NOT (
                elem.task_doc ->> 'task_id'
            ) ~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    ) THEN
        RAISE EXCEPTION 'invalid_or_missing_decomposition_task_id: %', p_architecture_id;
    END IF;

    IF EXISTS (
        SELECT 1
        FROM jsonb_array_elements(COALESCE(v_arch.tasks, '[]'::jsonb)) AS elem(task_doc)
        CROSS JOIN LATERAL jsonb_array_elements_text(
            CASE
                WHEN jsonb_typeof(elem.task_doc -> 'dependencies') = 'array'
                    THEN elem.task_doc -> 'dependencies'
                ELSE '[]'::jsonb
            END
        ) AS dep(decomposition_task_id)
        WHERE dep.decomposition_task_id !~* '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    ) THEN
        RAISE EXCEPTION 'invalid_dependency_decomposition_task_id: %', p_architecture_id;
    END IF;

    IF EXISTS (
        WITH source_ids AS (
            SELECT (elem.task_doc ->> 'task_id')::uuid AS decomposition_task_id
            FROM jsonb_array_elements(COALESCE(v_arch.tasks, '[]'::jsonb)) AS elem(task_doc)
        ),
        dependency_ids AS (
            SELECT dep.decomposition_task_id::uuid AS decomposition_task_id
            FROM jsonb_array_elements(COALESCE(v_arch.tasks, '[]'::jsonb)) AS elem(task_doc)
            CROSS JOIN LATERAL jsonb_array_elements_text(
                CASE
                    WHEN jsonb_typeof(elem.task_doc -> 'dependencies') = 'array'
                        THEN elem.task_doc -> 'dependencies'
                    ELSE '[]'::jsonb
                END
            ) AS dep(decomposition_task_id)
        )
        SELECT 1
        FROM dependency_ids d
        WHERE NOT EXISTS (
            SELECT 1
            FROM source_ids s
            WHERE s.decomposition_task_id = d.decomposition_task_id
        )
    ) THEN
        RAISE EXCEPTION 'dependency_points_outside_architecture: %', p_architecture_id;
    END IF;

    WITH source_tasks AS (
        SELECT
            v_arch.project_id AS project_id,
            v_arch.id AS architecture_id,
            (elem.task_doc ->> 'task_id')::uuid AS decomposition_task_id,
            COALESCE(
                NULLIF(elem.task_doc ->> 'name', ''),
                NULLIF(elem.task_doc ->> 'title', ''),
                'Architecture task ' || elem.ordinality::text
            ) AS title,
            NULLIF(elem.task_doc ->> 'description', '') AS description,
            CASE
                WHEN jsonb_typeof(elem.task_doc -> 'inputs') = 'array'
                    THEN elem.task_doc -> 'inputs'
                ELSE '[]'::jsonb
            END AS inputs,
            CASE
                WHEN jsonb_typeof(elem.task_doc -> 'outputs') = 'array'
                    THEN elem.task_doc -> 'outputs'
                ELSE '[]'::jsonb
            END AS outputs,
            CASE
                WHEN jsonb_typeof(elem.task_doc -> 'dependencies') = 'array'
                    THEN elem.task_doc -> 'dependencies'
                ELSE '[]'::jsonb
            END AS dependencies,
            NULLIF(elem.task_doc ->> 'component', '') AS component,
            CASE
                WHEN (elem.task_doc ->> 'estimated_hours') ~ '^[0-9]+(\.[0-9]+)?$'
                    THEN (elem.task_doc ->> 'estimated_hours')::numeric
                ELSE NULL
            END AS estimated_hours
        FROM jsonb_array_elements(COALESCE(v_arch.tasks, '[]'::jsonb))
            WITH ORDINALITY AS elem(task_doc, ordinality)
    ),
    upserted AS (
        INSERT INTO agent_tasks (
            project_id,
            title,
            description,
            status,
            priority,
            assigned_agent,
            spec_reference,
            architecture_id,
            decomposition_task_id,
            inputs,
            outputs,
            dependencies,
            component,
            estimated_hours
        )
        SELECT
            project_id,
            title,
            description,
            'pending',
            'medium',
            NULL,
            v_arch.spec_id::text,
            architecture_id,
            decomposition_task_id,
            inputs,
            outputs,
            dependencies,
            component,
            estimated_hours
        FROM source_tasks
        ON CONFLICT (architecture_id, decomposition_task_id)
            WHERE architecture_id IS NOT NULL AND decomposition_task_id IS NOT NULL
        DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            inputs = EXCLUDED.inputs,
            outputs = EXCLUDED.outputs,
            dependencies = EXCLUDED.dependencies,
            component = EXCLUDED.component,
            estimated_hours = EXCLUDED.estimated_hours,
            updated_at = now()
        RETURNING id
    )
    SELECT count(*) INTO v_materialized_count
    FROM upserted;

    WITH materialized_tasks AS (
        SELECT id, decomposition_task_id
        FROM agent_tasks
        WHERE architecture_id = p_architecture_id
          AND decomposition_task_id IS NOT NULL
    ),
    source_dependencies AS (
        SELECT
            (elem.task_doc ->> 'task_id')::uuid AS task_decomposition_id,
            dep.decomposition_task_id::uuid AS depends_on_decomposition_id
        FROM jsonb_array_elements(COALESCE(v_arch.tasks, '[]'::jsonb)) AS elem(task_doc)
        CROSS JOIN LATERAL jsonb_array_elements_text(
            CASE
                WHEN jsonb_typeof(elem.task_doc -> 'dependencies') = 'array'
                    THEN elem.task_doc -> 'dependencies'
                ELSE '[]'::jsonb
            END
        ) AS dep(decomposition_task_id)
    ),
    deleted AS (
        DELETE FROM agent_task_dependencies existing
        USING materialized_tasks mt
        WHERE existing.task_id = mt.id
    ),
    inserted AS (
        INSERT INTO agent_task_dependencies (
            task_id,
            depends_on_task_id,
            dependency_type
        )
        SELECT
            task_row.id,
            depends_on_row.id,
            'blocks'
        FROM source_dependencies sd
        JOIN materialized_tasks task_row
          ON task_row.decomposition_task_id = sd.task_decomposition_id
        JOIN materialized_tasks depends_on_row
          ON depends_on_row.decomposition_task_id = sd.depends_on_decomposition_id
        WHERE task_row.id <> depends_on_row.id
        ON CONFLICT (task_id, depends_on_task_id) DO UPDATE
            SET dependency_type = EXCLUDED.dependency_type
        RETURNING id
    )
    SELECT count(*) INTO v_dependency_count
    FROM inserted;

    RETURN jsonb_build_object(
        'ok', true,
        'architecture_id', p_architecture_id,
        'materialized_tasks', v_materialized_count,
        'materialized_dependencies', v_dependency_count,
        'dependency_model', 'agent_task_dependencies is canonical; agent_tasks.dependencies is projection only'
    );
END;
$$;

REVOKE ALL ON FUNCTION materialize_architecture_tasks(UUID) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION materialize_architecture_tasks(UUID) TO service_role;

COMMENT ON COLUMN agent_tasks.architecture_id IS
    'Nullable FK to agent_architectures.id. NULL means legacy/manual/non-architecture task.';
COMMENT ON COLUMN agent_tasks.decomposition_task_id IS
    'Architecture decomposition task_id from agent_architectures.tasks[*].task_id; distinct from agent_tasks.id.';
COMMENT ON COLUMN agent_tasks.inputs IS
    'Projected architecture task inputs array for build context.';
COMMENT ON COLUMN agent_tasks.outputs IS
    'Projected architecture task outputs array for build/verification context.';
COMMENT ON COLUMN agent_tasks.dependencies IS
    'Non-canonical projection of architecture decomposition dependencies. agent_task_dependencies remains canonical for dispatch.';
COMMENT ON COLUMN agent_tasks.component IS
    'Projected architecture component key for this task.';
COMMENT ON COLUMN agent_tasks.estimated_hours IS
    'Projected non-negative effort estimate from architecture decomposition.';
COMMENT ON FUNCTION materialize_architecture_tasks(UUID) IS
    'Materializes future Architecture Agent decomposition tasks into agent_tasks. Intended to be called from create_architecture_revision in the same transaction.';

-- REQUIRED RPC PATCH POINT
-- This migration is complete only when create_architecture_revision includes
-- this call after v_new_id is assigned and root_architecture_id has been set,
-- before the final JSON return:
--
--     PERFORM materialize_architecture_tasks(v_new_id);
--
-- The helper raises exceptions for protected projects, invalid task ids, or write
-- errors so the surrounding RPC transaction rolls back instead of leaving a
-- partially materialized architecture revision.

COMMIT;
