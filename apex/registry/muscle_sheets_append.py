"""
muscle_sheets_append.py — Google Sheets Row Appender Muscle
Ref:        APEX-MB-PY-00015
Version:    1.0
Author:     MB / SYS
Description: Append one or more rows to a named Google Sheet tab.
             Auto-creates the tab if it does not exist.
             Writes header row on first use of a new tab.
             Designed for the Receipt Ledger schema.
Inputs:     --spreadsheet-id  ID      Google Sheets spreadsheet ID
            --tab-name        NAME    Sheet tab name (e.g. Receipts_2026)
            --rows-file       PATH    JSON file containing array of row arrays
            --credentials     PATH    Service account JSON key file
Outputs:    Prints {"status": "OK", "output": RANGE, "rows_written": N} on success.
"""

import argparse
import json
import sys
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Canonical header — matches WO-BERM-RECEIPT-OCR-001 sheet schema
SHEET_HEADER = [
    "receipt_id",
    "receipt_type",
    "processed_at",
    "image_url",
    "invoice_date",
    "supplier_name",
    "supplier_address",
    "supplier_vat_reg_no",
    "invoice_number",
    "line_no",
    "line_description",
    "line_quantity",
    "line_unit_price_ex_vat",
    "line_vat_rate_pct",
    "line_vat_amount",
    "line_total_inc_vat",
    "subtotal_ex_vat",
    "total_vat",
    "total_inc_vat",
    "currency",
    "category_hint",
    "status",
    "ocr_confidence",
    "notes",
]


def _build_service(credentials_path: str):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds, cache_discovery=False)


def _get_sheet_ids(service, spreadsheet_id: str) -> dict:
    """Return {tab_name: sheetId} for all existing tabs."""
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {s["properties"]["title"]: s["properties"]["sheetId"] for s in meta["sheets"]}


def _create_tab(service, spreadsheet_id: str, tab_name: str):
    """Add a new sheet tab."""
    body = {"requests": [{"addSheet": {"properties": {"title": tab_name}}}]}
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()


def _tab_is_empty(service, spreadsheet_id: str, tab_name: str) -> bool:
    """Return True if the tab has no data yet."""
    range_name = f"'{tab_name}'!A1"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
    )
    return "values" not in result


def muscle_sheets_append(
    spreadsheet_id: str, tab_name: str, rows_file: str, credentials: str
) -> dict:
    """
    Append rows from rows_file JSON array to the named tab.
    Creates tab + writes header if tab is new.
    Returns {"status": "OK", "output": range_written, "rows_written": N}.
    """
    rows_path = Path(rows_file)
    if not rows_path.exists():
        raise FileNotFoundError(f"rows-file not found: {rows_file}")

    rows = json.loads(rows_path.read_text())
    if not isinstance(rows, list) or not rows:
        raise ValueError("rows-file must contain a non-empty JSON array")

    service = _build_service(credentials)
    existing_tabs = _get_sheet_ids(service, spreadsheet_id)

    if tab_name not in existing_tabs:
        _create_tab(service, spreadsheet_id, tab_name)
        is_new = True
    else:
        is_new = _tab_is_empty(service, spreadsheet_id, tab_name)

    values_to_append = []
    if is_new:
        values_to_append.append(SHEET_HEADER)

    values_to_append.extend(rows)

    range_name = f"'{tab_name}'!A1"
    body = {"values": values_to_append}

    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body,
        )
        .execute()
    )

    updated_range = result.get("updates", {}).get("updatedRange", range_name)
    rows_written = len(rows)

    return {
        "status": "OK",
        "output": updated_range,
        "rows_written": rows_written,
        "header_written": is_new,
    }


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: append rows to Google Sheet")
    parser.add_argument("--spreadsheet-id", required=True, help="Google Sheets spreadsheet ID")
    parser.add_argument("--tab-name",        required=True, help="Sheet tab name e.g. Receipts_2026")
    parser.add_argument("--rows-file",       required=True, help="JSON file with array of row arrays")
    parser.add_argument("--credentials",     required=True, help="Service account JSON key file")
    parser.add_argument("--task-folder",     default="",    help="Foreman task folder (unused)")
    args = parser.parse_args()

    try:
        result = muscle_sheets_append(
            args.spreadsheet_id, args.tab_name, args.rows_file, args.credentials
        )
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
