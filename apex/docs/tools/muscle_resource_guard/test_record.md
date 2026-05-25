# TEST RECORD - muscle_resource_guard

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-CFG-00004 |
| **Tested By** | Codex |
| **Test Date** | 2026-05-23 |
| **Overall Result** | PASS |

## Test Environment

| Field | Value |
|---|---|
| OS | Windows |
| Workspace | `C:\Users\Owner\Repos\code-artifacts\apex` |
| Lock test directory | `C:\tmp\apex_lock_test` |

## Test Cases

### TC-001: PowerShell syntax validation

**Command:** Parsed the script with `[scriptblock]::Create(...)`.

**Expected:** No parser error.

**Result:** PASS - `PowerShell syntax OK`.

### TC-002: Create job lock after resource checks

**Command:** `powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName codex-smoke-test -LockDir C:\tmp\apex_lock_test -MinDiskFreeGB 1 -MinMemoryFreeGB 0.1`

**Expected:** JSON stdout with `status: OK` and lock file path.

**Result:** PASS - lock file created at `C:\tmp\apex_lock_test\codex-smoke-test.lock.json`.

### TC-003: Release job lock

**Command:** `powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName codex-smoke-test -LockDir C:\tmp\apex_lock_test -Release`

**Expected:** JSON stdout with `status: OK` and released lock list.

**Result:** PASS - lock file released.

### TC-004: Release verification

**Command:** `Test-Path -LiteralPath C:\tmp\apex_lock_test\codex-smoke-test.lock.json`

**Expected:** `False`.

**Result:** PASS - no stale smoke-test lock remains.

## Summary

| Test | Result |
|------|--------|
| TC-001 Syntax validation | PASS |
| TC-002 Create job lock | PASS |
| TC-003 Release job lock | PASS |
| TC-004 Release verification | PASS |

**All tests passed:** YES
**Approved:** YES - 2026-05-23
