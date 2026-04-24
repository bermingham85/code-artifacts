"""
receipt_ocr_api.py — Local HTTP API wrapping Receipt OCR muscles
Port: 5691
Run: python receipt_ocr_api.py

Endpoints:
  POST /drive/files       List new files in watched Drive folder
  POST /dedup/check       Check if file already processed
  POST /dedup/mark        Mark file as processed
  POST /ocr               OCR a Drive file → structured JSON
  POST /sheets/append     Append rows to Google Sheet
  POST /batch/trigger     Manually trigger a batch run
  GET  /batch/status      Last batch run result

Background: Scans Drive every 5 mins, classifies all new docs, routes to correct
            sheet tab (Receipts_2026 / Bank_Statements_2026 / Credit_Cards_2026 / Other_2026).
            Deduplication prevents double-processing.
"""

import json
import os
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request

sys.path.insert(0, str(Path(__file__).parent))

from muscle_gdrive_watcher    import muscle_gdrive_watcher
from muscle_ocr_receipt       import muscle_ocr_receipt
from muscle_sheets_append     import muscle_sheets_append
from muscle_receipt_dedup     import muscle_receipt_dedup_check, muscle_receipt_dedup_mark
from muscle_classify_document import classify_document, build_rows

app = Flask(__name__)

CREDS      = r"C:\Users\bermi\Projects\apex\data\google_service_account.json"
STATE_FILE = r"C:\Users\bermi\Projects\apex\data\receipt_watcher_state.json"
DEDUP_DB   = r"C:\Users\bermi\Projects\apex\data\receipt_dedup.db"
OCR_DIR    = r"C:\Users\bermi\Projects\apex\data"
SHEET_ID   = "11zzWGWM4oiOPt2_er2xS-gjEiiXKaUmFaMbgDEfOhK4"
FOLDER_ID  = "1f4IBmSK42rfgKUbnG_SIDxE5bsyJB6CW"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

BATCH_INTERVAL_SECS = 300   # 5 minutes

# Shared state for last batch result
_batch_lock   = threading.Lock()
_last_batch   = {"status": "never_run", "ran_at": None, "results": []}


# ── Core: process one file ────────────────────────────────────────────────────

def _now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_rows_direct(tab_name: str, header: list, rows: list):
    """Write rows to Google Sheets, creating tab + header if needed."""
    import tempfile as _tf
    rows_file = _tf.NamedTemporaryFile(mode="w", suffix=".json",
                                       delete=False, encoding="utf-8")
    json.dump(rows, rows_file)
    rows_file_path = rows_file.name
    rows_file.close()

    # Temporarily override SHEET_HEADER in muscle_sheets_append for non-receipt tabs
    import muscle_sheets_append as msa
    original_header = msa.SHEET_HEADER
    msa.SHEET_HEADER = header
    try:
        result = muscle_sheets_append(SHEET_ID, tab_name, rows_file_path, CREDS)
    finally:
        msa.SHEET_HEADER = original_header
        Path(rows_file_path).unlink(missing_ok=True)
    return result


def process_single_file(file_info: dict) -> dict:
    """
    Full pipeline for one Drive file:
    1. Dedup check
    2. Classify + extract (Claude)
    3. Append to correct sheet tab
    4. Mark as processed
    """
    file_id  = file_info["id"]
    filename = file_info.get("name", file_id)
    image_url = file_info.get("webViewLink", "")

    # 1. Skip if already processed
    dedup = muscle_receipt_dedup_check(file_id, DEDUP_DB)
    if dedup.get("already_processed"):
        return {"status": "SKIPPED", "file_id": file_id, "name": filename,
                "reason": "already_processed"}

    if not ANTHROPIC_KEY:
        return {"status": "ERROR", "file_id": file_id, "name": filename,
                "error": "ANTHROPIC_API_KEY not set"}

    # 2. Classify + extract
    doc = classify_document(file_id, image_url, CREDS, ANTHROPIC_KEY)
    doc_type = doc.get("doc_type", "other")

    # 3. Build sheet rows and append
    tab_name, header, rows = build_rows(doc, _now_iso())
    if rows:
        _append_rows_direct(tab_name, header, rows)

    # 4. Mark as processed
    muscle_receipt_dedup_mark(file_id, DEDUP_DB, receipt_id=file_id)

    return {
        "status": "OK",
        "file_id": file_id,
        "name": filename,
        "doc_type": doc_type,
        "tab": tab_name,
        "rows_written": len(rows),
    }


