# GUIDANCE - muscle_replit_builder_packet

## CLI Usage

```bash
python registry/muscle_replit_builder_packet.py --instruction-file docs/spec/my_claude_build.md --mode create --project APEX
```

Inline instruction:

```bash
python registry/muscle_replit_builder_packet.py --instruction "Build a React dashboard for the Apex work order queue." --mode create
```

Foreman-compatible usage:

```bash
python registry/muscle_replit_builder_packet.py --task-folder active_projects/tasks/task_demo --input docs/spec/my_claude_build.md --mode create
```

## Recommended Claude Flow

1. Claude writes a precise build instruction or uses an existing WorkOrder.
2. Run this muscle to create a Replit packet.
3. Send `replit_prompt.md` to Replit Agent, or use an approved Replit connector that accepts natural-language prompts.
4. Replit builds the app or change.
5. Claude reviews the Replit result and sends the changed app through the existing Codex review gate before shipping.

## Prompt Rules

Every generated Replit prompt includes:

- "Use Perplexity Pro first for external research; keep web/source reads targeted."
- No real credentials or secrets.
- Build exactly what Claude requested.
- Return app URL, changed areas, run steps, tests, risks, and follow-up needs.

## Operational Notes

Use `--mode create` for a new Replit app, `--mode update` when Replit already has the app, and `--mode inspect` when asking Replit to explain current behavior without changing it.

The script intentionally creates a packet instead of trying to drive Replit through an undocumented local API. That keeps the workflow auditable and avoids storing Replit credentials in Apex.
