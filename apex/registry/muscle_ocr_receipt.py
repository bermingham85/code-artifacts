"""
muscle_ocr_receipt.py — Receipt OCR Muscle (Irish Revenue Compliant)
Ref:        APEX-MB-PY-00011
Version:    2.0
Author:     MB / SYS
Description: Two-tier OCR: Tesseract (free) first pass, Claude vision only when
             Tesseract confidence is below threshold. Reduces LLM costs significantly.
             Supports single mode (immediate) and batch-prep mode (for Anthropic Batch API).
             Handles JPEG, PNG, PDF (first page via PyMuPDF), WebP.
Inputs:     --file-id       DRIVE_FILE_ID    Google Drive file ID
            --image-url     URL              Drive shareable link (stored in output)
            --credentials   PATH             Service account JSON key file
            --anthropic-key KEY              Anthropic API key (or ANTHROPIC_API_KEY env)
            --output-file   PATH             Where to write structured JSON result
            --mode          single|batch-prep
                            single: process immediately (default)
                            batch-prep: write base64 payload to output-file for batch submission
            --tess-threshold FLOAT           Tesseract confidence threshold 0-100 (default 70)
                            If mean word confidence >= threshold, skip Claude entirely.
Outputs:    Prints {"status": "OK"|"PARTIAL"|"NOT_A_RECEIPT"|"ERROR"|"BATCH_READY", "output": PATH}
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
TESS_CONFIDENCE_THRESHOLD = 70  # skip Claude if Tesseract mean word conf >= this

EXTRACT_PROMPT = """You are an Irish Revenue-compliant receipt data extractor.

Analyse the receipt image and return ONLY valid JSON — no markdown, no commentary.

Schema:
{
  "receipt_type": "full_vat_invoice" | "simplified" | "not_a_receipt",
  "ocr_confidence": "high" | "medium" | "low",
  "invoice_date": "YYYY-MM-DD or null",
  "invoice_number": "string or null",
  "supplier_name": "string or null",
  "supplier_address": "string or null",
  "supplier_vat_reg_no": "IE... or null",
  "subtotal_ex_vat": number or null,
  "total_vat": number or null,
  "total_inc_vat": number or null,
  "currency": "EUR",
  "notes": "any issues or missing fields",
  "lines": [
    {
      "line_no": integer,
      "description": "string",
      "quantity": number or null,
      "unit_price_ex_vat": number or null,
      "vat_rate_pct": number or null,
      "vat_amount": number or null,
      "line_total_inc_vat": number or null
    }
  ]
}

Rules:
- receipt_type = "full_vat_invoice" if supplier VAT reg number is present
- receipt_type = "simplified" if total < 100 EUR or no VAT reg present but is clearly a receipt
- receipt_type = "not_a_receipt" if image is not a receipt at all
- Irish VAT rates: 23%, 13.5%, 9%, 0% — assign correct rate per line if visible
- If a field is not visible or illegible, use null — do not guess
- currency default is EUR unless another currency is explicitly shown
- lines must have at least one entry for a valid receipt
- If receipt_type is "not_a_receipt", lines may be empty []
"""

# --- Irish Revenue field extraction from Tesseract raw text ---
IE_VAT_RE = re.compile(r'\bIE\s*\d{7}[A-Z]{1,2}\b', re.IGNORECASE)
DATE_RE    = re.compile(r'\b(\d{1,2})[/\-\.](\d{1,2})[/\-\.](\d{2,4})\b')
TOTAL_RE   = re.compile(r'(?:total|amount\s+due|balance\s+due)[^\d]*(\d+[\.,]\d{2})', re.IGNORECASE)
VAT_RE     = re.compile(r'(?:vat|tax)[^\d]*(\d+[\.,]\d{2})', re.IGNORECASE)


def _build_drive_service(credentials_path: str):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _download_file(file_id: str, credentials: str) -> tuple:
    """Download file bytes, return (bytes, mime_type)."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    service = _build_drive_service(credentials)
    meta = service.files().get(fileId=file_id, fields="mimeType",
                               supportsAllDrives=True).execute()
    mime = meta.get("mimeType", "application/octet-stream")
    if mime.startswith("application/vnd.google-apps."):
        request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
        mime = "application/pdf"
    else:
        request = service.files().get_media(fileId=file_id)
    buf = io.BytesIO()
    dl = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = dl.next_chunk()
    return buf.getvalue(), mime


