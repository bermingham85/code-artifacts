"""
muscle_ocr_batch_retrieve.py — Anthropic Batch API Result Retriever
Ref:        APEX-MB-PY-00018
Version:    1.0
Author:     MB / SYS
Description: Polls an Anthropic Message Batch for completion.
             When ready, parses all results, writes per-receipt JSON files,
             and returns a summary for the n8n sheets-append node.
             Run hourly by n8n until batch is ended.
Inputs:     --manifest-file PATH    Batch manifest from muscle_ocr_batch_submit
            --output-dir    PATH    Where to write per-receipt result JSONs
            --anthropic-key KEY     Anthropic API key (or ANTHROPIC_API_KEY env)
Outputs:    Prints {"status": "PENDING"|"OK"|"ERROR",
                    "batch_id": ID, "processed": N, "results_dir": PATH}
            status=PENDING means batch not done yet — retry later.
            status=OK means all results written to output-dir.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def _clean_json(raw: str) -> dict:
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    return json.loads(raw)


def muscle_ocr_batch_retrieve(manifest_file: str, output_dir: str, anthropic_key: str) -> dict:
    """
    Check batch status. If ended, write per-receipt JSON results.
    Returns {"status": "PENDING"|"OK"|"ERROR", ...}.
    """
    import anthropic as sdk

    manifest_path = Path(manifest_file)
    if not manifest_path.exists():
        return {"status": "ERROR", "error": f"Manifest not found: {manifest_file}"}

    manifest = json.loads(manifest_path.read_text())
    batch_id = manifest["batch_id"]
    file_map = manifest["file_map"]

    client = sdk.Anthropic(api_key=anthropic_key)
    batch = client.messages.batches.retrieve(batch_id)

    if batch.processing_status != "ended":
        return {
            "status": "PENDING",
            "batch_id": batch_id,
            "processing_status": batch.processing_status,
            "request_counts": {
                "processing": batch.request_counts.processing,
                "succeeded": batch.request_counts.succeeded,
                "errored": batch.request_counts.errored,
                "canceled": batch.request_counts.canceled,
                "expired": batch.request_counts.expired,
            },
        }

    # Batch complete — process results
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    processed = 0
    errors = 0
    result_files = []

    for result in client.messages.batches.results(batch_id):
        custom_id = result.custom_id
        entry = file_map.get(custom_id, {})
        file_id = entry.get("file_id", custom_id)
        image_url = entry.get("image_url", "")

        out_file = out_dir / f"ocr_result_{file_id}.json"

        if result.result.type == "succeeded":
            raw_text = result.result.message.content[0].text.strip()
            try:
                data = _clean_json(raw_text)
                data["ocr_engine"] = "claude-haiku-batch"
                data["image_url"] = image_url
                data["file_id"] = file_id
                receipt_type = data.get("receipt_type", "")
                if receipt_type == "not_a_receipt":
                    data["status"] = "NOT_A_RECEIPT"
                elif data.get("ocr_confidence") == "low" or not data.get("lines"):
                    data["status"] = "PARTIAL"
                else:
                    data["status"] = "OK"
                processed += 1
            except (json.JSONDecodeError, KeyError) as e:
                data = {"status": "ERROR", "error": f"Parse failed: {e}",
                        "raw": raw_text[:300], "file_id": file_id, "image_url": image_url}
                errors += 1
        else:
            data = {"status": "ERROR", "error": str(result.result.type),
                    "file_id": file_id, "image_url": image_url}
            errors += 1

        out_file.write_text(json.dumps(data, indent=2))
        result_files.append(str(out_file))

    # Update manifest status
    manifest["retrieved_at"] = str(__import__("datetime").datetime.utcnow())
    manifest["processed"] = processed
    manifest["errors"] = errors
    manifest_path.write_text(json.dumps(manifest, indent=2))

    return {
        "status": "OK",
        "batch_id": batch_id,
        "processed": processed,
        "errors": errors,
        "results_dir": str(out_dir),
        "result_files": result_files,
    }


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: retrieve Anthropic batch results")
    parser.add_argument("--manifest-file", required=True)
    parser.add_argument("--output-dir",    required=True)
    parser.add_argument("--anthropic-key", default="")
    parser.add_argument("--task-folder",   default="")
    args = parser.parse_args()

    api_key = args.anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(json.dumps({"status": "ERROR", "error": "No Anthropic API key"}))
        sys.exit(1)

    try:
        result = muscle_ocr_batch_retrieve(args.manifest_file, args.output_dir, api_key)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e),
                          "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
