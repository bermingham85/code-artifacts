# TROUBLESHOOT - muscle_classify_document

| Symptom | Likely Cause | Fix |
|---|---|---|
| Import error for Google or Anthropic packages | Runtime dependencies missing | Install approved dependencies in the worker environment |
| Permission denied on Drive file | Service account lacks access | Share the file/folder with the service account |
| JSON parse failure from model output | Model returned non-JSON text | Retry with stricter prompt and save raw response as private evidence only |
| Private data appears in logs | Workflow logged document contents | Stop, redact logs, and move evidence to approved private storage |
