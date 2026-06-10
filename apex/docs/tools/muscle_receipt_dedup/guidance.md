# GUIDANCE - muscle_receipt_dedup

Use `check` before OCR/append and `mark` only after the receipt has been successfully processed.

Local checks:

```powershell
python -m py_compile registry\muscle_receipt_dedup.py
python registry\muscle_receipt_dedup.py --help
```

The database file is local state; keep it out of broad commits unless it is a deliberate fixture.
