# BLUEPRINT — muscle_health_check

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00007 |
| **Tool Name** | muscle_health_check |
| **File** | `registry/muscle_health_check.py` |
| **Category** | system |
| **Version** | 1.0 |
| **Author** | MB / SYS |
| **Created** | 2026-02-27 |
| **Status** | APPROVED |

## Purpose

Runs a full system health check and writes a structured JSON report covering disk space, Python environment, Apex manifest state, foreman heartbeat, and n8n reachability.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--output` | path | no | Where to write health_report.json (default: `audit/health/health_report.json`) |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | JSON | `{"status": "OK", "output": "<path>"}` |
| file | JSON | Full health report at output path |

**Report fields:** `disk_free_gb`, `disk_total_gb`, `disk_pct_used`, `python_version`, `platform`, `pip_packages`, `manifest_skills`, `manifest_last_indexed`, `heartbeat_age_seconds`, `n8n_reachable`, `overall` (OK/WARN/ERROR), `timestamp`

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Python 3.11+ | runtime | stdlib only |
| n8n | network | 192.168.50.246:5678 (tested with urllib, graceful if unreachable) |
| manifest.json | filesystem | `registry/manifest.json` |

## How It Works

1. Measures disk free/total for Apex root drive
2. Collects Python version + pip count
3. Reads manifest.json for skill count + last indexed timestamp
4. Checks foreman heartbeat file age (`hub/.heartbeat`)
5. HTTP GET to n8n `/api/v1/workflows` (1s timeout, non-blocking)
6. Computes `overall`: OK if disk >5GB free + n8n reachable, WARN if marginal, ERROR if critical

## Limitations

- n8n check is fire-and-forget; no auth header sent (counts reachability only)
- Disk check uses the drive containing the Apex root, not all drives
- Does not check GPU machine, QNAP storage health, or Claude API status

## Calling Convention

```json
{
  "sop": { "action": "muscle_health_check", "params": {} },
  "qa":  { "rule": "FILE_EXISTS", "target": "audit/health/health_report.json" }
}
```
