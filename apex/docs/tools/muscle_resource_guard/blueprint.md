# BLUEPRINT - muscle_resource_guard

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-CFG-00004 |
| **Tool Name** | muscle_resource_guard |
| **File** | `registry/muscle_resource_guard.ps1` |
| **Category** | system |
| **Version** | 1.0 |
| **Author** | MB / SYS |
| **Created** | 2026-05-23 |
| **Status** | APPROVED |

## Purpose

Prevents startup clashes and unsafe scheduled-job overlap by checking disk, memory, duplicate-job locks, backup/deploy/destructive locks, and optional GPU lock ownership.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `-JobName` | string | yes | Name of the job requesting or releasing a lock |
| `-LockDir` | path | no | Directory for lock files. Default: `.\store\locks` |
| `-MinDiskFreeGB` | number | no | Minimum free system-drive space. Default: `10` |
| `-MinMemoryFreeGB` | number | no | Minimum free memory. Default: `2` |
| `-LockTtlMinutes` | integer | no | Maximum live lock age before stale cleanup. Default: `240` |
| `-RequireGpuLock` | switch | no | Also acquire/release `gpu.lock.json` |
| `-Release` | switch | no | Release the named job lock and matching GPU lock if owned |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | JSON | `{"status":"OK"|"BLOCKED","message":"...","data":{...}}` |
| file | JSON | Lock file at `LockDir/<job>.lock.json`; optional `gpu.lock.json` |
| exit code | integer | `0` OK, `2` lock blocked, `3` disk blocked, `4` memory blocked |

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Windows PowerShell 5+ or PowerShell 7+ | runtime | Uses standard cmdlets only |
| CIM/WMI providers | OS | Uses disk and OS memory counters |
| Write access to lock directory | filesystem | Creates lock directory if missing |

## How It Works

1. Creates the lock directory if missing.
2. If `-Release` is passed, removes the current job lock and matching GPU lock owned by that job.
3. Checks for current job duplicate lock and global backup/deploy/destructive locks.
4. Checks optional GPU lock when `-RequireGpuLock` is passed.
5. Removes stale locks older than `-LockTtlMinutes`.
6. Checks disk and memory thresholds.
7. Creates the job lock and optional GPU lock.
8. Prints JSON status to stdout.

## Limitations and Edge Cases

- The script gates job starts; it does not monitor running processes after the job begins.
- It assumes jobs call `-Release` at completion or rely on TTL cleanup for crash recovery.
- GPU locking is cooperative. Other applications that ignore the lock can still use the GPU.
- Destructive jobs still require a separate backup and rollback gate.

## Calling Convention

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName gpu-batch -RequireGpuLock -MinDiskFreeGB 20 -MinMemoryFreeGB 4
```

Release when the job finishes:

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName gpu-batch -RequireGpuLock -Release
```

## Apex WorkOrder Use

This is a PowerShell support tool. Use it as a preflight command inside scheduled jobs, Task Packets, or wrapper scripts. A job should fail closed when this tool returns `BLOCKED`.
