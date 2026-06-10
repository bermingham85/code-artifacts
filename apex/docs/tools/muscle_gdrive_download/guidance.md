# GUIDANCE - muscle_gdrive_download

Use this tool when an automation needs a local copy of a specific Drive file.

Run syntax/help checks before live use:

```powershell
python -m py_compile registry\muscle_gdrive_download.py
python registry\muscle_gdrive_download.py --help
```

Live use requires a valid Google service-account JSON path and access to the target file.
