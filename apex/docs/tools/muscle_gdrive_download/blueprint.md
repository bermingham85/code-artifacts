# BLUEPRINT - muscle_gdrive_download

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00014 |
| Tool | muscle_gdrive_download |
| File | `registry/muscle_gdrive_download.py` |
| Category | files |
| Status | DRAFT - pending live Google Drive test |

## Purpose

Downloads one Google Drive file to a local path. Google Workspace documents are exported as PDF.

## Exact Call

```powershell
python registry\muscle_gdrive_download.py --file-id DRIVE_FILE_ID --output-path audit\downloads\file.pdf --credentials C:\path\service_account.json
```

## Safety Boundary

Credentials must stay outside the repo. Download only user-owned or authorized files.
