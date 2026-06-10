# BLUEPRINT - muscle_classify_document

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00015 |
| Tool | muscle_classify_document |
| File | `registry/muscle_classify_document.py` |
| Category | documents |
| Status | DRAFT - pending live credential test |

## Purpose

Classifies financial documents with Claude vision and extracts structured rows for receipt, invoice, bank statement, credit card statement, or other document handling.

## Inputs

- Google Drive file ID.
- Google service-account credentials.
- Anthropic API key or approved environment source.

## Outputs

- Structured document classification.
- Receipt/statement rows ready for `muscle_sheets_append`.

## Safety Boundary

Do not commit service-account files, API keys, downloaded documents, or extracted private financial data. Run only against files the user owns or is authorized to process.
