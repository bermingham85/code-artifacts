# GUIDANCE - muscle_gdrive_watcher

Use this tool as a polling fallback where webhooks are unavailable.

Local checks:

```powershell
python -m py_compile registry\muscle_gdrive_watcher.py
python registry\muscle_gdrive_watcher.py --help
```

Use a stable state file so repeat runs do not reprocess old files.
