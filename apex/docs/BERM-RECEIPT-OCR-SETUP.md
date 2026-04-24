# BERM Receipt OCR Pipeline — Setup Guide

## Prerequisites

All Python deps already installed:
- `google-api-python-client` 2.147.0
- `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`
- `anthropic` 0.74.1
- `PyMuPDF` (fitz) 1.26.7

---

## Step 1: Google Service Account

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create or select a project
3. Enable these APIs:
   - **Google Drive API**
   - **Google Sheets API**
4. Go to **IAM & Admin → Service Accounts → Create**
   - Name: `receipt-ocr-sa`
5. Create key → JSON → download to:
   ```
   C:\Users\bermi\Projects\apex\credentials\google-sa-receipt.json
   ```
6. Share your receipt Drive folder with the service account email (Viewer)
7. Share your receipt Google Sheet with the service account email (Editor)

---

## Step 2: Create the Google Sheet

1. Create a new Google Sheet
2. Name it: **Receipt Ledger**
3. Note the spreadsheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
   ```
4. Leave it blank — `muscle_sheets_append` will create tabs and headers automatically

---

## Step 3: Create the Drive Inbox Folder

1. Create a folder in Google Drive: **Receipts/INBOX**
2. Get the folder ID from the URL:
   ```
   https://drive.google.com/drive/folders/FOLDER_ID_HERE
   ```
3. Share it with the service account (Viewer)

---

## Step 4: Config File

Create `C:\Users\bermi\Projects\apex\config\receipt_ocr.json`:

```json
{
  "google_credentials": "C:\\Users\\bermi\\Projects\\apex\\credentials\\google-sa-receipt.json",
  "anthropic_api_key_env": "ANTHROPIC_API_KEY",
  "drive_folder_id": "YOUR_FOLDER_ID_HERE",
  "spreadsheet_id": "YOUR_SPREADSHEET_ID_HERE",
  "state_file": "C:\\Users\\bermi\\Projects\\apex\\data\\receipt_watcher_state.json",
  "dedup_db": "C:\\Users\\bermi\\Projects\\apex\\data\\receipt_dedup.db",
  "ocr_output_dir": "C:\\Users\\bermi\\Projects\\apex\\data\\ocr_results"
}
```

---

## Step 5: n8n Workflow

Import `BERM_Receipt_OCR_Pipeline.json` into n8n at http://192.168.50.246:5678

Or configure manually with 8 nodes as per WO-BERM-RECEIPT-OCR-001.

---

## Manual Test Run

Test each muscle individually before running full pipeline:

### Test dedup (no credentials needed):
```bash
python muscle_receipt_dedup.py \
  --file-id TEST001 \
  --db-file C:/tmp/test_dedup.db \
  --action check
# Expected: {"status": "OK", "already_processed": false}
```

### Test watcher (needs credentials + folder ID):
```bash
python muscle_gdrive_watcher.py \
  --folder-id YOUR_FOLDER_ID \
  --state-file C:/tmp/watcher_state.json \
  --credentials path/to/google-sa-receipt.json
```

### Test OCR on a receipt (needs credentials + Anthropic key):
```bash
python muscle_ocr_receipt.py \
  --file-id DRIVE_FILE_ID_OF_RECEIPT \
  --image-url "https://drive.google.com/file/d/FILE_ID/view" \
  --credentials path/to/google-sa-receipt.json \
  --anthropic-key $ANTHROPIC_API_KEY \
  --output-file C:/tmp/ocr_result.json
cat C:/tmp/ocr_result.json
```

### Test sheets append:
```bash
# Create rows file first:
echo '[["REC-001","full_vat_invoice","2026-02-27T00:00:00Z","https://url","2026-02-27","Test Supplier","123 Test St","IE1234567T","INV-001","1","Widget A","2","10.00","23","4.60","24.60","20.00","4.60","24.60","EUR","","OK","high",""]]' > C:/tmp/test_rows.json

python muscle_sheets_append.py \
  --spreadsheet-id YOUR_SHEET_ID \
  --tab-name Receipts_2026 \
  --rows-file C:/tmp/test_rows.json \
  --credentials path/to/google-sa-receipt.json
```

---

## Sheet Columns (24 total)

| # | Column | Notes |
|---|--------|-------|
| 1 | receipt_id | UUID per receipt |
| 2 | receipt_type | full_vat_invoice / simplified |
| 3 | processed_at | ISO timestamp |
| 4 | image_url | Drive shareable link |
| 5 | invoice_date | YYYY-MM-DD |
| 6 | supplier_name | |
| 7 | supplier_address | |
| 8 | supplier_vat_reg_no | IE format |
| 9 | invoice_number | |
| 10 | line_no | 1,2,3... per receipt |
| 11 | line_description | |
| 12 | line_quantity | |
| 13 | line_unit_price_ex_vat | ex VAT |
| 14 | line_vat_rate_pct | 23 / 13.5 / 9 / 0 |
| 15 | line_vat_amount | |
| 16 | line_total_inc_vat | |
| 17 | subtotal_ex_vat | Repeated per line |
| 18 | total_vat | Repeated per line |
| 19 | total_inc_vat | Repeated per line |
| 20 | currency | EUR |
| 21 | category_hint | Empty, for manual tagging |
| 22 | status | OK / PARTIAL / ERROR |
| 23 | ocr_confidence | high / medium / low |
| 24 | notes | Missing fields or issues |

---

## Irish Revenue Compliance

- **Full VAT invoice** required when supply > €100 incl. VAT
- **Simplified invoice** acceptable below €100
- **Retention**: Keep originals (Drive) for 6 years (Revenue IT70)
- **VAT rates**: 23% standard, 13.5% reduced (building/hospitality), 9% tourism/media, 0% food/children's
- **VAT reg format**: IE followed by 8 characters

---

## Files Created

```
apex/registry/
  muscle_gdrive_watcher.py    APEX-MB-PY-00010
  muscle_gdrive_download.py   APEX-MB-PY-00014
  muscle_ocr_receipt.py       APEX-MB-PY-00011
  muscle_sheets_append.py     APEX-MB-PY-00012
  muscle_receipt_dedup.py     APEX-MB-PY-00013

apex/hub/
  WO-BERM-RECEIPT-OCR-001.json

apex/docs/
  BERM-RECEIPT-OCR-SETUP.md   (this file)
```
