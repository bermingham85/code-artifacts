# SP-A.0 preflight inventory — authority chain

The 9 files listed in `apex_governance/cc_runbook/00_KICKOFF.md` Step 1, each loaded and verified during SP-A.0 preflight. SHAs are full SHA-256 (64 hex chars). Sizes in bytes. Last-modified is the filesystem mtime captured at preflight; immutable for cert audit.

| # | Path | SHA-256 | Size | Last-modified (UTC) | Role |
|---|---|---|---|---|---|
| 1 | `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.md` | `a2e8b707e2e1d6d92265f95f7e0a26c909a5881ef02ed13b7e700ff1da70f6fb` | 6799 | 2026-05-03T21:21:30Z | Binding doctrine prose, DRAFT v0.1 |
| 2 | `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.rules.json` | `eaa1ccc47e25ded1a2ff3af57c14316330feaeedffc889949869cca89bd689bc` | 8232 | 2026-05-03T21:22:05Z | Machine-checkable rule IDs (P/S/D/PT/O/E/A/C), DRAFT v0.1 |
| 3 | `apex/docs/doctrine/conformance-checklist.md` | `5d3ac9940dc1d85e230a72d297bc76336a5a850a3e1598fa8231d223c6dc835a` | 2070 | 2026-05-03T21:22:17Z | Per-cert conformance table template |
| 4 | `apex_governance/PLAN_CRITERIA.md` | `7714b61061db0b6ed63a007999d8169002e1b35095982f0d34fe51bd6e36a6d2` | 18587 | 2026-05-03T22:50:46Z | Authority hierarchy, micro-phase lifecycle, DoDs, cleanup, tempo |
| 5 | `apex_governance/SUBPROJECTS.md` | `6eeec0cb67402422b5f4c9dee81c125310f56d9896538647b8d541699522c409` | 9274 | 2026-05-03T22:51:08Z | SP-A…SP-J + dependency graph |
| 6 | `apex_governance/PHASE_TEMPLATE.md` | `e86bd63f104c7f0331225307993f0da386055dcf98cb6e744f656357add30bbc` | 5173 | 2026-05-03T22:50:03Z | Per-phase form-fill template |
| 7 | `apex_governance/PROMPT_APEX_INGEST_PIPELINE.md` | `e3624eaa9b8b3625b6278a17421980f7ef59a6e2496b176cb2a6decdf3a577f1` | 29217 | 2026-05-03T22:50:38Z | Operational prompt for the orchestrator-engineer |
| 8 | `apex/PROJECT_APEX_v2.2.md` | `a06005aec7ff7e1f04471703b1ceb1a3113515792d7cc15e1809dc1493cc2325` | 44878 | 2026-02-27T09:12:43Z | Programme-wide hardened build spec; feature reference for SP-F/G/H/J |
| 9 | `apex/hub/WO-BERM-RECEIPT-OCR-001.json` | `7251fed586125338083b3e9793941c34410efee137bea44bbb0419ece12d58a2` | 11764 | 2026-02-27T12:41:38Z | Worked-example WO for SP-F (receipts ledger) |

**Hash algorithm and method (canonical for SP-A.0 and downstream phases):** SHA-256 over raw byte content with no normalisation. Full 64-hex digest stored above; the cert evidence ledger references these full values for audit. Reference implementation:
```python
import hashlib
hashlib.sha256(open(path, "rb").read()).hexdigest()
```
The re-pin check uses the same method so a hash mismatch unambiguously means the file content changed, not the hashing tool. **Do not truncate the digest** for re-pin comparison — the full 64-hex value is the authoritative comparison.

All 9 files were loaded into the orchestrator's working context during SP-A.0; the SHAs above are the source-of-truth for the cert evidence row "every input file inventoried with SHA". Any future divergence (file rewritten, doctrine locked at v1.0, etc.) requires a fresh SHA capture in the receiving phase's preflight.
