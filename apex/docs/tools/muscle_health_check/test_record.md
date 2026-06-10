# TEST RECORD — muscle_health_check

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-PY-00007 |
| **Tested By** | SYS (automated on build) |
| **Test Date** | 2026-02-27 |
| **Overall Result** | PASS |

## Test Environment

- OS: Windows 11, C:\Users\bermi\
- Python: 3.11.x
- n8n: 192.168.50.246:5678 (running)

## Test Cases

### TC-001: Happy path — default output

**Command:** `python registry/muscle_health_check.py`
**Expected:** JSON with `status: OK`, output file written
**Result:** PASS — report written to `audit/health/health_report.json`, overall=OK

### TC-002: Custom output path

**Command:** `python registry/muscle_health_check.py --output "C:/temp/test_health.json"`
**Expected:** File written to custom path
**Result:** PASS

### TC-003: n8n unreachable (simulated)

**Input:** n8n offline
**Expected:** `n8n_reachable: false`, overall=ERROR or WARN depending on disk
**Result:** PASS — graceful degradation, no crash

### TC-004: Missing manifest

**Input:** manifest.json temporarily renamed
**Expected:** `manifest_skills: 0`, `manifest_last_indexed: null`
**Result:** PASS — handled gracefully

## Summary

| Test | Result |
|------|--------|
| TC-001 Happy path | PASS |
| TC-002 Custom output | PASS |
| TC-003 n8n offline | PASS |
| TC-004 No manifest | PASS |

**All tests passed:** YES
**Approved for registry:** YES
**Approval date:** 2026-02-27
