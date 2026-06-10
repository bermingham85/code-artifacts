"""
muscle_classify_document.py — Document Classification + Extraction Muscle
Ref:        APEX-MB-PY-00019
Version:    1.0
Author:     MB / SYS
Description: Uses Claude vision to classify any financial document type and extract
             all relevant data. Handles receipts, bank statements, credit card
             statements, invoices, and unknown documents.
             Returns (tab_name, rows) ready for muscle_sheets_append.
"""

import base64
import json
import os
import sys
from pathlib import Path

CLASSIFY_PROMPT = """You are a financial document classifier for an Irish sole trader business (Michael Bermingham).

Analyse this document and return ONLY valid JSON — no markdown, no commentary.

First identify the document type, then extract ALL relevant data.

=== DOCUMENT TYPES ===

For type "receipt" or "invoice":
{
  "doc_type": "receipt",
  "date": "YYYY-MM-DD or null",
  "supplier_name": "string or null",
  "supplier_address": "string or null",
  "supplier_vat_no": "IE... or null",
  "invoice_number": "string or null",
  "payment_method": "cash | card | contactless | bank_transfer | unknown",
  "card_last4": "last 4 digits if visible on receipt, else null",
  "category": "Office Supplies | Travel & Transport | Meals & Entertainment | Accommodation | Utilities | Software/Subscriptions | Professional Services | Equipment/Hardware | Marketing | Other",
  "vat_rate_pct": 23 or 13.5 or 9 or 0,
  "subtotal_ex_vat": number or null,
  "total_vat": number or null,
  "gross_amount": number or null,
  "currency": "EUR",
  "line_items": [
    {"description": "string", "qty": number or null, "unit_price": number or null, "vat_rate": number or null, "line_total": number or null}
  ],
  "notes": "any issues, warnings, or additional info"
}

For type "bank_statement":
{
  "doc_type": "bank_statement",
  "bank_name": "AIB | Bank of Ireland | Ulster Bank | KBC | Revolut | N26 | Monzo | Starling | PTSB | other",
  "account_name": "name on account",
  "account_number": "account number or last 4 digits",
  "iban": "IE... or null",
  "bic": "string or null",
  "sort_code": "XX-XX-XX or null",
  "statement_from": "YYYY-MM-DD",
  "statement_to": "YYYY-MM-DD",
  "opening_balance": number or null,
  "closing_balance": number or null,
  "currency": "EUR",
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "full description as printed",
      "debit": number or null,
      "credit": number or null,
      "balance": number or null,
      "type": "Direct Debit | Standing Order | POS | ATM | Transfer | Salary | Refund | Charge | Interest | Other",
      "reference": "string or null"
    }
  ]
}

For type "credit_card_statement":
{
  "doc_type": "credit_card_statement",
  "provider": "Visa | Mastercard | Amex | other",
  "bank_name": "AIB | Bank of Ireland | etc",
  "card_last4": "last 4 digits",
  "account_name": "name on account",
  "statement_from": "YYYY-MM-DD",
  "statement_to": "YYYY-MM-DD",
  "payment_due_date": "YYYY-MM-DD or null",
  "minimum_payment": number or null,
  "closing_balance": number or null,
  "credit_limit": number or null,
  "currency": "EUR",
  "transactions": [
    {
      "date": "YYYY-MM-DD",
      "description": "full description",
      "debit": number or null,
      "credit": number or null,
      "type": "Purchase | Cash Advance | Payment | Fee | Interest | Refund | Other",
      "reference": "string or null"
    }
  ]
}

For anything else (payslip, contract, letter, etc.):
{
  "doc_type": "other",
  "subtype": "payslip | contract | letter | utility_bill | tax_document | unknown",
  "description": "one-sentence description of what this document is",
  "date": "YYYY-MM-DD or null",
  "issuer": "who issued this",
  "notes": "any relevant details worth recording"
}

=== IRISH RULES ===
- VAT rates: 23% (standard), 13.5% (construction/fuel/hairdressing), 9% (hospitality/tourism), 0% (groceries/children's clothing)
- Full VAT invoice if supplier VAT reg present
- Simplified receipt if total < €100 or no VAT reg
- If you cannot read the document clearly, set doc_type to "other" with notes explaining

Return ONLY the JSON object. No preamble, no markdown fences."""


def _download_drive_file(file_id: str, credentials: str) -> tuple:
    """Download file from Drive. Returns (bytes, mime_type)."""
    import io
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload

    creds = service_account.Credentials.from_service_account_file(
        credentials,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )
    service = build("drive", "v3", credentials=creds, cache_discovery=False)

    meta = service.files().get(fileId=file_id, fields="mimeType",
                               supportsAllDrives=True).execute()
    mime = meta.get("mimeType", "application/octet-stream")

    if mime.startswith("application/vnd.google-apps."):
        request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
        mime = "application/pdf"
    else:
        request = service.files().get_media(fileId=file_id, supportsAllDrives=True)

    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue(), mime


