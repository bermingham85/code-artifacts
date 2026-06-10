"""
muscle_gdrive_watcher.py — Google Drive Folder Watcher Muscle
Ref:        APEX-MB-PY-00013
Version:    1.0
Author:     MB / SYS
Description: Poll a Google Drive folder for new files since last run.
             Tracks last-seen state in a local JSON state file.
             Returns JSON array of new file objects.
Inputs:     --folder-id     DRIVE_FOLDER_ID   Google Drive folder ID to watch
            --state-file    PATH              JSON file tracking last_run timestamp
            --credentials   PATH              Service account JSON key file
Outputs:    Prints {"status": "OK", "output": PATH, "new_files": [...]} on success.
            new_files is a list of {id, name, mimeType, webViewLink, createdTime}.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def _build_service(credentials_path: str):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _load_state(state_file: Path) -> dict:
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except Exception:
            pass
    return {"last_run": "1970-01-01T00:00:00Z", "seen_ids": []}


def _save_state(state_file: Path, state: dict):
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps(state, indent=2))


def muscle_gdrive_watcher(folder_id: str, state_file: str, credentials: str) -> dict:
    """
    Poll a Google Drive folder for new files since last run.
    Returns {"status": "OK", "output": state_file, "new_files": [...]}.
    Each entry: {id, name, mimeType, webViewLink, createdTime}.
    """
    sf = Path(state_file)
    state = _load_state(sf)
    last_run = state.get("last_run", "1970-01-01T00:00:00Z")
    seen_ids = set(state.get("seen_ids", []))

    service = _build_service(credentials)

    query = (
        f"'{folder_id}' in parents "
        f"and createdTime > '{last_run}' "
        f"and trashed = false"
    )

    results = (
        service.files()
        .list(
            q=query,
            fields="files(id,name,mimeType,webViewLink,createdTime)",
            orderBy="createdTime asc",
            pageSize=100,
        )
        .execute()
    )

    files = results.get("files", [])
    new_files = [f for f in files if f["id"] not in seen_ids]

    # Update state
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["last_run"] = now_iso
    state["seen_ids"] = list(seen_ids | {f["id"] for f in new_files})
    _save_state(sf, state)

    # Write new_files list to a sidecar JSON for foreman/n8n to read
    output_path = sf.parent / "gdrive_new_files.json"
    output_path.write_text(json.dumps(new_files, indent=2))

    return {"status": "OK", "output": str(output_path), "new_files": new_files}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: watch Google Drive folder")
    parser.add_argument("--folder-id",   required=True, help="Google Drive folder ID")
    parser.add_argument("--state-file",  required=True, help="Path to JSON state file")
    parser.add_argument("--credentials", required=True, help="Service account JSON key file")
    parser.add_argument("--task-folder", default="",    help="Foreman task folder (unused)")
    args = parser.parse_args()

    try:
        result = muscle_gdrive_watcher(args.folder_id, args.state_file, args.credentials)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
