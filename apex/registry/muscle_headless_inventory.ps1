param(
    [string]$OutputDir = ".\audit\headless_inventory"
)

<#
Ref: APEX-MB-CFG-00003
Version: 1.0
Description: Read-only headless laptop inventory for Apex remote worker setup.
Outputs: JSON summary on stdout and a timestamped inventory JSON file.
Security: Does not collect secret values.
#>

$ErrorActionPreference = "Stop"

function Get-SafeCim {
    param([string]$ClassName)
    try {
        Get-CimInstance -ClassName $ClassName
    } catch {
        $null
    }
}

function ConvertTo-PlainObject {
    param($InputObject)
    if ($null -eq $InputObject) {
        return $null
    }
    $InputObject | Select-Object *
}

$repoRoot = Resolve-Path -LiteralPath "." | Select-Object -ExpandProperty Path
if ([System.IO.Path]::IsPathRooted($OutputDir)) {
    $targetOutputDir = $OutputDir
} else {
    $targetOutputDir = Join-Path $repoRoot $OutputDir
}
New-Item -ItemType Directory -Force -Path $targetOutputDir | Out-Null

$timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outputPath = Join-Path $targetOutputDir "headless_inventory_$timestamp.json"

$computer = Get-SafeCim "Win32_ComputerSystem"
$os = Get-SafeCim "Win32_OperatingSystem"
$cpu = Get-SafeCim "Win32_Processor"
$gpu = Get-SafeCim "Win32_VideoController"
$bios = Get-SafeCim "Win32_BIOS"
$disks = Get-SafeCim "Win32_LogicalDisk"
$network = Get-SafeCim "Win32_NetworkAdapterConfiguration" | Where-Object { $_.IPEnabled -eq $true }

$inventory = [ordered]@{
    status = "OK"
    generated_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    hostname = $env:COMPUTERNAME
    user_context = $env:USERNAME
    computer = ConvertTo-PlainObject $computer
    os = ConvertTo-PlainObject $os
    cpu = ConvertTo-PlainObject $cpu
    gpu = ConvertTo-PlainObject $gpu
    bios = ConvertTo-PlainObject $bios
    disks = ConvertTo-PlainObject $disks
    network = ConvertTo-PlainObject $network
    tailscale = [ordered]@{
        installed = [bool](Get-Command tailscale -ErrorAction SilentlyContinue)
        note = "If installed, run tailscale status separately when authorized. This script does not expose auth keys."
    }
    ssh = [ordered]@{
        ssh_client_available = [bool](Get-Command ssh -ErrorAction SilentlyContinue)
        sshd_service = ConvertTo-PlainObject (Get-Service -Name sshd -ErrorAction SilentlyContinue)
    }
    security_notes = @(
        "No secrets collected.",
        "Public key fingerprints and credential reference names should be recorded separately.",
        "BIOS Wake-on-LAN and AC power recovery settings usually require physical or vendor-tool verification."
    )
}

$inventory | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $outputPath -Encoding UTF8

[ordered]@{
    status = "OK"
    output_path = $outputPath
    generated_at_utc = $inventory.generated_at_utc
} | ConvertTo-Json -Depth 4
