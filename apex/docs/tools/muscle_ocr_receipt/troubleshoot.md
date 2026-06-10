# TROUBLESHOOT - muscle_ocr_receipt

| Symptom | Likely Cause | Fix |
|---|---|---|
| OCR dependency error | Tesseract, PIL, or PyMuPDF missing | Install approved worker dependencies |
| Drive download fails | Bad file ID or permissions | Verify service account access |
| Claude fallback fails | API key/quota issue | Stop and request credential/billing resolution |
| Sensitive OCR in logs | Raw text was logged | Redact and move evidence to approved private storage |
