# GUIDANCE - muscle_resource_guard

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-CFG-00004 |
| **Version** | 1.0 |

## When to Use

- Before any scheduled job that can clash with backups, deployments, cleanup, or GPU work.
- Before local model/GPU workloads.
- Before large file-processing, report-generation, or batch API jobs.
- During startup to prevent multiple heavy jobs resuming at once.

## Do Not Use

- As the only guard for destructive operations. Destructive work still needs backup and rollback.
- As a hard security boundary. It is a cooperative scheduler guard.
- As proof that the GPU is idle if other tools ignore Apex lock files.

## How to Call

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName report-batch -MinDiskFreeGB 10 -MinMemoryFreeGB 2
```

For GPU jobs:

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName gpu-batch -RequireGpuLock -MinDiskFreeGB 20 -MinMemoryFreeGB 4
```

Release at job completion:

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName gpu-batch -RequireGpuLock -Release
```

## Example OK Output

```json
{
  "status": "OK",
  "message": "Resource checks passed and job lock was created.",
  "data": {
    "lock_path": "C:\\tmp\\apex_lock_test\\codex-smoke-test.lock.json",
    "free_disk_gb": 1361.51,
    "gpu_lock_path": null,
    "free_memory_gb": 11.92
  }
}
```

## Example Blocked Output

```json
{
  "status": "BLOCKED",
  "message": "A blocking lock is active.",
  "data": {
    "blocking_locks": [
      {
        "path": ".\\store\\locks\\backup.lock.json",
        "age_minutes": 4.2
      }
    ]
  }
}
```

## Scheduled Job Pattern

1. Call `muscle_resource_guard`.
2. If status is `OK`, run the job.
3. Write job evidence.
4. Call `muscle_resource_guard -Release`.
5. If status is `BLOCKED`, skip or queue the job and alert only if the block exceeds policy.

## Common Mistakes

- Forgetting to call `-Release` after successful completion.
- Using the same `JobName` for unrelated jobs.
- Setting `LockTtlMinutes` too low for long-running GPU work.
- Treating a stale-lock cleanup as proof that the crashed job completed successfully.
