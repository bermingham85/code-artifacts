# BLUEPRINT - muscle_sheets_append

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00012 |
| Tool | muscle_sheets_append |
| File | `registry/muscle_sheets_append.py` |
| Category | data |
| Status | DRAFT - pending live Google Sheets test |

## Purpose

Appends one or more rows to a Google Sheets tab and creates the tab/header on first use.

## Exact Call

```powershell
python registry\muscle_sheets_append.py --spreadsheet-id SHEET_ID --tab-name Receipts_2026 --rows-file audit\rows.json --credentials C:\path\service_account.json
```

## Safety Boundary

Do not commit service-account credentials or private ledger rows.
