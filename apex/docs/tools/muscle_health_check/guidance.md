# GUIDANCE — muscle_health_check

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00007 |
| **Version** | 1.0 |

## When to Use

- Before starting a heavy batch job (confirm disk space)
- When system feels slow or unresponsive
- As a scheduled daily check (cron: `0 8 * * *`)
- After a restart to confirm everything came back up
- **Do NOT use as a substitute for monitoring** — for persistent monitoring use supervisor.py

## How to Call

```bash
# Default output path
python registry/muscle_health_check.py

# Custom output path
python registry/muscle_health_check.py --output "C:/path/to/report.json"
```

### Via Telegram
```
/ticket check system health
/ticket run a health check
/ticket health
```

### Via Work Order drop
```bash
python registry/muscle_drop_ticket.py --action muscle_health_check --project APEX
```

## Example Output

```json
{
  "status": "OK",
  "output": "C:\\Users\\bermi\\Projects\\apex\\audit\\health\\health_report.json"
}
```

Report file:
```json
{
  "timestamp": "2026-02-28T10:00:00Z",
  "disk_free_gb": 45.2,
  "disk_total_gb": 500.0,
  "disk_pct_used": 90.9,
  "python_version": "3.11.8",
  "manifest_skills": 48,
  "manifest_last_indexed": "2026-02-27T12:45:46Z",
  "heartbeat_age_seconds": 45,
  "n8n_reachable": true,
  "overall": "OK"
}
```

## Output Interpretation

| overall | Meaning |
|---------|---------|
| `OK` | All systems nominal |
| `WARN` | Disk getting low (<10GB) OR heartbeat old (>5min) |
| `ERROR` | Disk critical (<2GB) OR n8n unreachable |
