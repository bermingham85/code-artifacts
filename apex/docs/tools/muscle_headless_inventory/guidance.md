# GUIDANCE - muscle_headless_inventory

| Field | Value |
|-------|-------|
| **Ref Code** | APEX-MB-CFG-00003 |
| **Version** | 1.0 |

## When to Use

- During Phase 1 discovery and inventory for the autonomous delivery stack.
- Before configuring a laptop as an Apex headless worker.
- After hardware, OS, network, or remote-access changes.
- Before issuing remote-access, WOL, backup, or resource-scheduling signoff.

## Do Not Use

- As a credential discovery tool.
- As proof that BIOS/UEFI WOL or AC-restore settings are enabled.
- As a replacement for a security review.

## How to Call

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_headless_inventory.ps1 -OutputDir .\audit\headless_inventory
```

For temporary validation outside the repo:

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_headless_inventory.ps1 -OutputDir C:\tmp\apex_headless_inventory_test
```

## Example Output

```json
{
  "status": "OK",
  "output_path": "C:\\tmp\\apex_headless_inventory_test\\headless_inventory_20260523T054616Z.json",
  "generated_at_utc": "2026-05-23T05:46:18.4252629Z"
}
```

## Review Checklist

| Check | Expected |
|---|---|
| Stdout parses as JSON | yes |
| `status` is `OK` | yes |
| Output file exists | yes |
| Output contains no secret values | yes, by design |
| BIOS-only settings are separately verified | required before power signoff |

## Common Mistakes

- Treating inventory output as remote-access approval. Access approval still requires the Remote Access Signoff.
- Committing raw inventory files if they contain private hostnames or network details. Store operational evidence in the audit area approved for the deployment.
- Assuming Wi-Fi WOL works. Prefer Ethernet and verify WOL separately.
