# Apex Estate Cleanup Report

| Field | Value |
|---|---|
| Work Order | `hub/WO-APEX-ESTATE-CLEANUP-004.json` |
| Date | 2026-05-27 |
| Status | PARTIAL_BLOCKED |
| Scope completed | Phases A, B, C, D, and E |

## Before

Baseline from `audit/compliance/2026-05-27T11-09-41Z.json`:

| Counter | Value |
|---|---:|
| duplicate_refs | 1 |
| header_register_mismatches | 8 |
| registered_missing | 4 |
| registered_stale_path | 26 |
| muscles_missing_docs | 8 |
| muscles_unapproved | 0 |
| secrets_on_disk | 1 |

## After Phase D

Evidence from `audit/compliance/2026-05-27T11-14-08Z.json`:

| Counter | Value |
|---|---:|
| duplicate_refs | 1 |
| header_register_mismatches | 8 |
| registered_missing | 4 |
| registered_stale_path | 26 |
| muscles_missing_docs | 0 |
| muscles_unapproved | 8 |
| secrets_on_disk | 1 |

Phase D closed the missing-document condition. The eight legacy muscles now have blueprint, guidance, test record, and troubleshoot pages. They remain unapproved because live external-service tests require Google, Anthropic, or Google Sheets credentials and safe fixtures.

## After Phases A/B/C/E

Evidence from `audit/compliance/2026-05-28T09-29-58Z.json`:

| Counter | Value |
|---|---:|
| duplicate_refs | 0 |
| header_register_mismatches | 0 |
| registered_missing | 0 |
| registered_stale_path | 0 |
| muscles_missing_docs | 0 |
| muscles_unapproved | 8 |
| secrets_on_disk | 1 |

Phase A closed the duplicate `APEX-MB-PY-00015` header collision by restoring legacy muscle headers to their existing register refs. Phase B closed all header/register mismatches. Phase C and Phase E are closed by registering the compliance checker and classifying external/session/cross-project rows as external instead of local missing/stale files.

## Created

- `docs/tools/muscle_classify_document/blueprint.md`
- `docs/tools/muscle_classify_document/guidance.md`
- `docs/tools/muscle_classify_document/test_record.md`
- `docs/tools/muscle_classify_document/troubleshoot.md`
- `docs/tools/muscle_gdrive_download/blueprint.md`
- `docs/tools/muscle_gdrive_download/guidance.md`
- `docs/tools/muscle_gdrive_download/test_record.md`
- `docs/tools/muscle_gdrive_download/troubleshoot.md`
- `docs/tools/muscle_gdrive_watcher/blueprint.md`
- `docs/tools/muscle_gdrive_watcher/guidance.md`
- `docs/tools/muscle_gdrive_watcher/test_record.md`
- `docs/tools/muscle_gdrive_watcher/troubleshoot.md`
- `docs/tools/muscle_ocr_batch_retrieve/blueprint.md`
- `docs/tools/muscle_ocr_batch_retrieve/guidance.md`
- `docs/tools/muscle_ocr_batch_retrieve/test_record.md`
- `docs/tools/muscle_ocr_batch_retrieve/troubleshoot.md`
- `docs/tools/muscle_ocr_batch_submit/blueprint.md`
- `docs/tools/muscle_ocr_batch_submit/guidance.md`
- `docs/tools/muscle_ocr_batch_submit/test_record.md`
- `docs/tools/muscle_ocr_batch_submit/troubleshoot.md`
- `docs/tools/muscle_ocr_receipt/blueprint.md`
- `docs/tools/muscle_ocr_receipt/guidance.md`
- `docs/tools/muscle_ocr_receipt/test_record.md`
- `docs/tools/muscle_ocr_receipt/troubleshoot.md`
- `docs/tools/muscle_receipt_dedup/blueprint.md`
- `docs/tools/muscle_receipt_dedup/guidance.md`
- `docs/tools/muscle_receipt_dedup/test_record.md`
- `docs/tools/muscle_receipt_dedup/troubleshoot.md`
- `docs/tools/muscle_sheets_append/blueprint.md`
- `docs/tools/muscle_sheets_append/guidance.md`
- `docs/tools/muscle_sheets_append/test_record.md`
- `docs/tools/muscle_sheets_append/troubleshoot.md`
- `audit/compliance/2026-05-27T11-14-08Z.json`
- `audit/compliance/2026-05-28T09-29-58Z.json`
- `audit/compliance/cleanup-report.md`

