# GUIDANCE - muscle_classify_document

Use this tool when a financial document needs classification before ledger routing.

Typical use is through an orchestrated workflow, not direct manual CLI use. Keep credentials outside the repo and pass only approved file IDs.

Minimum local checks:

```powershell
python -m py_compile registry\muscle_classify_document.py
```

Live use requires:

- Google Drive read access.
- Anthropic API access.
- A non-sensitive test document.
