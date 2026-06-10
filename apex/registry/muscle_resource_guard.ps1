param(
    [Parameter(Mandatory = $true)]
    [string]$JobName,

    [string]$LockDir = ".\store\locks",

    [double]$MinDiskFreeGB = 10,

    [double]$MinMemoryFreeGB = 2,

    [int]$LockTtlMinutes = 240,

    [switch]$RequireGpuLock,

    [switch]$Release
)

<#
Ref: APEX-MB-CFG-00004
Version: 1.0
Description: Apex resource gate for scheduled jobs; checks disk/memory and manages lock files.
Outputs: JSON status on stdout.
Security: No secrets read or written.
#>

$ErrorActionPreference = "Stop"

function Write-JsonResult {
    param(
        [string]$Status,
        [string]$Message,
        [hashtable]$Data = @{}
    )
    $result = [ordered]@{
        status = $Status
        message = $Message
        generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
        data = $Data
    }
    $result | ConvertTo-Json -Depth 6
}

New-Item -ItemType Directory -Force -Path $LockDir | Out-Null

$jobSafeName = ($JobName -replace '[^A-Za-z0-9_.-]', '_')
$jobLock = Join-Path $LockDir "$jobSafeName.lock.json"
$gpuLock = Join-Path $LockDir "gpu.lock.json"

if ($Release) {
    $released = @()
    if (Test-Path -LiteralPath $jobLock) {
        Remove-Item -LiteralPath $jobLock -Force
        $released += $jobLock
    }
    if ($RequireGpuLock -and (Test-Path -LiteralPath $gpuLock)) {
        $gpuLockContent = Get-Content -LiteralPath $gpuLock -Raw | ConvertFrom-Json
        if ($gpuLockContent.job_name -eq $JobName) {
            Remove-Item -LiteralPath $gpuLock -Force
            $released += $gpuLock
        }
    }
    Write-JsonResult -Status "OK" -Message "Requested locks released." -Data @{ released = $released }
    exit 0
}

$globalLocks = @("backup.lock.json", "deploy.lock.json", "destructive.lock.json")
if ($RequireGpuLock) {
    $globalLocks += "gpu.lock.json"
}

$now = Get-Date
$blockingLocks = @()

if (Test-Path -LiteralPath $jobLock) {
    $lockItem = Get-Item -LiteralPath $jobLock
    $ageMinutes = ($now - $lockItem.LastWriteTime).TotalMinutes
    if ($ageMinutes -le $LockTtlMinutes) {
        $blockingLocks += [ordered]@{
            path = $jobLock
            age_minutes = [math]::Round($ageMinutes, 2)
        }
    } else {
        Remove-Item -LiteralPath $jobLock -Force
    }
}

foreach ($lockName in $globalLocks) {
    $lockPath = Join-Path $LockDir $lockName
    if (Test-Path -LiteralPath $lockPath) {
        $lockItem = Get-Item -LiteralPath $lockPath
        $ageMinutes = ($now - $lockItem.LastWriteTime).TotalMinutes
        if ($ageMinutes -le $LockTtlMinutes) {
            $blockingLocks += [ordered]@{
                path = $lockPath
                age_minutes = [math]::Round($ageMinutes, 2)
            }
        } else {
            Remove-Item -LiteralPath $lockPath -Force
        }
    }
}

if ($blockingLocks.Count -gt 0) {
    Write-JsonResult -Status "BLOCKED" -Message "A blocking lock is active." -Data @{ blocking_locks = $blockingLocks }
    exit 2
}

$systemDrive = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='$env:SystemDrive'"
$freeDiskGb = [math]::Round(($systemDrive.FreeSpace / 1GB), 2)
if ($freeDiskGb -lt $MinDiskFreeGB) {
    Write-JsonResult -Status "BLOCKED" -Message "Insufficient free disk space." -Data @{
        free_disk_gb = $freeDiskGb
        min_disk_free_gb = $MinDiskFreeGB
    }
    exit 3
}

$os = Get-CimInstance Win32_OperatingSystem
$freeMemoryGb = [math]::Round(($os.FreePhysicalMemory / 1MB), 2)
if ($freeMemoryGb -lt $MinMemoryFreeGB) {
    Write-JsonResult -Status "BLOCKED" -Message "Insufficient free memory." -Data @{
        free_memory_gb = $freeMemoryGb
        min_memory_free_gb = $MinMemoryFreeGB
    }
    exit 4
}

$lockPayload = [ordered]@{
    job_name = $JobName
    created_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    process_id = $PID
    min_disk_free_gb = $MinDiskFreeGB
    min_memory_free_gb = $MinMemoryFreeGB
    require_gpu_lock = [bool]$RequireGpuLock
}

$lockPayload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $jobLock -Encoding UTF8
if ($RequireGpuLock) {
    $lockPayload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $gpuLock -Encoding UTF8
}

Write-JsonResult -Status "OK" -Message "Resource checks passed and job lock was created." -Data @{
    lock_path = $jobLock
    gpu_lock_path = $(if ($RequireGpuLock) { $gpuLock } else { $null })
    free_disk_gb = $freeDiskGb
    free_memory_gb = $freeMemoryGb
}