# ── Batch runner ──────────────────────────────────────────────────────────────

def run_batch() -> dict:
    """
    Scan Drive for new files, process all of them.
    Returns summary dict.
    """
    global _last_batch

    try:
        watch_result = muscle_gdrive_watcher(FOLDER_ID, STATE_FILE, CREDS)
        new_files = watch_result.get("new_files", [])
    except Exception as e:
        result = {"status": "ERROR", "ran_at": _now_iso(),
                  "error": f"Drive scan failed: {e}", "results": []}
        with _batch_lock:
            _last_batch = result
        return result

    results = []
    for file_info in new_files:
        try:
            r = process_single_file(file_info)
        except Exception as e:
            r = {"status": "ERROR", "file_id": file_info.get("id"),
                 "name": file_info.get("name"), "error": str(e)}
        results.append(r)
        app.logger.info("Batch file: %s", r)

    summary = {
        "status": "OK",
        "ran_at": _now_iso(),
        "files_found": len(new_files),
        "processed": sum(1 for r in results if r["status"] == "OK"),
        "skipped":   sum(1 for r in results if r["status"] == "SKIPPED"),
        "errors":    sum(1 for r in results if r["status"] == "ERROR"),
        "results": results,
    }
    with _batch_lock:
        _last_batch = summary

    app.logger.info("Batch complete: found=%d processed=%d skipped=%d errors=%d",
                    summary["files_found"], summary["processed"],
                    summary["skipped"], summary["errors"])
    return summary


def _scheduler_loop():
    """Background thread: run batch every 5 minutes."""
    app.logger.info("Batch scheduler started — interval %ds", BATCH_INTERVAL_SECS)
    while True:
        try:
            run_batch()
        except Exception as e:
            app.logger.error("Batch scheduler error: %s", e)
        time.sleep(BATCH_INTERVAL_SECS)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "OK", "service": "receipt-ocr-api"})


@app.route("/drive/files", methods=["POST"])
def drive_files():
    """List new files in the watched Drive folder since last run."""
    try:
        result = muscle_gdrive_watcher(FOLDER_ID, STATE_FILE, CREDS)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500


@app.route("/dedup/check", methods=["POST"])
def dedup_check():
    """Body: {"file_id": "..."}"""
    body = request.get_json() or {}
    file_id = body.get("file_id", "")
    if not file_id:
        return jsonify({"status": "ERROR", "error": "file_id required"}), 400
    try:
        return jsonify(muscle_receipt_dedup_check(file_id, DEDUP_DB))
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500


@app.route("/dedup/mark", methods=["POST"])
def dedup_mark():
    """Body: {"file_id": "...", "receipt_id": "..."}"""
    body = request.get_json() or {}
    file_id    = body.get("file_id", "")
    receipt_id = body.get("receipt_id", "")
    if not file_id:
        return jsonify({"status": "ERROR", "error": "file_id required"}), 400
    try:
        return jsonify(muscle_receipt_dedup_mark(file_id, DEDUP_DB, receipt_id))
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500


