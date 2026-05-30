# SPEC-SP-A.0a — Authority-chain inventory (SHA-pinned)

- **Identity**: Phase `SP-A.0a` (parent SP-A; depends-on none; blocks SP-A.1+; branch `phase/A-0a`).
- **Inputs** (9, pinned by absolute path; SHAs in the inventory file): `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.md`, `apex/docs/doctrine/CLAUDE_CODEX_DOCTRINE.rules.json`, `apex/docs/doctrine/conformance-checklist.md`, `apex_governance/PLAN_CRITERIA.md`, `apex_governance/SUBPROJECTS.md`, `apex_governance/PHASE_TEMPLATE.md`, `apex_governance/PROMPT_APEX_INGEST_PIPELINE.md`, `apex/PROJECT_APEX_v2.2.md`, `apex/hub/WO-BERM-RECEIPT-OCR-001.json`. Roots: `C:\Users\Owner\Repos\code-artifacts\` and `C:\Users\Owner\`.
- **Output**: `apex/docs/spec/SPEC-SP-A.0a.preflight-inventory.md` — full SHA-256 (64 hex over raw bytes), size in bytes, last-modified as UTC ISO-8601 to second precision, and a free-form short role description (one line, human-readable; not a machine-parseable taxonomy) per file.
- **DoD**: all 9 SHAs captured in the inventory; **at cert mint** the inventory is verified by re-hashing each input and comparing to the captured digest. **On any mismatch**: abort cert mint, drop incident WO `WO-APEX-SP-A.0a-DRIFT-001`, regenerate the inventory against the new content, restart the SP-A.0a lifecycle from scratch (per R2 in `apex/docs/policy/SP-A.0b-policy-contributions.md`); **never** mint the cert against a stale inventory.

Operational policy (locking, drift, rescue, deferral, paper-primary exemption, etc.) lives in `apex/docs/policy/SP-A.0b-policy-contributions.md` and feeds SP-A.2; not in scope here.
