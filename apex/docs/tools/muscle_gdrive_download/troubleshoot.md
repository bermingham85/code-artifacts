# TROUBLESHOOT - muscle_gdrive_download

| Symptom | Likely Cause | Fix |
|---|---|---|
| Credentials file error | Bad path or invalid service account | Use an approved external credentials path |
| 404 or permission error | File not shared with service account | Grant read access or use the correct file ID |
| Workspace doc has wrong extension | Export converted it to PDF | Use the returned `output` path, not the requested extension |
