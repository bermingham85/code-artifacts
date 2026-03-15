# Skill: suno-bulk-rename

## Purpose
Bulk rename songs in Suno workspaces using Claude-in-Chrome JavaScript injection against
the Suno internal API. Does NOT use UI clicking — uses direct API calls injected via
the browser extension's javascript_tool.

## Trigger Phrases
- "rename my suno songs"
- "bulk rename suno"
- "organise suno files"
- "sort suno workspace"
- "rename tracks in suno"

## Prerequisites
- Claude-in-Chrome extension active and connected
- User logged into Suno in Chrome
- Target workspace ID known

## Known Workspace IDs
| Workspace | ID |
|---|---|
| Jesse in Oz | `027faff0-1afc-4424-92ab-acd81334fcc6` |

## API Endpoints (injected via javascript_tool)

### Fetch all songs (paginated)
```
POST https://studio-api.prod.suno.com/api/feed/v3
Body: { page_size: 50, project_id: WID, cursor: "..." }
```
**CRITICAL:** This endpoint does NOT filter by project_id server-side.
Always filter client-side: `songs.filter(s => s.project?.id === WID)`

Use cursor-based pagination — loop until no `next_cursor` returned.

### Rename a song
```
POST https://studio-api.prod.suno.com/api/gen/{song_id}/set_metadata/
Body: { title: "New Name" }
```
Note: `/api/clip/set_metadata/` returns 405 — do NOT use that path.

## JavaScript Execution Pattern

Use `.then()` chains with named recursive functions — NOT async/await IIFEs.
Async/await IIFEs fail silently after extension disconnects.

```javascript
// Safe pattern
window._renameIdx = 0;
window._renameDone = false;
var songs = [...]; // populated from feed fetch

function renameNext() {
  if (window._renameIdx >= songs.length) {
    window._renameDone = true;
    return;
  }
  var s = songs[window._renameIdx];
  fetch('https://studio-api.prod.suno.com/api/gen/' + s.id + '/set_metadata/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({title: s.newTitle})
  }).then(function() {
    window._renameIdx++;
    setTimeout(renameNext, 400); // rate limit: ~400ms between calls
  });
}
renameNext();
```

Window variables (`window._renameDone`, `window._renameIdx`) persist in the tab
even after extension disconnects — use them to check progress on reconnect.

## Naming Logic

For songs with lyrics: derive title from first distinctive lyric line.
For pure instrumentals (no lyric text): leave as-is, they cannot be renamed meaningfully.

Check for duplicate songs (same lyrics, different names) — consolidate before renaming.
Example: "she matters", "Down By The River", "Fabuloso" were all the same song —
confirmed by searching for a unique word ("fabuloso") within the lyrics.

## Rate Limiting
400ms between rename calls is safe. Faster will get rate-limited.

## Liked Songs (different endpoint)
```
GET https://studio-api.prod.suno.com/api/feed/v2?page=0&page_size=50
```
Uses page-number pagination with query params (not cursor-based).

## Skill ZIP Format for claude.ai upload
If uploading as a skill to claude.ai:
- ZIP must contain folder: `suno-bulk-rename/SKILL.md`
- YAML description field must NOT contain unescaped quotes
- Upload the ZIP, not the bare .md file

## Status
- Originally built and fully tested: 2026-03-11
- Confirmed working on: Jesse in Oz workspace (578 songs), Brilliant workspace (114 songs)
- Recovered and committed to code-artifacts: 2026-03-15
- Last known issue: extension disconnect mid-run on "Decommissioned Nets" batch (resume via window._renameIdx check)
