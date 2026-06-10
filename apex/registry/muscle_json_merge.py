"""
muscle_json_merge.py — JSON Deep Merge Muscle
Ref:        APEX-MB-PY-00006
Version:    1.0
Author:     MB / SYS
Description: Deep-merges two or more JSON files. Last file wins on key conflicts.
Inputs:     --inputs PATH,PATH,...  Comma-separated list of JSON files to merge
            --output PATH           Output merged JSON file
Outputs:    Merged JSON at --output. Prints {"status": "OK", "output": "<path>"}.
"""

import argparse
import json
import sys
from pathlib import Path


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base. Last value wins on conflict."""
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def muscle_json_merge(input_paths: list[str], output_path: str) -> dict:
    """
    Deep-merge a list of JSON files. Last file wins on key conflicts.
    Returns {"status": "OK", "output": output_path} or raises.
    """
    if len(input_paths) < 2:
        raise ValueError(f"Need at least 2 input files, got {len(input_paths)}")

    merged = {}
    for path_str in input_paths:
        p = Path(path_str)
        if not p.exists():
            raise FileNotFoundError(f"Input not found: {path_str}")
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Only JSON objects (dicts) can be merged — {path_str} contains {type(data).__name__}")
        merged = _deep_merge(merged, data)

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")

    return {"status": "OK", "output": str(out_path), "merged_files": len(input_paths)}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: deep merge JSON files")
    parser.add_argument("--inputs",      required=True, help="Comma-separated JSON file paths")
    parser.add_argument("--output",      required=True, help="Output JSON file path")
    parser.add_argument("--task-folder", default="",    help="Foreman task folder (unused)")
    args = parser.parse_args()

    input_paths = [p.strip() for p in args.inputs.split(",") if p.strip()]

    try:
        result = muscle_json_merge(input_paths, args.output)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
