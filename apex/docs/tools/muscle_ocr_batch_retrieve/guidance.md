# GUIDANCE - muscle_ocr_batch_retrieve

Use this tool after `muscle_ocr_batch_submit` returns a batch manifest.

Local checks:

```powershell
python -m py_compile registry\muscle_ocr_batch_retrieve.py
python registry\muscle_ocr_batch_retrieve.py --help
```

If status is `PENDING`, schedule a later retry rather than treating it as failure.
