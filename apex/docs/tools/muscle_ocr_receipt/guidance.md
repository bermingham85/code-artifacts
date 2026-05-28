# GUIDANCE - muscle_ocr_receipt

Use `single` mode for immediate processing and `batch-prep` mode when building a batch payload for cheaper later processing.

Local checks:

```powershell
python -m py_compile registry\muscle_ocr_receipt.py
python registry\muscle_ocr_receipt.py --help
```

Live tests require Google Drive access, OCR dependencies, Anthropic access, and a non-sensitive receipt fixture.