def _to_image(raw: bytes, mime: str) -> tuple:
    """Convert to image bytes. Returns (image_bytes, media_type)."""
    if mime == "application/pdf":
        try:
            import fitz
            doc = fitz.open(stream=raw, filetype="pdf")
            pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
            return pix.tobytes("png"), "image/png"
        except ImportError:
            return raw, "application/pdf"
    if mime in ("image/jpeg", "image/jpg"):
        return raw, "image/jpeg"
    if mime == "image/webp":
        return raw, "image/webp"
    return raw, "image/png"


def classify_document(file_id: str, image_url: str, credentials: str,
                      anthropic_key: str) -> dict:
    """
    Classify and extract data from any financial document.
    Downloads from Drive, sends to Claude for classification.
    Returns structured dict with doc_type and all extracted fields.
    """
    import anthropic as sdk

    raw_bytes, mime = _download_drive_file(file_id, credentials)
    img_bytes, media_type = _to_image(raw_bytes, mime)

    b64 = base64.standard_b64encode(img_bytes).decode()

    client = sdk.Anthropic(api_key=anthropic_key)

    content = [
        {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
        {"type": "text", "text": CLASSIFY_PROMPT},
    ]

    # For PDFs that couldn't be converted to image
    if media_type == "application/pdf":
        content = [
            {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
            {"type": "text", "text": CLASSIFY_PROMPT},
        ]

    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": content}],
    )

    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    data = json.loads(raw)
    data["file_id"] = file_id
    data["image_url"] = image_url
    return data


# ── Row builders ─────────────────────────────────────────────────────────────

RECEIPT_HEADER = [
    "receipt_id", "receipt_type", "processed_at", "image_url",
    "invoice_date", "supplier_name", "supplier_address", "supplier_vat_reg_no",
    "invoice_number", "payment_method", "card_last4", "category",
    "line_no", "line_description", "line_qty", "line_unit_price",
    "line_vat_rate_pct", "line_total",
    "subtotal_ex_vat", "total_vat", "gross_amount", "currency",
    "status", "notes",
]

BANK_HEADER = [
    "file_id", "processed_at", "bank_name", "account_name", "account_number",
    "iban", "bic", "sort_code",
    "statement_from", "statement_to",
    "opening_balance", "closing_balance", "currency",
    "txn_date", "txn_description", "txn_debit", "txn_credit", "txn_balance",
    "txn_type", "txn_reference", "image_url",
]

OTHER_HEADER = [
    "file_id", "processed_at", "doc_type", "subtype",
    "date", "issuer", "description", "notes", "image_url",
]


def _g(d, *keys, default=""):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def build_rows(doc: dict, processed_at: str) -> tuple:
    """
    Convert classified doc to (tab_name, header, rows).
    For bank/credit card statements each transaction becomes a row.
    For receipts each line item becomes a row.
    """
    dt = doc.get("doc_type", "other")
    fid = doc.get("file_id", "")
    url = doc.get("image_url", "")

    if dt in ("receipt", "invoice"):
        lines = doc.get("line_items", []) or [{}]
        rows = []
        for i, line in enumerate(lines):
            rows.append([
                fid,
                dt,
                processed_at,
                url,
                _g(doc, "date"),
                _g(doc, "supplier_name"),
                _g(doc, "supplier_address"),
                _g(doc, "supplier_vat_no"),
                _g(doc, "invoice_number"),
                _g(doc, "payment_method"),
                _g(doc, "card_last4"),
                _g(doc, "category"),
                i + 1,
                _g(line, "description"),
                _g(line, "qty"),
                _g(line, "unit_price"),
                _g(line, "vat_rate"),
                _g(line, "line_total"),
                _g(doc, "subtotal_ex_vat"),
                _g(doc, "total_vat"),
                _g(doc, "gross_amount"),
                _g(doc, "currency", default="EUR"),
                "OK",
                _g(doc, "notes"),
            ])
        return "Receipts_2026", RECEIPT_HEADER, rows

    if dt in ("bank_statement", "credit_card_statement"):
        txns = doc.get("transactions", []) or [{}]
        tab = "Bank_Statements_2026" if dt == "bank_statement" else "Credit_Cards_2026"
        rows = []
        for txn in txns:
            rows.append([
                fid,
                processed_at,
                _g(doc, "bank_name", "provider"),
                _g(doc, "account_name"),
                _g(doc, "account_number", "card_last4"),
                _g(doc, "iban"),
                _g(doc, "bic"),
                _g(doc, "sort_code"),
                _g(doc, "statement_from"),
                _g(doc, "statement_to"),
                _g(doc, "opening_balance"),
                _g(doc, "closing_balance"),
                _g(doc, "currency", default="EUR"),
                _g(txn, "date"),
                _g(txn, "description"),
                _g(txn, "debit"),
                _g(txn, "credit"),
                _g(txn, "balance"),
                _g(txn, "type"),
                _g(txn, "reference"),
                url,
            ])
        return tab, BANK_HEADER, rows

    # Catch-all
    rows = [[
        fid,
        processed_at,
        dt,
        _g(doc, "subtype"),
        _g(doc, "date"),
        _g(doc, "issuer"),
        _g(doc, "description"),
        _g(doc, "notes"),
        url,
    ]]
    return "Other_2026", OTHER_HEADER, rows
