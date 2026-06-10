# GUIDANCE - muscle_sheets_append

Use this tool only after rows have been validated against the receipt ledger schema.

Local checks:

```powershell
python -m py_compile registry\muscle_sheets_append.py
python registry\muscle_sheets_append.py --help
```

Live tests require a dedicated test spreadsheet and service-account write access.
