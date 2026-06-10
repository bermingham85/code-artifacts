# Replit Builder Bridge

> **Status: SUPERSEDED-BY-TOOL-DOCS (2026-05-30)** — The committed `muscle_replit_builder_packet` tool (APEX-MB-PY-00024) has full governed documentation under `docs/tools/muscle_replit_builder_packet/` (blueprint, guidance, test_record, troubleshoot — 213 lines total vs this file's 30). This single-file bridge note is kept as historical provenance only. Canonical references: `docs/tools/muscle_replit_builder_packet/guidance.md` for usage, `docs/APEX_TOOL_MENU.md` for selection.

`registry/muscle_replit_builder_packet.py` lets Apex treat Replit as the code builder while Claude stays responsible for planning, instruction quality, and post-build review.

## Workflow

1. Claude writes the build instruction.
2. Apex generates a Replit packet:

```bash
python registry/muscle_replit_builder_packet.py --instruction-file docs/spec/my_build.md --mode create --project APEX
```

3. Send the generated `replit_prompt.md` to Replit Agent or an approved Replit connector.
4. Replit builds the app/change.
5. Claude reviews the result and sends it through the Codex gate before shipping.

## Why It Uses Packets

The script does not store Replit credentials and does not assume a private Replit API. It produces a clean, auditable handoff that can be used manually or by any approved connector that accepts natural-language Replit instructions.

## Required Handoff Line

Every delegated prompt includes:

```text
Use Perplexity Pro first for external research; keep web/source reads targeted.
```

If Perplexity Pro is unavailable in the active stack, the builder should state that and use targeted primary-source research instead.
