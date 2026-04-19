# Receipt OCR Pipeline — Setup Guide
**Project:** BERM | **WO:** WO-BERM-RECEIPT-OCR-001 | **Date:** 2026-02-27

---

## What This Does

Watches a Google Drive folder every 5 minutes. Any receipt image or PDF dropped
in that folder gets OCR'd by Claude vision, and the extracted data (itemized per
line) is appended to a Google Sheet. Irish Revenue compliant fields. No
duplicates. Errors logged to a separate sheet tab.

---

## Step 1 — Google Cloud Setup (one-time)

### 1a. Create a Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create a new project: `bermech-receipts`
3. Enable these APIs:
   - Google Drive API
   - Google Sheets API

### 1b. Create a Service Account

1. IAM & Admin → Service Accounts → Create
2. Name: `receipt-ocr-bot`
3. Grant role: **Editor** (or create custom role with Drive read + Sheets write)
4. Create JSON key → download as `google_service_account.json`
5. Copy to: `C:\Users\bermi\Projects\apex\data\google_service_account.json`

### 1c. Share your Google Drive folder with the service account

1. Open Google Drive
2. Right-click your receipts folder → Share
3. Add the service account email (format: `receipt-ocr-bot@bermech-receipts.iam.gserviceaccount.com`)
4. Permission: **Viewer**
5. Note the folder ID from the URL (the long alphanumeric string after `/folders/`)

### 1d. Create the Google Sheet

1. Create a new Google Sheet: `Bermech Receipt Ledger`
2. Note the spreadsheet ID from the URL (between `/spreadsheets/d/` and `/edit`)
3. Share with the service account email → **Editor** permission

---

## Step 2 — Configure Environment

Create `C:\Users\bermi\Projects\apex\data\.env`:

```
RECEIPT_FOLDER_ID=<your-drive-folder-id>
RECEIPT_SHEET_ID=<your-spreadsheet-id>
ANTHROPIC_API_KEY=<your-anthropic-key>
```

Ensure the data directory exists:
```
mkdir C:\Users\bermi\Projects\apex\data
```

---

## Step 3 — Import the n8n Workflow

1. Open n8n: http://192.168.50.246:5678
2. Workflows → Import from file
3. Select: `C:\Users\bermi\Projects\apex\registry\n8n_receipt_ocr_pipeline.json`
4. Set environment variables in n8n:
   - Settings → Environment Variables
   - Add `RECEIPT_FOLDER_ID` and `RECEIPT_SHEET_ID` from your .env above
5. Activate the workflow

---

## Step 4 — Test Run

Drop a receipt photo or PDF into your watched Drive folder and wait up to 5
minutes (or manually trigger the workflow in n8n). Check the Google Sheet for
new rows.

For the full 8-test-case acceptance run, see the test plan in:
`C:\Users\bermi\Projects\apex\hub\WO-BERM-RECEIPT-OCR-001.json`

---

## Files Created

| File | Purpose |
|------|---------|
| `registry/muscle_gdrive_watcher.py` | Polls Drive folder for new files |
| `registry/muscle_gdrive_download.py` | Downloads a Drive file to local path |
| `registry/muscle_ocr_receipt.py` | Claude vision OCR → structured JSON |
| `registry/muscle_sheets_append.py` | Appends rows to Google Sheet |
| `registry/muscle_receipt_dedup.py` | SQLite dedup ledger |
| `registry/n8n_receipt_ocr_pipeline.json` | n8n workflow import file |
| `data/receipt_watcher_state.json` | Auto-created: tracks last poll timestamp |
| `data/receipt_dedup.db` | Auto-created: SQLite dedup store |

---

## Sheet Columns (24 total — one row per line item)

```
receipt_id | receipt_type | processed_at | image_url | invoice_date |
supplier_name | supplier_address | supplier_vat_reg_no | invoice_number |
line_no | line_description | line_quantity | line_unit_price_ex_vat |
line_vat_rate_pct | line_vat_amount | line_total_inc_vat |
subtotal_ex_vat | total_vat | total_inc_vat | currency |
category_hint | status | ocr_confidence | notes
```

---

## Irish Revenue Compliance

- Full VAT invoices: all mandatory fields per s.86 VAT Consolidation Act 2010
- Simplified receipts (< €100 incl. VAT): reduced field set, flagged as `receipt_type=simplified`
- Irish VAT rates handled: 23%, 13.5%, 9%, 0%
- Records should be retained 6 years minimum (Revenue eBrief 025/21)
- Currency defaults to EUR; multi-currency receipts will show explicit currency code

---

## Troubleshooting

**No rows appearing in sheet**
- Check n8n execution log for errors
- Verify service account has Editor on the Sheet and Viewer on the Drive folder
- Run watcher manually: `python muscle_gdrive_watcher.py --folder-id X --state-file test_state.json --credentials google_service_account.json`

**OCR returning null fields**
- Image quality too low → re-photograph with better lighting
- Check `ocr_confidence` column — `low` means partial extraction

**Duplicate check not working**
- The dedup DB is at `data/receipt_dedup.db` — do not delete it
- To reset (reprocess all): delete the DB file and reset `receipt_watcher_state.json`
