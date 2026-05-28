# TROUBLESHOOT - muscle_ocr_batch_retrieve

| Symptom | Likely Cause | Fix |
|---|---|---|
| Manifest not found | Wrong path or submit step failed | Use the manifest emitted by submit |
| Status remains PENDING | Batch not ended | Retry on schedule |
| Parse failed | Model returned invalid JSON | Preserve private raw evidence and rerun or repair manually |
