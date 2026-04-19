# BLUEPRINT — {TOOL_NAME}

| Field | Value |
|-------|-------|
| **Ref Code** | {REF_CODE} |
| **Tool Name** | {TOOL_NAME} |
| **File** | `registry/{TOOL_NAME}.py` |
| **Category** | {system \| files \| data \| media \| comms \| ai} |
| **Version** | 1.0 |
| **Author** | MB / SYS |
| **Created** | {DATE} |
| **Status** | DRAFT → APPROVED |

---

## Purpose

One sentence: what does this tool do and why does it exist?

---

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `--param1` | string | yes | Description |
| `--param2` | string | no | Description (default: X) |

---

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | JSON | `{"status": "OK", "result": ...}` or `{"status": "ERROR", "error": "..."}` |
| file | path | If the tool writes a file, describe it here |

**Always returns JSON on stdout.** Status is either `"OK"` or `"ERROR"`.

---

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Python 3.11+ | runtime | Standard library only, no pip required |
| `some_package` | pip | Install: `pip install some_package` |
| `N:\projects\` | filesystem | QNAP drive must be mounted |

---

## How It Works (brief)

1. Step one of the internal logic
2. Step two
3. Step three

---

## Limitations & Edge Cases

- What it does NOT do
- Known failure modes
- Performance limits (max file size, max records, etc.)

---

## Calling Convention (Apex WorkOrder)

```json
{
  "sop": {
    "action": "{TOOL_NAME}",
    "params": {
      "param1": "value",
      "param2": "value"
    }
  },
  "qa": {
    "rule": "FILE_EXISTS | SIZE_GT_ZERO | CONTAINS_STRING",
    "target": "path/to/expected/output"
  }
}
```
