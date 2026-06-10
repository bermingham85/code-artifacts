# TEST RECORD - muscle_replit_builder_packet

| Field | Value |
|-------|-------|
| **Tool** | muscle_replit_builder_packet |
| **Ref Code** | APEX-MB-PY-00024 |
| **Date** | 2026-05-23 |
| **Tester** | Codex |
| **Approved** | YES - 2026-05-23 |

## Tests

| Test | Command | Expected | Result |
|------|---------|----------|--------|
| Syntax check | `python -m py_compile registry/muscle_replit_builder_packet.py` | No syntax errors | PASS |
| Inline packet | `python registry/muscle_replit_builder_packet.py --instruction "Build a small Apex queue dashboard." --out-dir C:/tmp/apex_replit_packet_test` | JSON stdout with `status=OK`; prompt and manifest written | PASS |
| Missing instruction | `python registry/muscle_replit_builder_packet.py --out-dir C:/tmp/apex_replit_packet_test` | JSON stdout with `status=ERROR` | PASS |

## Notes

This test record covers packet generation and CLI failure behavior. It does not verify Replit build quality because that depends on an external Replit Agent run.
