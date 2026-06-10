# Apex Tool Menu Research - 2026-05-25

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00022 |
| Status | ACTIVE |
| Scope | Research on the Apex low-token tool menu, how-to docs, and editable troubleshooting logs |

## Research Routing Note

Perplexity Pro was requested by Apex governance as the preferred external research path, but it was not available in the active tool stack for this pass. Fallback used targeted web research with source links, prioritizing official/open-source documentation and using user-platform signals only for practical risk notes.

## Concept Tested

Apex concept:

- A low-token cover-page menu for tool selection.
- One approved tool row per capability with current state and exact call.
- Per-tool `guidance.md` for exact how-to.
- Per-tool `troubleshoot.md` as a version-controlled reusable fix log.
- Full specs loaded only after selection, not during boot.

## Comparable Open-Source Patterns

| Pattern | What it proves | Fit for Apex |
|---|---|---|
| Backstage Software Catalog + TechDocs | A central catalog plus docs-as-code is a mature developer-platform pattern. Backstage catalogs components from metadata files and TechDocs renders Markdown docs beside catalog entries. | Strong if Apex grows into a multi-user portal; heavy for current local-first needs. |
| MkDocs | Markdown docs with YAML navigation are simple, static, and searchable. Good match for repo-native docs. | Strong next step for a browser UI without custom app complexity. |
| Docusaurus | Open-source docs site with search, versioning, plugin system, and Markdown/MDX. | Good alternative if richer UI/versioned docs are required; heavier than MkDocs. |
| OpenAPI | Machine-readable API descriptions enable documentation, tooling, and automation from one contract. | Useful model for a future `tools.schema.json` / generated menu. |
| MCP | Standardizes tool/resource/prompt discovery for AI agents. | Strong future integration if Apex tools become MCP-callable. |
| Diataxis | Separates tutorials, how-to guides, reference, and explanation. | Validates Apex split: menu/reference, guidance/how-to, troubleshoot/fix log, spec/explanation. |
| llms.txt | Curated AI-facing indexes reduce discovery cost, but ecosystem adoption is mixed. | Useful low-cost addition as `llms.txt` or repo-root AI index, but should not replace `AGENTS.md`/`CLAUDE.md`. |

## Probability Of Success

Assumptions:

- The repo remains the source of truth.
- Tool docs are kept short and version-controlled.
- Future agents actually read `AGENTS.md`, `CLAUDE.md`, or `docs/APEX_CONTEXT_INDEX.md`.
- The menu is regenerated or manually kept in sync when tools change.

| Version | Probability | Reason |
|---|---:|---|
| Current implementation | 0.72 | Strong enough for local/future-context reuse, but manual sync can drift. |
| Add generated machine-readable menu + CI checks | 0.86 | Reduces drift by generating menu from manifest/docs and failing checks when docs are missing. |
| Add MkDocs static site with search | 0.88 | Better human usability while keeping repo-native docs; low operational complexity. |
| Move fully to Backstage now | 0.62 | Powerful but likely too heavy for current single-user/local-first Apex; maintenance burden may exceed value. |
| Backstage later after tool count/team size grows | 0.82 | Becomes attractive if Apex has many tools, owners, services, dashboards, and users. |

## Best Improvement Found

The best improvement is not a complete replacement. It is:

1. Keep the current Markdown cover-page menu.
2. Add a machine-readable `docs/APEX_TOOL_MENU.json`.
3. Generate `docs/APEX_TOOL_MENU.md` from that JSON plus `registry/manifest.json`.
4. Add a validation script that checks every approved tool has:
   - `blueprint.md`
   - `guidance.md`
   - `test_record.md`
   - `troubleshoot.md`
   - an approved row in `registry/TOOL_INDEX.md`
   - a document-register row
5. Optionally publish with MkDocs for human browsing and search.

This preserves the low-token agent workflow while reducing manual drift.

## Complete Alternative If Better

Alternative architecture: Backstage + TechDocs.

Use if Apex becomes a larger internal developer portal with multiple users, teams, owners, dashboards, deployment links, service status, and infrastructure metadata.

Why not now:

- Higher setup and maintenance cost.
- Requires a Node/React Backstage app.
- The current need is a lightweight local agent-facing tool catalog, not a full enterprise portal.

Recommended decision:

- Do not replace the Apex menu now.
- Add generated JSON + validation.
- Reconsider MkDocs when the menu passes 20 approved tools.
- Reconsider Backstage when Apex has multiple users or service ownership boundaries.

## Implementation Recommendation

Next Apex improvement packet:

| Task | Output |
|---|---|
| Add `docs/APEX_TOOL_MENU.schema.json` | Stable contract for tool menu entries |
| Add `docs/APEX_TOOL_MENU.json` | Machine-readable source for menu |
| Add `registry/generate_tool_menu.py` | Regenerates Markdown menu from manifest/docs |
| Add `registry/validate_tool_docs.py` | Fails if approved tools lack required docs/troubleshoot |
| Add optional `llms.txt` | AI-friendly root map for docs and tools |
| Later: add MkDocs | Searchable human UI |

## Sources

- Backstage overview: https://backstage.io/docs/overview/generated-index
- Backstage TechDocs: https://backstage.io/docs/techdocs/generated-index/
- Backstage component registration: https://backstage.io/docs/next/getting-started/register-a-component/
- MkDocs: https://www.mkdocs.org/
- Docusaurus docs: https://docusaurus.io/docs/
- OpenAPI overview: https://swagger.io/docs/specification/v3_0/about/
- Diataxis: https://diataxis.fr/
- Nix docs using Diataxis: https://nix.dev/contributing/documentation/diataxis.html
- X docs on `llms.txt`: https://docs.x.com/tools/llms-txt
- User-platform signal on Backstage complexity: https://www.reddit.com/r/devops/comments/1171it7/backstage_is_not_userfriendly_i_want_something/
