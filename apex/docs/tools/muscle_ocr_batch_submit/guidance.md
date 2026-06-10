# GUIDANCE - muscle_ocr_batch_submit

Use this tool after `muscle_ocr_receipt --mode batch-prep` has produced payload JSON files.

Local checks:

```powershell
python -m py_compile registry\muscle_ocr_batch_submit.py
python registry\muscle_ocr_batch_submit.py --help
```

Do not run live without approved API budget and a non-sensitive payload fixture.
