-- AGEN-SCRPT-pm-supabase-migration-v1.sql
-- Project Manager Agent — Supabase Tables & Functions
-- Date: 2026-02-22
-- Run on: Supabase project ylcepmvbjjnwmzvevxid
-- NOTE: agent_projects table already exists (10 rows) — DO NOT recreate

-----------------------------------------------
-- 1. agent_tasks
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES agent_projects(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','in_progress','complete','blocked','failed')),
    priority TEXT NOT NULL DEFAULT 'medium'
        CHECK (priority IN ('critical','high','medium','low')),
    assigned_agent TEXT,
    parent_task_id UUID REFERENCES agent_tasks(id),
    spec_reference TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_project ON agent_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);

-----------------------------------------------
-- 2. agent_task_dependencies
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_task_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
    depends_on_task_id UUID NOT NULL REFERENCES agent_tasks(id) ON DELETE CASCADE,
    dependency_type TEXT NOT NULL DEFAULT 'blocks'
        CHECK (dependency_type IN ('blocks','informs','optional')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(task_id, depends_on_task_id)
);

-----------------------------------------------
-- 3. agent_sessions
-----------------------------------------------
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES agent_projects(id),
    agent_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active','completed','abandoned')),
    summary TEXT,
    context JSONB DEFAULT '{}'::jsonb,
    tasks_completed UUID[] DEFAULT '{}',
    next_steps TEXT[] DEFAULT '{}',
    started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    ended_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_agent_sessions_project ON agent_sessions(project_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_status ON agent_sessions(status);

-----------------------------------------------
-- 4. Updated-at trigger for agent_tasks
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_agent_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_agent_tasks_updated ON agent_tasks;
CREATE TRIGGER trg_agent_tasks_updated
    BEFORE UPDATE ON agent_tasks
    FOR EACH ROW EXECUTE FUNCTION update_agent_tasks_updated_at();

-----------------------------------------------
-- 5. Helper: get_project_status
-----------------------------------------------
CREATE OR REPLACE FUNCTION get_project_status(p_project_id UUID DEFAULT NULL)
RETURNS JSONB AS $$
BEGIN
    IF p_project_id IS NOT NULL THEN
        RETURN (
            SELECT jsonb_build_object(
                'project', row_to_json(p),
                'task_counts', jsonb_build_object(
                    'total', (SELECT count(*) FROM agent_tasks WHERE project_id = p_project_id),
                    'pending', (SELECT count(*) FROM agent_tasks WHERE project_id = p_project_id AND status = 'pending'),
                    'in_progress', (SELECT count(*) FROM agent_tasks WHERE project_id = p_project_id AND status = 'in_progress'),
                    'complete', (SELECT count(*) FROM agent_tasks WHERE project_id = p_project_id AND status = 'complete'),
                    'blocked', (SELECT count(*) FROM agent_tasks WHERE project_id = p_project_id AND status = 'blocked'),
                    'failed', (SELECT count(*) FROM agent_tasks WHERE project_id = p_project_id AND status = 'failed')
                )
            )
            FROM agent_projects p WHERE p.id = p_project_id
        );
    ELSE
        RETURN (
            SELECT COALESCE(jsonb_agg(
                jsonb_build_object(
                    'project', row_to_json(p),
                    'task_counts', jsonb_build_object(
                        'total', (SELECT count(*) FROM agent_tasks WHERE project_id = p.id),
                        'pending', (SELECT count(*) FROM agent_tasks WHERE project_id = p.id AND status = 'pending'),
                        'in_progress', (SELECT count(*) FROM agent_tasks WHERE project_id = p.id AND status = 'in_progress'),
                        'complete', (SELECT count(*) FROM agent_tasks WHERE project_id = p.id AND status = 'complete'),
                        'blocked', (SELECT count(*) FROM agent_tasks WHERE project_id = p.id AND status = 'blocked'),
                        'failed', (SELECT count(*) FROM agent_tasks WHERE project_id = p.id AND status = 'failed')
                    )
                )
            ), '[]'::jsonb)
            FROM agent_projects p WHERE p.status != 'complete'
        );
    END IF;
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------
-- 6. Helper: get_blockers
-----------------------------------------------
CREATE OR REPLACE FUNCTION get_blockers(p_project_id UUID DEFAULT NULL)
RETURNS JSONB AS $$
BEGIN
    RETURN (
        SELECT COALESCE(jsonb_agg(jsonb_build_object(
            'task_id', t.id,
            'task_title', t.title,
            'project_id', t.project_id,
            'blocked_by', (
                SELECT jsonb_agg(jsonb_build_object(
                    'task_id', dep.depends_on_task_id,
                    'title', dt.title,
                    'status', dt.status
                ))
                FROM agent_task_dependencies dep
                JOIN agent_tasks dt ON dt.id = dep.depends_on_task_id
                WHERE dep.task_id = t.id
                AND dep.dependency_type = 'blocks'
                AND dt.status != 'complete'
            )
        )), '[]'::jsonb)
        FROM agent_tasks t
        WHERE t.status = 'blocked'
        AND (p_project_id IS NULL OR t.project_id = p_project_id)
    );
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------
-- 7. Helper: get_next_actions
-----------------------------------------------
CREATE OR REPLACE FUNCTION get_next_actions(p_project_id UUID DEFAULT NULL, p_limit INT DEFAULT 10)
RETURNS JSONB AS $$
BEGIN
    RETURN (
        SELECT COALESCE(jsonb_agg(jsonb_build_object(
            'task_id', t.id,
            'title', t.title,
            'project_id', t.project_id,
            'priority', t.priority,
            'assigned_agent', t.assigned_agent,
            'notes', t.notes
        )), '[]'::jsonb)
        FROM (
            SELECT t.*
            FROM agent_tasks t
            WHERE t.status = 'pending'
            AND (p_project_id IS NULL OR t.project_id = p_project_id)
            AND NOT EXISTS (
                SELECT 1 FROM agent_task_dependencies dep
                JOIN agent_tasks dt ON dt.id = dep.depends_on_task_id
                WHERE dep.task_id = t.id
                AND dep.dependency_type = 'blocks'
                AND dt.status != 'complete'
            )
            ORDER BY
                CASE t.priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                t.created_at
            LIMIT p_limit
        ) t
    );
END;
$$ LANGUAGE plpgsql;

-----------------------------------------------
-- 8. Helper: update_task_status
-----------------------------------------------
CREATE OR REPLACE FUNCTION update_task_status(
    p_task_id UUID,
    p_new_status TEXT,
    p_notes TEXT DEFAULT ''
)
RETURNS JSONB AS $$
DECLARE
    v_old_status TEXT;
    v_result JSONB;
    v_unblocked INT := 0;
BEGIN
    SELECT status INTO v_old_status FROM agent_tasks WHERE id = p_task_id;

    IF v_old_status IS NULL THEN
        RETURN jsonb_build_object('error', 'Task not found');
    END IF;

    IF v_old_status = 'complete' THEN
        RETURN jsonb_build_object('error', 'Cannot change status of completed task');
    END IF;

    UPDATE agent_tasks
    SET status = p_new_status,
        notes = CASE WHEN p_notes != '' THEN p_notes ELSE notes END
    WHERE id = p_task_id;

    IF p_new_status = 'complete' THEN
        UPDATE agent_tasks SET status = 'pending'
        WHERE status = 'blocked'
        AND id IN (
            SELECT dep.task_id
            FROM agent_task_dependencies dep
            WHERE dep.depends_on_task_id = p_task_id
            AND dep.dependency_type = 'blocks'
        )
        AND NOT EXISTS (
            SELECT 1 FROM agent_task_dependencies dep2
            JOIN agent_tasks dt ON dt.id = dep2.depends_on_task_id
            WHERE dep2.task_id = agent_tasks.id
            AND dep2.dependency_type = 'blocks'
            AND dt.status != 'complete'
            AND dt.id != p_task_id
        );
        GET DIAGNOSTICS v_unblocked = ROW_COUNT;
    END IF;

    v_result := jsonb_build_object(
        'task_id', p_task_id,
        'old_status', v_old_status,
        'new_status', p_new_status,
        'tasks_unblocked', v_unblocked
    );

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;
