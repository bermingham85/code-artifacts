# TROUBLESHOOT - muscle_sheets_append

| Symptom | Likely Cause | Fix |
|---|---|---|
| Permission denied | Sheet not shared with service account | Share the test/prod Sheet with the service account |
| Rows rejected | Rows file not a non-empty JSON array | Validate rows file before append |
| Header duplicated | Workflow wrote to a different tab or reset state | Check tab name and sheet contents before retry |
