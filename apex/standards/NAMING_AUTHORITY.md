# Naming Authority

Version: 1.0 — 2026-05-29

Machine-readable twin: `naming_authority.json` (same folder).
HTTP endpoint: `http://100.93.145.25:8767/naming` (once Naming Authority service is built — prompt 1000).

This document is the single source of truth for every naming convention used by Apex Microprompter. Every LLM, every script, and every human must read this before naming anything.

## Prompt codes

Format: `{prompt}.{phase}.{micro}[.{letter}...]`

- Prompt numbers start at 1000.
- Phase numbers are 0–8 (see SPEC section 5.2).
- Letter extensions denote emergent prompts discovered during execution: `1001.4.3.A`.
- Codes are immutable. Never renumber.

## File names

`{prompt_code}_{slug}.{ext}` — e.g. `1001.4.3_receipt_schema.sql`

Slug rules:
- Lowercase, underscores only, 3–40 chars.
- Derived deterministically from the project fingerprint.
- Banned words **in the slug**: `temp`, `test`, `new`, `final`.

## Archive file names

`{prompt_code}_{slug}_v{N}.{ext}` — e.g. `1001.4.3_receipt_schema_v1.sql`

The `_v{N}` suffix is **not** a slug; the slug ban does not apply to it.

## Project folders

`{prompt_number}_{slug}` — e.g. `1001_ocr_receipt_extractor`

## Phase folders

`{0-8}_{NAME}` — e.g. `0_REUSE`, `4_BUILD`, `8_HANDOVER`

## APEX register codes (existing, preserved)

`[PROJECT]-[ORIG]-[TYPE]-[SEQ5]` — e.g. `CRIC-MICH-MUSC-00001`

## Supabase tables

`{schema}.{table}` — e.g. `microprompter.prompt_tasks`

## n8n workflows

`Microprompter-{Title Case}` — e.g. `Microprompter-Master Watcher`

## Git branches

`{type}/{prompt_number}-{kebab-description}` — e.g. `feat/1001-receipt-schema`

Types: `feat`, `fix`, `chore`, `docs`.

## Evolution

Every change to these rules is a PR to `code-artifacts/standards/naming_authority.json`. Version bumps on every accepted change. Old outputs keep their original `naming_authority_version` stamp; they were correct under that version.
