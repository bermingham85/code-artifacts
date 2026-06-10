# BLUEPRINT - muscle_ocr_batch_retrieve

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00016 |
| Tool | muscle_ocr_batch_retrieve |
| File | `registry/muscle_ocr_batch_retrieve.py` |
| Category | ai |
| Status | DRAFT - pending live Anthropic batch test |

## Purpose

Polls an Anthropic Message Batch and writes per-receipt JSON result files when the batch has ended.

## Exact Call

```powershell
python registry\muscle_ocr_batch_retrieve.py --manifest-file audit\ocr\batch_manifest.json --output-dir audit\ocr\results --anthropic-key %ANTHROPIC_API_KEY%
```

## Safety Boundary

Do not commit receipt result files unless they have been checked for sensitive data.
