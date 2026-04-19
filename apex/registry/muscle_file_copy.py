"""
muscle_file_copy.py — File Copy Muscle
Ref:        APEX-MB-PY-00004
Version:    1.0
Author:     MB / SYS
Description: Copies a file from source to destination.
             Validates source exists. Creates destination directory if missing.
Inputs:     --source PATH  Source file path
            --dest PATH    Destination file path
Outputs:    Destination file. Prints {"status": "OK", "output": "<dest>"} on success.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path


def muscle_file_copy(source: str, dest: str) -> dict:
    """
    Copy file from source to dest.
    Creates destination directory if it does not exist.
    Returns {"status": "OK", "output": dest} or raises on error.
    """
    src_path  = Path(source)
    dest_path = Path(dest)

    if not src_path.exists():
        raise FileNotFoundError(f"Source not found: {source}")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src_path), str(dest_path))
    return {"status": "OK", "output": str(dest_path)}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: copy a file")
    parser.add_argument("--source",      required=True, help="Source file path")
    parser.add_argument("--dest",        required=True, help="Destination file path")
    parser.add_argument("--task-folder", default="",    help="Foreman task folder (unused by this muscle)")
    args = parser.parse_args()

    # Doc control duplicate check before writing output
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "docs"))
        from doc_controller import check_duplicate
        check_duplicate(Path(args.dest).name, args.dest)
    except Exception:
        pass  # Non-fatal: doc_controller may not be available in all envs

    try:
        result = muscle_file_copy(args.source, args.dest)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
