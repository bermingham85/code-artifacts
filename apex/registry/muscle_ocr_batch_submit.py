"""
muscle_ocr_batch_submit.py — Anthropic Batch API Receipt Submitter
Ref:        APEX-MB-PY-00017
Version:    1.0
Author:     MB / SYS
Description: Takes a folder of batch-prep payloads (from muscle_ocr_receipt --mode batch-prep)
             and submits them all as a single Anthropic Message Batch.
             50% cheaper than individual API calls. Results available within 24h.
             Writes a batch manifest JSON for retrieval by muscle_ocr_batch_retrieve.
Inputs:     --payloads-dir  PATH    Folder of *.json batch-prep payload files
            --anthropic-key KEY     Anthropic API key (or ANTHROPIC_API_KEY env)
            --manifest-file PATH    Where to write the batch manifest (batch_id + file mappings)
Outputs:    Prints {"status": "OK", "batch_id": ID, "count": N, "output": manifest_path}
"""

import argparse
import json
import os
import sys
from pathlib import Path


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
- receipt_type = "simplified" if total < 100 EUR or no VAT reg present but clearly a receipt
- receipt_type = "not_a_receipt" if image is not a receipt at all
- Irish VAT rates: 23%, 13.5%, 9%, 0%
- Null for missing/illegible fields
- currency default EUR
"""


def muscle_ocr_batch_submit(payloads_dir: str, anthropic_key: str, manifest_file: str) -> dict:
    """
    Submit all batch-prep payloads in payloads_dir as one Anthropic Message Batch.
    Returns {"status": "OK", "batch_id": str, "count": int, "output": manifest_file}.
    """
    import anthropic as sdk

    payloads_path = Path(payloads_dir)
    payload_files = sorted(payloads_path.glob("*.json"))

    if not payload_files:
        return {"status": "ERROR", "error": f"No payload files found in {payloads_dir}"}

    client = sdk.Anthropic(api_key=anthropic_key)

    requests = []
    file_map = {}  # custom_id → {file_id, image_url, payload_file}

    for pf in payload_files:
        payload = json.loads(pf.read_text())
        custom_id = f"receipt-{payload['file_id']}"
        requests.append(
            sdk.types.MessageBatchRequestParam(
                custom_id=custom_id,
                params=sdk.types.MessageCreateParamsNonStreaming(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=2048,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": payload["media_type"],
                                    "data": payload["b64"],
                                },
                            },
                            {"type": "text", "text": EXTRACT_PROMPT},
                        ],
                    }],
                ),
            )
        )
        file_map[custom_id] = {
            "file_id": payload["file_id"],
            "image_url": payload["image_url"],
            "payload_file": str(pf),
        }

    batch = client.messages.batches.create(requests=requests)

    manifest = {
        "batch_id": batch.id,
        "status": batch.processing_status,
        "submitted_at": str(batch.created_at),
        "count": len(requests),
        "file_map": file_map,
    }

    manifest_path = Path(manifest_file)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return {
        "status": "OK",
        "batch_id": batch.id,
        "count": len(requests),
        "output": str(manifest_path),
    }


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: submit receipt batch to Anthropic")
    parser.add_argument("--payloads-dir",  required=True)
    parser.add_argument("--anthropic-key", default="")
    parser.add_argument("--manifest-file", required=True)
    parser.add_argument("--task-folder",   default="")
    args = parser.parse_args()

    api_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(json.dumps({"status": "ERROR", "error": "No Anthropic API key"}))
        sys.exit(1)

    try:
        result = muscle_ocr_batch_submit(args.payloads_dir, api_key, args.manifest_file)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e),
                          "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
