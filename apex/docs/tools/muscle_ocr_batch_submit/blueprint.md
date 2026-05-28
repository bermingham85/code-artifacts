# BLUEPRINT - muscle_ocr_batch_submit

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00015 |
| Tool | muscle_ocr_batch_submit |
| File | `registry/muscle_ocr_batch_submit.py` |
| Category | ai |
| Status | DRAFT - pending ref cleanup and live Anthropic batch test |

## Purpose

Submits prepared receipt OCR payload JSON files as one Anthropic Message Batch and writes a manifest for later retrieval.

## Exact Call

```powershell
python registry\muscle_ocr_batch_submit.py --payloads-dir audit\ocr\payloads --manifest-file audit\ocr\batch_manifest.json --anthropic-key %ANTHROPIC_API_KEY%
```

## Known Governance Issue

This file currently shares `APEX-MB-PY-00015` with `muscle_classify_document.py`. Estate cleanup Phase A must resolve the duplicate before approval.
