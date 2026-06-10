"""
muscle_receipt_dedup.py — Receipt Deduplication Ledger Muscle
Ref:        APEX-MB-PY-00020
Version:    1.0
Author:     MB / SYS
Description: Check or mark a Google Drive file ID in a local SQLite dedup ledger.
             Prevents the same receipt being processed and appended twice.
Inputs:     --file-id    DRIVE_FILE_ID   Google Drive file ID to check or mark
            --db-file    PATH            SQLite database file path
            --action     check|mark      check: returns already_processed flag
                                         mark:  inserts record as processed
            --receipt-id STRING          Receipt ID to store (only used with mark)
Outputs:    Prints {"status": "OK", "already_processed": bool} on check.
            Prints {"status": "OK", "output": db_file} on mark.
"""

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path


def _ensure_db(db_file: str) -> sqlite3.Connection:
    db_path = Path(db_file)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS processed_receipts (
            file_id      TEXT PRIMARY KEY,
            receipt_id   TEXT,
            processed_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def muscle_receipt_dedup_check(file_id: str, db_file: str) -> dict:
    """
    Check if file_id has already been processed.
    Returns {"status": "OK", "already_processed": True|False}.
    """
    conn = _ensure_db(db_file)
    try:
        row = conn.execute(
            "SELECT file_id FROM processed_receipts WHERE file_id = ?", (file_id,)
        ).fetchone()
        return {"status": "OK", "already_processed": row is not None}
    finally:
        conn.close()


def muscle_receipt_dedup_mark(file_id: str, db_file: str, receipt_id: str = "") -> dict:
    """
    Mark file_id as processed.
    Returns {"status": "OK", "output": db_file}.
    """
    conn = _ensure_db(db_file)
    try:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn.execute(
            """
            INSERT OR REPLACE INTO processed_receipts (file_id, receipt_id, processed_at)
            VALUES (?, ?, ?)
            """,
            (file_id, receipt_id, now),
        )
        conn.commit()
        return {"status": "OK", "output": str(Path(db_file).resolve())}
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: receipt deduplication ledger")
    parser.add_argument("--file-id",    required=True,  help="Google Drive file ID")
    parser.add_argument("--db-file",    required=True,  help="SQLite database path")
    parser.add_argument("--action",     required=True,  choices=["check", "mark"], help="check or mark")
    parser.add_argument("--receipt-id", required=False, default="", help="Receipt ID (used with mark)")
    parser.add_argument("--task-folder",default="",     help="Foreman task folder (unused)")
    args = parser.parse_args()

    try:
        if args.action == "check":
            result = muscle_receipt_dedup_check(args.file_id, args.db_file)
        else:
            result = muscle_receipt_dedup_mark(args.file_id, args.db_file, args.receipt_id)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
