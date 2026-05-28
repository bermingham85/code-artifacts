# TROUBLESHOOT - muscle_receipt_dedup

| Symptom | Likely Cause | Fix |
|---|---|---|
| Duplicate still processed | `mark` was not called after append | Mark only after successful downstream completion |
| SQLite file locked | Concurrent workflow access | Serialize receipt jobs or use a queue |
| Wrong already_processed value | Different db-file path used | Use one canonical ledger path per workflow |