def _pdf_first_page_to_png(pdf_bytes: bytes) -> bytes:
    import fitz
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.0, 2.0))
    return pix.tobytes("png")


def _to_image_bytes(raw: bytes, mime: str) -> tuple:
    """Return (image_bytes, media_type) ready for base64 or Tesseract."""
    if mime == "application/pdf":
        return _pdf_first_page_to_png(raw), "image/png"
    if mime in ("image/jpeg", "image/jpg"):
        return raw, "image/jpeg"
    if mime == "image/webp":
        return raw, "image/webp"
    return raw, "image/png"


# ---------------------------------------------------------------------------
# TIER 1 — Tesseract (free)
# ---------------------------------------------------------------------------

def _tesseract_ocr(img_bytes: bytes) -> tuple:
    """
    Run Tesseract on image bytes.
    Returns (text: str, mean_confidence: float).
    """
    import io
    import pytesseract
    from PIL import Image

    img = Image.open(io.BytesIO(img_bytes))
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    confs = [c for c in data["conf"] if isinstance(c, (int, float)) and c >= 0]
    mean_conf = sum(confs) / len(confs) if confs else 0.0
    text = pytesseract.image_to_string(img)
    return text, mean_conf


def _parse_tesseract_text(text: str, file_id: str, image_url: str) -> dict:
    """
    Best-effort structured extraction from raw Tesseract text.
    Returns a partial receipt dict — good enough for clear receipts.
    """
    vat_match = IE_VAT_RE.search(text)
    date_match = DATE_RE.search(text)
    total_match = TOTAL_RE.search(text)
    vat_amount_match = VAT_RE.search(text)

    invoice_date = None
    if date_match:
        d, m, y = date_match.groups()
        y = y if len(y) == 4 else f"20{y}"
        invoice_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"

    total = None
    if total_match:
        try:
            total = float(total_match.group(1).replace(",", "."))
        except ValueError:
            pass

    vat_amount = None
    if vat_amount_match:
        try:
            vat_amount = float(vat_amount_match.group(1).replace(",", "."))
        except ValueError:
            pass

    lines_raw = [l.strip() for l in text.split("\n") if l.strip() and len(l.strip()) > 3]
    supplier_name = lines_raw[0] if lines_raw else None

    receipt_type = "full_vat_invoice" if vat_match else "simplified"

    return {
        "receipt_type": receipt_type,
        "ocr_confidence": "high",  # Tesseract path = we had good confidence
        "ocr_engine": "tesseract",
        "invoice_date": invoice_date,
        "invoice_number": None,
        "supplier_name": supplier_name,
        "supplier_address": None,
        "supplier_vat_reg_no": vat_match.group(0).upper().replace(" ", "") if vat_match else None,
        "subtotal_ex_vat": round(total - vat_amount, 2) if total and vat_amount else None,
        "total_vat": vat_amount,
        "total_inc_vat": total,
        "currency": "EUR",
        "notes": "Extracted by Tesseract (free tier). Line items not itemized — Claude not called.",
        "lines": [{"line_no": 1, "description": "See image — Tesseract pass, not itemized",
                   "quantity": None, "unit_price_ex_vat": None,
                   "vat_rate_pct": None, "vat_amount": None, "line_total_inc_vat": total}],
        "image_url": image_url,
        "file_id": file_id,
        "status": "OK",
    }


# ---------------------------------------------------------------------------
# TIER 2 — Claude vision (paid, fallback)
# ---------------------------------------------------------------------------

