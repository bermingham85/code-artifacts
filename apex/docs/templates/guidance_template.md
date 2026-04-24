# GUIDANCE — {TOOL_NAME}

| Field | Value |
|-------|-------|
| **Ref Code** | {REF_CODE} |
| **Tool Name** | {TOOL_NAME} |
| **Version** | 1.0 |

---

## When to Use This Tool

- Use case 1: describe the scenario
- Use case 2: describe the scenario
- **Do NOT use when:** describe anti-patterns

---

## How to Call It (Direct)

```bash
python registry/{TOOL_NAME}.py --param1 "value" --param2 "value"
```

### Via Apex Work Order (Telegram /ticket)
```
/ticket {natural language description}
# Brian will map this to {TOOL_NAME} automatically
```

### Via Direct Muscle Drop
```bash
python registry/muscle_drop_ticket.py --action {TOOL_NAME} --project APEX
```

---

## Examples

### Example 1: Basic use
```bash
python registry/{TOOL_NAME}.py --param1 "example_value"
```
Expected output:
```json
{"status": "OK", "result": "..."}
```

### Example 2: Edge case
```bash
python registry/{TOOL_NAME}.py --param1 "edge_case_value" --param2 "optional"
```

---

## Common Mistakes

| Mistake | Correct approach |
|---------|-----------------|
| Passing Windows path with backslashes | Use forward slashes or escape: `C:\\path\\to\\file` |
| Forgetting required params | Check blueprint for required vs optional |

---

## Output Interpretation

| Status | Meaning | Action |
|--------|---------|--------|
| `"OK"` | Success | Read `result` field |
| `"ERROR"` | Failure | Read `error` field, check logs |

---

## Related Tools

- **{RELATED_TOOL}** — use instead when {condition}
