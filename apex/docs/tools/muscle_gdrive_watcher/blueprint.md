# BLUEPRINT - muscle_gdrive_watcher

| Field | Value |
|---|---|
| Ref Code | APEX-MB-PY-00010 |
| Tool | muscle_gdrive_watcher |
| File | `registry/muscle_gdrive_watcher.py` |
| Category | files |
| Status | DRAFT - pending live Google Drive test |

## Purpose

Polls a Google Drive folder for files created since the last run and writes a local state file plus `gdrive_new_files.json`.

## Exact Call

```powershell
python registry\muscle_gdrive_watcher.py --folder-id DRIVE_FOLDER_ID --state-file audit\gdrive\state.json --credentials C:\path\service_account.json
```

## Safety Boundary

Use a dedicated state path per folder. Do not store service-account JSON in the repo.