@app.route("/ocr", methods=["POST"])
def ocr():
    """
    Body: {"file_id": "...", "image_url": "...", "mode": "single"}
    Returns structured receipt JSON.
    """
    body = request.get_json() or {}
    file_id   = body.get("file_id", "")
    image_url = body.get("image_url", "")
    mode      = body.get("mode", "single")

    if not file_id:
        return jsonify({"status": "ERROR", "error": "file_id required"}), 400

    out_file = str(Path(OCR_DIR) / f"ocr_result_{file_id}.json")
    try:
        meta = muscle_ocr_receipt(
            file_id, image_url, CREDS, ANTHROPIC_KEY, out_file, mode
        )
        # Also return the extracted data inline
        if Path(out_file).exists():
            data = json.loads(Path(out_file).read_text(encoding="utf-8"))
            meta["data"] = data
        return jsonify(meta)
    except Exception as e:
        import traceback
        return jsonify({"status": "ERROR", "error": str(e),
                        "traceback": traceback.format_exc()}), 500


@app.route("/sheets/append", methods=["POST"])
def sheets_append():
    """
    Body: {"tab_name": "Receipts_2026", "rows": [[...], ...]}
    """
    body     = request.get_json() or {}
    tab_name = body.get("tab_name", "Receipts_2026")
    rows     = body.get("rows", [])

    if not rows:
        return jsonify({"status": "ERROR", "error": "rows required"}), 400

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                    delete=False, encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=True)
        rows_file = f.name
    try:
        result = muscle_sheets_append(SHEET_ID, tab_name, rows_file, CREDS)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "ERROR", "error": str(e)}), 500
    finally:
        Path(rows_file).unlink(missing_ok=True)


@app.route("/drive/upload", methods=["POST"])
def drive_upload():
    """
    Upload a file to the watched Drive folder.
    Accepts multipart/form-data with field 'file', OR JSON body with
    {"filename": "...", "mimeType": "...", "data": "<base64>"}.
    Returns {"status": "OK", "file_id": ID, "name": NAME, "webViewLink": URL}
    """
    import io, base64
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload

    # Support both multipart and JSON (base64) formats
    if request.is_json:
        body = request.get_json() or {}
        filename   = body.get("filename") or "receipt.jpg"
        mime       = body.get("mimeType") or "image/jpeg"
        file_bytes = base64.b64decode(body.get("data", ""))
    elif "file" in request.files:
        uploaded   = request.files["file"]
        filename   = request.form.get("filename") or uploaded.filename or "receipt.jpg"
        mime       = uploaded.content_type or "image/jpeg"
        file_bytes = uploaded.read()
    else:
        return jsonify({"status": "ERROR", "error": "No file field in request"}), 400

    try:
        creds = service_account.Credentials.from_service_account_file(
            CREDS,
            scopes=["https://www.googleapis.com/auth/drive.file"]
        )
        service = build("drive", "v3", credentials=creds, cache_discovery=False)

        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime, resumable=False)
        meta = {"name": filename, "parents": [FOLDER_ID]}

        created = service.files().create(
            body=meta,
            media_body=media,
            fields="id,name,webViewLink",
            supportsAllDrives=True
        ).execute()

        return jsonify({
            "status": "OK",
            "file_id": created["id"],
            "name": created["name"],
            "webViewLink": created.get("webViewLink", ""),
        })
    except Exception as e:
        import traceback
        return jsonify({"status": "ERROR", "error": str(e),
                        "traceback": traceback.format_exc()}), 500


@app.route("/batch/trigger", methods=["POST"])
def batch_trigger():
    """Manually trigger a batch scan + process run."""
    def _run():
        run_batch()
    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"status": "OK", "message": "Batch triggered — check /batch/status"})


@app.route("/batch/status", methods=["GET"])
def batch_status():
    """Return the result of the last batch run."""
    with _batch_lock:
        return jsonify(_last_batch)


if __name__ == "__main__":
    print("Receipt OCR API starting on http://localhost:5691")
    print(f"Batch scheduler: every {BATCH_INTERVAL_SECS}s — routes receipts, bank statements, etc.")

    # Start background batch scheduler
    t = threading.Thread(target=_scheduler_loop, daemon=True)
    t.start()

    app.run(host="0.0.0.0", port=5691, debug=False)
