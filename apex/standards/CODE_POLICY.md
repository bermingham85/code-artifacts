# Code Policy — How to Read Any Apex Microprompter Code

Version: 1.0 — 2026-05-29

This document explains every code system used by Apex Microprompter in plain English. If you see a code anywhere in a file, register, output, or log, look it up here.

## The headline format

`{prompt}.{phase}.{micro}` — e.g. `1001.4.3` means:
- **1001** — the project (prompt number 1001)
- **4** — phase 4 of that project (BUILD)
- **3** — the third micro-prompt within phase 4

If you see extra letters like `1001.4.3.A`, that's an **emergent** micro-prompt — work discovered during execution that the original plan didn't include.

## Phase numbers

| # | Name | What happens |
|---|---|---|
| 0 | REUSE | Check if this has been done before |
| 1 | RESEARCH | Gather context |
| 2 | FOUNDATION | Set up the scaffolding |
| 3 | DESIGN | Decide the architecture |
| 4 | BUILD | Implement |
| 5 | INTEGRATION | Wire it into the rest of the stack |
| 6 | VALIDATION | Test it |
| 7 | DEPLOYMENT | Push it to production |
| 8 | HANDOVER | Document and hand off |

## Looking up any code

Three ways:

1. **Web**: `http://100.93.145.25:8766/d/{code}` (Tailscale only)
2. **Telegram**: send `/decode {code}` to `@LisaLookupBot`
3. **Phone camera**: scan the QR code printed on the output

All three return the same card explaining: what the code is, what it does, when it was made, by which LLM, where the output lives, and what it builds on.

## See also

- `NAMING_AUTHORITY.md` — the full naming rules
- `APEX-MICROPROMPTER-SPEC.md` — the full system specification
