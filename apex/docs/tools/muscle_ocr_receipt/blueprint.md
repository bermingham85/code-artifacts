# BLUEPRINT - muscle_ocr_receipt

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00011 |
| Tool | muscle_ocr_receipt |
| File | `registry/muscle_ocr_receipt.py` |
| Category | documents |
| Status | DRAFT - pending live OCR fixture test |

## Purpose

Processes receipt images or PDFs with Tesseract first and Claude vision only when confidence is below threshold. Supports immediate and batch-prep modes.

## Exact Call

```powershell
python registry\muscle_ocr_receipt.py --file-id DRIVE_FILE_ID --image-url DRIVE_URL --credentials C:\path\service_account.json --anthropic-key %ANTHROPIC_API_KEY% --output-file audit\ocr\receipt.json --mode single
```

## Safety Boundary

Receipt data can contain personal and financial information. Do not commit raw receipts, OCR text, or structured receipt JSON unless explicitly approved.
