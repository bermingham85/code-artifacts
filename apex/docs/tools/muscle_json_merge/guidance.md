# GUIDANCE — muscle_json_merge

## When to Use

- Combine config files from multiple sources
- Merge n8n workflow exports with overrides
- Consolidate multiple JSON data outputs into one

## How to Call

```bash
python registry/muscle_json_merge.py --inputs "base.json,override.json" --output "merged.json"
python registry/muscle_json_merge.py --inputs "a.json,b.json,c.json" --output "out.json"
```

### Via Telegram
```
/ticket merge config.json with overrides.json into final.json
```
