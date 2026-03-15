# Skill: suno-bulk-rename

## Purpose
Bulk rename songs in Suno workspaces using Claude-in-Chrome browser automation.
Handles full rename workflows across one or multiple Suno workspaces without manual UI interaction.

## Trigger Phrases
- "rename my suno songs"
- "bulk rename suno"
- "organise suno files"
- "sort suno workspace"
- "rename tracks in suno"

## Prerequisites
- Claude-in-Chrome extension active and connected
- Logged into Suno in the Chrome browser
- Target workspace ID known (Jesse in Oz: `027faff0-1afc-4424-92ab-acd81334fcc6`)

## Known Workspace IDs
| Workspace | ID |
|---|---|
| Jesse in Oz | `027faff0-1afc-4424-92ab-acd81334fcc6` |

## Workflow

### Step 1 - Navigate to workspace
```
Navigate to: https://suno.com/library
Switch to target workspace if needed via workspace selector
```

### Step 2 - Collect song list
Use `get_page_text` or `read_page` to extract all visible song titles and their DOM element references.
Scroll to load all songs (Suno uses infinite scroll - scroll to bottom, wait, repeat until no new items load).

### Step 3 - Build rename map
Ask user to provide naming convention OR infer from existing titles.
Common conventions:
- `[Project] - [Scene] - [Description]` e.g. `Jesse Oz - S01 - Opening Theme`
- Sequential numbering: `Track 001 - Title`

Present the full rename map to user for approval before executing.

### Step 4 - Execute renames
For each song:
1. Use `find` to locate the song's options/kebab menu
2. Click to open options
3. Select "Rename" or "Edit title"
4. Use `form_input` to clear and set new title
5. Confirm/save
6. Brief pause before next item to avoid rate limiting

### Step 5 - Verify
After all renames, reload the library page and extract titles again to confirm all renames applied correctly.

## Error Handling
- If a rename fails (stale DOM, rate limit): log it, skip, continue, report failures at end
- If Suno UI changes: use `read_page` to re-map DOM structure before retrying
- Session timeout: re-navigate to library and resume from last successful rename

## Notes
- Suno does not have a bulk rename API - all operations are UI-driven
- Works best with songs already loaded in library view (not clips/stems)
- Rate limit observed: ~1 rename per 2 seconds is safe
- This skill requires Claude-in-Chrome to be active - cannot run headlessly

## Status
- Originally built and tested: Feb/Mar 2026
- Recovered and committed to code-artifacts: 2026-03-15
- Needs: re-test against current Suno UI (may have changed)
