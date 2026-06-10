# APEX Transaction Model — The Three-Rung Ladder

**Ref:** APEX-MB-DOC-00002
**Version:** 1.0
**Author:** MB / SYS
**Status:** APPROVED — GOVERNING STANDARD

---

## Overview

Every unit of work in Apex follows exactly one transaction model. No exceptions.
Brian uses this model for every muscle call. The Postman coordinates every step.

```
ORIGINATOR (Brian / Michael / another muscle)
    │
    │  drops WorkOrder.json → hub/
    ▼
┌─────────────────────────────────────────────────────────┐
│  RUNG 1 — POSTMAN INBOUND                               │
│  n8n Blind Postman polls hub/ → detects new ticket      │
│  → hands to Foreman                                     │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  RUNG 2 — MUSCLE EXECUTES                               │
│  Foreman runs the muscle (Python script)                │
│  Muscle writes output + returns compact JSON result     │
│  Result format: {"status":"OK","output":"...","summary":"one-liner"} │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  RUNG 3 — QA GATE (two questions)                       │
│                                                         │
│  Q1 COMPLETENESS: Is all required output present?       │
│     → FILE_EXISTS / SIZE_GT_ZERO / JSON_VALID           │
│     If NO → FAIL, send DiagnosticTicket, stop           │
│                                                         │
│  Q2 SPEC COMPLIANCE: Is it the RIGHT output?            │
│     → SPEC_MATCH: does output meet what was asked for?  │
│     → Checks a field, value, or string against the spec │
│     If NO → FAIL, hand back for retry                   │
│     If YES → PASS                                       │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  RUNG 4 — POSTMAN OUTBOUND (close the loop)             │
│  Foreman writes compact CompletionReport to audit/      │
│  Postman detects COMPLETE state → notifies originator   │
│  Brian receives: job_id + result + one-line summary     │
│  Work is done, quality-checked, closed.                 │
└─────────────────────────────────────────────────────────┘
```

---

## The WorkOrder — Request Ticket

Every transaction starts with a WorkOrder. **Nothing runs without one.**

```json
{
  "meta": {
    "job_id":          "uuid-v4",
    "ref_code":        "APEX-SYS-WF-00000",
    "created_at":      "ISO-8601",
    "sender":          "brian | human | job_id_of_parent",
    "receiver":        "foreman",
    "project":         "APEX | CLAW | BERM | JESS | TALE | BALP",
    "priority":        "NORMAL | HIGH | LOW",
    "retry_count":     0,
    "max_retries":     3
  },
  "sop": {
    "action":          "muscle_name",
    "inputs":          ["optional/input/path.txt"],
    "parameters":      {},
    "timeout_seconds": 300
  },
  "qa_gate": {
    "rule": "MULTI",
    "checks": [
      {
        "rule":    "FILE_EXISTS | SIZE_GT_ZERO | JSON_VALID",
        "target":  "path/to/expected/output"
      },
      {
        "rule":             "SPEC_MATCH",
        "target":           "path/to/output.json",
        "expected_field":   "status",
        "expected_value":   "OK"
      }
    ]
  }
}
```

**Rules:**
- `sender` = who dropped this ticket (Brian uses her own ID or "brian")
- `qa_gate` must have at least one completeness check (Q1) and one spec check (Q2) for non-trivial muscles
- If `qa_gate.checks` is empty → defaults to FILE_EXISTS on the muscle's output log (not recommended)

---

## The CompletionReport — What Comes Back

Every finished job writes a compact CompletionReport. **Not a data dump — a signal.**

```json
{
  "job_id":          "uuid-v4",
  "action":          "muscle_name",
  "project":         "APEX",
  "sender":          "brian",
  "result":          "PASS | FAIL",
  "qa_checks": [
    {"rule": "FILE_EXISTS",  "result": "PASS"},
    {"rule": "SPEC_MATCH",   "result": "PASS"}
  ],
  "output_summary":  "one-line description of what was produced",
  "output_path":     "path/to/output/file (if applicable)",
  "duration_seconds": 2.3,
  "timestamp":       "ISO-8601"
}
```

**Rules:**
- `output_summary` must be one sentence or less — the WHAT, not the HOW
- `output_path` is optional — only include if there's a file to reference
- Never dump raw muscle output into the report — extract the summary field only
- This file is written to `audit/YYYY-MM-DD/task_{job_id}/CompletionReport.json`

---

## The QA Gate — Two Questions

### Q1: Completeness (Is it all there?)

| Rule | What it checks |
|------|----------------|
| `FILE_EXISTS` | Output file exists at target path |
| `SIZE_GT_ZERO` | Output file size > 0 bytes |
| `JSON_VALID` | Output file is valid parseable JSON |
| `CONTAINS_STRING` | Output file contains a specific string |

### Q2: Spec Compliance (Is it the right thing?)

| Rule | What it checks |
|------|----------------|
| `SPEC_MATCH` | A specific JSON field in the output equals an expected value |
| `SPEC_FIELD_EXISTS` | A specific JSON field is present (any value) |
| `SPEC_STATUS_OK` | Output JSON `status` field equals `"OK"` (shorthand) |

**The distinction is critical:**
- Q1 answers: *"Did the muscle produce something?"*
- Q2 answers: *"Did the muscle produce what was asked for?"*

Both must PASS before the Postman closes the loop.

---

## QA Failure Handling

```
FAIL Q1 (missing output)
  → severity: ERROR
  → no retry (muscle didn't produce anything — likely a bug)
  → DiagnosticTicket written → hub/
  → Postman notifies Brian: job_id + what failed + why

FAIL Q2 (wrong output)
  → severity: WARN
  → retry if retry_count < max_retries
  → DiagnosticTicket written with qa_reason
  → Postman notifies Brian after max retries exhausted

PASS both
  → CompletionReport written → audit/
  → state = COMPLETE
  → Postman notifies originator: PASS + output_summary
```

---

## Brian's Role in This Model

Brian is both originator and receiver.

**As originator (dropping a ticket):**
1. Identify the right muscle from TOOL_INDEX.md
2. Build a valid WorkOrder with Q1 + Q2 qa_gate checks
3. Drop via `muscle_drop_ticket` or `/ticket` command
4. Wait for CompletionReport (Postman notifies via Telegram or check `/apex`)

**As receiver (reading results):**
- Read CompletionReport `output_summary` — that's all that matters
- `result: "PASS"` → proceed with next step
- `result: "FAIL"` → read `qa_checks` to see which gate failed
- Never dig into raw muscle output unless debugging

---

## Adding a New Muscle (Checklist)

Every new muscle must support this transaction model:

```
□ stdout returns compact JSON: {"status":"OK","output":"...","summary":"one-liner"}
□ stderr reserved for errors only (never mixed with stdout)
□ Exit code 0 on success, non-zero on failure
□ Blueprint lists what qa_gate checks to use (Q1 + Q2)
□ test_record includes QA gate verification test case
□ Docstring includes: Outputs: {"status":"OK","output":"PATH","summary":"TEXT"}
```
