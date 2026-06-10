# TEST RECORD — {TOOL_NAME}

| Field | Value |
|-------|-------|
| **Ref Code** | {REF_CODE} |
| **Tool Name** | {TOOL_NAME} |
| **Tested By** | MB / SYS |
| **Test Date** | {DATE} |
| **Overall Result** | PASS / FAIL |

---

## Test Environment

- OS: Windows 11, C:\Users\bermi\
- Python: 3.11.x
- Dependencies: all installed per blueprint
- QNAP: mounted as N:\

---

## Test Cases

### TC-001: Happy path — basic valid input

**Command:**
```bash
python registry/{TOOL_NAME}.py --param1 "valid_value"
```

**Expected:**
```json
{"status": "OK", "result": "expected_output"}
```

**Actual:**
```json
{paste actual output here}
```

**Result:** PASS / FAIL
**Notes:** —

---

### TC-002: Missing required parameter

**Command:**
```bash
python registry/{TOOL_NAME}.py
```

**Expected:**
- Exit code non-zero
- Error message mentioning the missing param

**Actual:**
```
{paste actual output}
```

**Result:** PASS / FAIL
**Notes:** —

---

### TC-003: Invalid input (bad path / bad format)

**Command:**
```bash
python registry/{TOOL_NAME}.py --param1 "/nonexistent/path/file.txt"
```

**Expected:**
```json
{"status": "ERROR", "error": "..."}
```

**Actual:**
```json
{paste actual output}
```

**Result:** PASS / FAIL
**Notes:** —

---

### TC-004: {Additional test case as needed}

---

## Summary

| Test | Result |
|------|--------|
| TC-001 Happy path | PASS |
| TC-002 Missing param | PASS |
| TC-003 Invalid input | PASS |
| TC-004 ... | PASS |

**All tests passed:** YES / NO
**Approved for registry:** YES / NO
**Approval date:** {DATE}
