# GUIDANCE — muscle_file_copy

## When to Use

- Backup a file before modifying it
- Move output from one Apex stage to another
- Deploy a compiled file to a target location

## How to Call

```bash
python registry/muscle_file_copy.py --source "C:/path/source.txt" --dest "C:/path/dest.txt"
```

### Via Telegram
```
/ticket copy file X to Y
/ticket backup config.json to config.json.bak
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Source doesn't exist | Check path; use forward slashes or escaped backslashes |
| Dest dir doesn't exist | No action needed — tool creates it automatically |
