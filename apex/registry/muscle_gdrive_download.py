"""
muscle_gdrive_download.py — Google Drive File Downloader Muscle
Ref:        APEX-MB-PY-00014
Version:    1.0
Author:     MB / SYS
Description: Download a single file from Google Drive to a local path.
             Handles binary files (images, PDFs) and exports Google Workspace
             docs as PDF automatically.
Inputs:     --file-id       DRIVE_FILE_ID   Google Drive file ID
            --output-path   PATH            Local destination path
            --credentials   PATH            Service account JSON key file
Outputs:    Prints {"status": "OK", "output": PATH, "mime_type": TYPE} on success.
"""

import argparse
import io
import json
import sys
from pathlib import Path


SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

# Google Workspace MIME types → export as PDF
EXPORT_AS_PDF = {
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
    "application/vnd.google-apps.presentation",
}


def _build_service(credentials_path: str):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=SCOPES
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def muscle_gdrive_download(file_id: str, output_path: str, credentials: str) -> dict:
    """
    Download a Google Drive file to output_path.
    Returns {"status": "OK", "output": output_path, "mime_type": mime}.
    """
    from googleapiclient.http import MediaIoBaseDownload

    service = _build_service(credentials)
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Get metadata first
    meta = service.files().get(fileId=file_id, fields="id,name,mimeType").execute()
    mime = meta.get("mimeType", "application/octet-stream")

    if mime in EXPORT_AS_PDF:
        # Export Google Workspace file as PDF
        request = service.files().export_media(fileId=file_id, mimeType="application/pdf")
        effective_mime = "application/pdf"
        # Adjust output extension if needed
        if not str(dest).endswith(".pdf"):
            dest = dest.with_suffix(".pdf")
    else:
        request = service.files().get_media(fileId=file_id)
        effective_mime = mime

    buf = io.BytesIO()
    downloader = MediaIoBaseDownload(buf, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()

    dest.write_bytes(buf.getvalue())

    return {"status": "OK", "output": str(dest), "mime_type": effective_mime}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: download file from Google Drive")
    parser.add_argument("--file-id",     required=True, help="Google Drive file ID")
    parser.add_argument("--output-path", required=True, help="Local destination path")
    parser.add_argument("--credentials", required=True, help="Service account JSON key file")
    parser.add_argument("--task-folder", default="",    help="Foreman task folder (unused)")
    args = parser.parse_args()

    try:
        result = muscle_gdrive_download(args.file_id, args.output_path, args.credentials)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
