# AGEN Task Lineage Live Schema Inspection

| Field | Value |
|---|---|
| Work order | `WO-APEX-AGEN-TASK-LINEAGE-IMPLEMENT-007` |
| Timestamp | 2026-05-30T06:56:41Z |
| Project ref | `ylcepmvbjjnwmzvevxid` |
| Method | Supabase PostgREST OpenAPI metadata request |
| Auth source | Windows environment variables; names observed only, values not printed |
| Data rows read | No |
| Secrets recorded | No |

## Result

The live schema confirms the task-lineage gap. `agent_tasks` is present but has no direct lineage columns back to `agent_architectures.tasks[*]`.

## Target Tables

| Table | Present | Columns observed |
|---|---|---|
| `agent_tasks` | yes | `id`, `project_id`, `title`, `description`, `status`, `priority`, `assigned_agent`, `parent_task_id`, `spec_reference`, `notes`, `started_at`, `completed_at`, `created_at`, `updated_at` |
| `agent_architectures` | yes | `id`, `project_id`, `spec_id`, `task_id`, `action`, `components`, `tasks`, `build_order`, `dependencies`, `status`, `version`, `parent_architecture_id`, `root_architecture_id`, `idempotency_key`, `request_payload_hash`, `stored_response`, `summary`, `requested_by`, `notes`, `created_at`, `updated_at` |
| `agent_task_dependencies` | yes | `id`, `task_id`, `depends_on_task_id`, `dependency_type`, `created_at` |
| `agent_build_artifacts` | yes | `id`, `project_id`, `task_id`, `architecture_id`, `spec_id`, `type`, `name`, `content`, `content_hash`, `content_bytes`, `deploy_instructions`, `status`, `rejection_reason`, `version`, `parent_artifact_id`, `root_artifact_id`, `idempotency_key`, `request_payload_hash`, `stored_response`, `requested_by`, `notes`, `created_at`, `updated_at` |
| `agent_verifications` | yes | `id`, `project_id`, `task_id`, `spec_id`, `build_artifact_id`, `status`, `findings`, `summary`, `reviewer`, `reasoning_effort`, `codex_run_id`, `codex_status`, `version`, `parent_verification_id`, `root_verification_id`, `idempotency_key`, `requested_by`, `notes`, `created_at`, `updated_at` |
| `agent_routing_logs` | yes | `id`, `project_id`, `task_id`, `spec_id`, `request_id`, `request_text`, `intent`, `confidence`, `routed_to`, `reason`, `phase_check`, `phase_blocker`, `agent_response`, `llm_model`, `classification_latency_ms`, `total_latency_ms`, `outcome`, `error_code`, `error_message`, `idempotency_key`, `request_payload_hash`, `stored_response`, `requested_by`, `session_id`, `notes`, `created_at`, `updated_at` |

## Gap Confirmation

Missing from `agent_tasks`:

- `architecture_id`
- `decomposition_task_id`
- `inputs`
- `outputs`
- `component`
- `estimated_hours`
- any documented task-lineage projection column

`agent_build_artifacts` already contains `architecture_id` and `spec_id`, so downstream build artifacts can hold architecture context after the task is built. The missing link is before build: the operational task row itself cannot deterministically identify the architecture decomposition entry that created it.

## Decision Enabled

S1 live schema inspection is complete for the implementation packet. Next safe step is owner decision and migration drafting. No production migration has been run.