## Modified

- `foreman.py` header ref aligned from `APEX-MB-PY-00002` to `APEX-MB-PY-00003`.
- `registry/muscle_classify_document.py` header ref aligned from `APEX-MB-PY-00015` to `APEX-MB-PY-00019`.
- `registry/muscle_gdrive_watcher.py` header ref aligned from `APEX-MB-PY-00010` to `APEX-MB-PY-00013`.
- `registry/muscle_ocr_batch_retrieve.py` header ref aligned from `APEX-MB-PY-00016` to `APEX-MB-PY-00018`.
- `registry/muscle_ocr_batch_submit.py` header ref aligned from `APEX-MB-PY-00015` to `APEX-MB-PY-00017`.
- `registry/muscle_ocr_receipt.py` header ref aligned from `APEX-MB-PY-00011` to `APEX-MB-PY-00016`.
- `registry/muscle_receipt_dedup.py` header ref aligned from `APEX-MB-PY-00013` to `APEX-MB-PY-00020`.
- `registry/muscle_sheets_append.py` header ref aligned from `APEX-MB-PY-00012` to `APEX-MB-PY-00015`.
- `registry/muscle_compliance_check.py` now treats `<external>`, `N/A` session metadata, and known cross-project prefixes as external when the path is otherwise non-local.
- `docs/DOCUMENT_REGISTER.md` now includes `APEX-SYS-PY-00001` for `registry/muscle_compliance_check.py`.
- `hub/WO-APEX-ESTATE-CLEANUP-004.json` updated with the latest partial result.

## Deleted Or Reconciled

- Duplicate header ref `APEX-MB-PY-00015` reconciled.
- Eight header/register mismatches reconciled.
- Four missing external/session rows reconciled by external classification.
- Twenty-six SHEGOO stale path warnings reconciled by cross-project classification.

## Validation

Passed:

```powershell
python -m py_compile registry\muscle_classify_document.py registry\muscle_gdrive_download.py registry\muscle_gdrive_watcher.py registry\muscle_ocr_batch_retrieve.py registry\muscle_ocr_batch_submit.py registry\muscle_ocr_receipt.py registry\muscle_receipt_dedup.py registry\muscle_sheets_append.py
python registry\validate_tool_docs.py --quiet
python -m py_compile foreman.py registry\muscle_compliance_check.py registry\muscle_classify_document.py registry\muscle_gdrive_watcher.py registry\muscle_ocr_batch_retrieve.py registry\muscle_ocr_batch_submit.py registry\muscle_ocr_receipt.py registry\muscle_receipt_dedup.py registry\muscle_sheets_append.py
python registry\muscle_compliance_check.py
```

CLI help passed for:

- `muscle_gdrive_download.py`
- `muscle_gdrive_watcher.py`
- `muscle_ocr_batch_retrieve.py`
- `muscle_ocr_batch_submit.py`
- `muscle_ocr_receipt.py`
- `muscle_receipt_dedup.py`
- `muscle_sheets_append.py`

## Blockers

Phase F is blocked. `active_projects/bermcoin/.env` exists and contains real secret-bearing keys. Values were not printed or copied, but key names include Supabase, Stripe, Telegram, Brevo, Meta WhatsApp, exchange-rate API, and n8n API credentials. Do not rename, delete, commit, or rewrite history automatically. This needs an operator-approved secret handling plan.

Strict compliance remains blocked by accepted residual warnings: the eight legacy muscles are deliberately unapproved until live credential-backed fixtures are available, unregistered disk files include parallel Claude/audit material outside this commit, and Phase F still reports the real `.env` file.
