# GUIDANCE — muscle_drop_ticket

## When to Use

- Any time you want to run a muscle asynchronously via the Apex pipeline
- When you need the full QA gate + audit trail (not just direct execution)
- For scheduled or queued work

## How to Call

```bash
# Drop a health check
python registry/muscle_drop_ticket.py --action muscle_health_check --project APEX

# Drop a file copy with QA
python registry/muscle_drop_ticket.py \
  --action muscle_file_copy \
  --inputs "C:/src.txt,C:/dest.txt" \
  --qa-rule FILE_EXISTS \
  --qa-target "C:/dest.txt"
```

### Via Telegram
```
/ticket <any natural language> → Brian maps intent to a muscle and calls this
/ticket muscle_health_check    → direct fast path
```

## Pipeline Flow

```
muscle_drop_ticket → hub/<job>.json → n8n Blind Postman → foreman.py → QA gate → audit/
```
