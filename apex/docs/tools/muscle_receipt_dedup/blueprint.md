# BLUEPRINT - muscle_receipt_dedup

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00013 |
| Tool | muscle_receipt_dedup |
| File | `registry/muscle_receipt_dedup.py` |
| Category | data |
| Status | DRAFT - local smoke tested |

## Purpose

Maintains a local SQLite ledger of processed Google Drive file IDs so receipt workflows do not append duplicates.

## Exact Calls

```powershell
python registry\muscle_receipt_dedup.py --action check --file-id DRIVE_FILE_ID --db-file audit\dedup\receipts.sqlite
python registry\muscle_receipt_dedup.py --action mark --file-id DRIVE_FILE_ID --receipt-id RECEIPT_ID --db-file audit\dedup\receipts.sqlite
```
