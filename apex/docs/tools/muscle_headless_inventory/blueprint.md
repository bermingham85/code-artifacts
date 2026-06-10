# BLUEPRINT - muscle_headless_inventory

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-CFG-00003 |
| **Tool Name** | muscle_headless_inventory |
| **File** | `registry/muscle_headless_inventory.ps1` |
| **Category** | system |
| **Version** | 1.0 |
| **Author** | MB / SYS |
| **Created** | 2026-05-23 |
| **Status** | APPROVED |

## Purpose

Captures a read-only headless laptop inventory for Apex remote-worker setup without collecting secret values.

## Inputs

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `-OutputDir` | path | no | Directory for the timestamped inventory JSON. Default: `.\audit\headless_inventory` |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| stdout | JSON | `{"status":"OK","output_path":"...","generated_at_utc":"..."}` |
| file | JSON | Timestamped inventory report containing OS, CPU, GPU, BIOS, disk, network, Tailscale availability, and SSH availability |

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| Windows PowerShell 5+ or PowerShell 7+ | runtime | Uses standard cmdlets only |
| CIM/WMI providers | OS | Uses `Get-CimInstance`; unavailable classes are returned as null |
| Write access to output directory | filesystem | Creates the output directory if missing |

## How It Works

1. Resolves the output directory.
2. Collects Windows CIM inventory classes for computer, OS, processor, video controller, BIOS, logical disks, and active network adapters.
3. Checks whether `tailscale`, `ssh`, and `sshd` are available without reading credentials.
4. Writes a timestamped JSON inventory file.
5. Prints a short JSON success summary to stdout.

## Limitations and Edge Cases

- BIOS Wake-on-LAN and AC power recovery settings may require physical BIOS/UEFI inspection or vendor tooling.
- The script does not run `tailscale status`, because that may expose device/user context beyond the inventory requirement.
- The script does not collect private keys, tokens, passwords, or secret values.
- Very detailed CIM output can produce a large JSON file on some machines.

## Calling Convention

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_headless_inventory.ps1 -OutputDir .\audit\headless_inventory
```

## Apex WorkOrder Use

This is a PowerShell support tool. Use it through a shell-capable runner or a Task Packet rather than the Python-only foreman muscle interface unless the foreman is extended to support PowerShell actions.
