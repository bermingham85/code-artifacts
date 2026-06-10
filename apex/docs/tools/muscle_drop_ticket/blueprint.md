# BLUEPRINT — muscle_drop_ticket

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00008 |
| **Tool Name** | muscle_drop_ticket |
| **Category** | system |
| **Version** | 1.0 |
| **Status** | APPROVED |

## Purpose

Builds a valid WorkOrder JSON and atomically drops it into `hub/` for the n8n Blind Postman to pick up and execute via foreman.py. This is the primary way to trigger any other muscle.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--action` | string | yes | Muscle name (e.g. `muscle_health_check`) |
| `--project` | string | no | Project code (default: APEX) |
| `--inputs` | string | no | Comma-separated input file paths for the muscle |
| `--qa-rule` | string | no | QA gate rule: FILE_EXISTS \| SIZE_GT_ZERO \| CONTAINS_STRING |
| `--qa-target` | string | no | Path the QA gate checks |

## Outputs

stdout: `{"status": "OK", "job_id": "<uuid>", "output": "<hub_path>"}` or `{"status": "ERROR", ...}`

The WorkOrder JSON is written atomically to `hub/<job_id>.json`. n8n polls this directory.

## Dependencies

- `hub/` directory must exist and be writable
- n8n Blind Postman workflow must be active on QNAP