def _claude_ocr(img_bytes: bytes, media_type: str, api_key: str,
                file_id: str, image_url: str) -> dict:
    import anthropic as sdk
    client = sdk.Anthropic(api_key=api_key)
    b64 = base64.standard_b64encode(img_bytes).decode()
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",   # cheapest capable vision model
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64",
                                             "media_type": media_type, "data": b64}},
                {"type": "text", "text": EXTRACT_PROMPT},
            ],
        }],
    )
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    data = json.loads(raw)
    data["ocr_engine"] = "claude-haiku"
    data["image_url"] = image_url
    data["file_id"] = file_id
    receipt_type = data.get("receipt_type", "")
    if receipt_type == "not_a_receipt":
        data["status"] = "NOT_A_RECEIPT"
    elif data.get("ocr_confidence") == "low" or not data.get("lines"):
        data["status"] = "PARTIAL"
    else:
        data["status"] = "OK"
    return data


# ---------------------------------------------------------------------------
# Main muscle function
# ---------------------------------------------------------------------------

def muscle_ocr_receipt(file_id: str, image_url: str, credentials: str,
                       anthropic_key: str, output_file: str,
                       mode: str = "single",
                       tess_threshold: float = TESS_CONFIDENCE_THRESHOLD) -> dict:
    """
    Two-tier OCR: Tesseract free first, Claude only if confidence < threshold.
    mode=batch-prep: writes base64 payload for Anthropic Batch API submission.
    """
    out = Path(output_file)
    out.parent.mkdir(parents=True, exist_ok=True)

    raw_bytes, mime = _download_file(file_id, credentials)
    img_bytes, media_type = _to_image_bytes(raw_bytes, mime)

    if mode == "batch-prep":
        # Write payload for batch submission — no API call at all
        payload = {
            "file_id": file_id,
            "image_url": image_url,
            "media_type": media_type,
            "b64": base64.standard_b64encode(img_bytes).decode(),
        }
        out.write_text(json.dumps(payload))
        return {"status": "BATCH_READY", "output": str(out)}

    # --- Tier 1: Tesseract ---
    try:
        tess_text, mean_conf = _tesseract_ocr(img_bytes)
        if mean_conf >= tess_threshold and len(tess_text.strip()) > 20:
            data = _parse_tesseract_text(tess_text, file_id, image_url)
            data["tess_confidence"] = round(mean_conf, 1)
            out.write_text(json.dumps(data, indent=2))
            return {"status": data["status"], "output": str(out), "engine": "tesseract"}
    except Exception as tess_err:
        mean_conf = 0.0
        tess_text = ""

    # --- Tier 2: Claude (only reached if Tesseract confidence low) ---
    if not anthropic_key:
        result = {"status": "ERROR", "error": "Tesseract confidence too low and no Anthropic key",
                  "tess_confidence": round(mean_conf, 1), "file_id": file_id}
        out.write_text(json.dumps(result, indent=2))
        return {"status": "ERROR", "output": str(out)}

    try:
        data = _claude_ocr(img_bytes, media_type, anthropic_key, file_id, image_url)
        data["tess_confidence"] = round(mean_conf, 1)
        out.write_text(json.dumps(data, indent=2))
        return {"status": data["status"], "output": str(out), "engine": "claude-haiku"}
    except json.JSONDecodeError as e:
        result = {"status": "ERROR", "error": f"Claude returned non-JSON: {e}",
                  "file_id": file_id, "image_url": image_url}
        out.write_text(json.dumps(result, indent=2))
        return {"status": "ERROR", "output": str(out)}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: two-tier receipt OCR")
    parser.add_argument("--file-id",        required=True)
    parser.add_argument("--image-url",      required=True)
    parser.add_argument("--credentials",    required=True)
    parser.add_argument("--anthropic-key",  default="")
    parser.add_argument("--output-file",    required=True)
    parser.add_argument("--mode",           default="single", choices=["single", "batch-prep"])
    parser.add_argument("--tess-threshold", type=float, default=TESS_CONFIDENCE_THRESHOLD)
    parser.add_argument("--task-folder",    default="")
    args = parser.parse_args()

    api_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")

    try:
        result = muscle_ocr_receipt(
            args.file_id, args.image_url, args.credentials,
            api_key, args.output_file, args.mode, args.tess_threshold,
        )
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e),
                          "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
