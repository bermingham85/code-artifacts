"""
muscle_text_transform.py — Text Transformation Muscle
Ref:        APEX-MB-PY-00005
Version:    1.0
Author:     MB / SYS
Description: Applies text transformations to a file: upper, lower, strip, replace, word_count.
Inputs:     --input PATH        Source file
            --output PATH       Output file
            --operation STR     upper | lower | strip | replace | word_count
            --find STR          (required for replace) string to find
            --replace STR       (required for replace) replacement string
Outputs:    Transformed file at --output. Prints {"status": "OK", "output": "<path>"}.
"""

import argparse
import json
import sys
from pathlib import Path


def muscle_text_transform(input_path: str, output_path: str, operation: str,
                          find: str = "", replace_with: str = "") -> dict:
    """
    Read input file, apply text operation, write to output file.
    Operations: upper, lower, strip, replace, word_count.
    Returns {"status": "OK", "output": output_path, "word_count": N} or raises.
    """
    src = Path(input_path)
    if not src.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    text = src.read_text(encoding="utf-8", errors="ignore")
    extra = {}

    if operation == "upper":
        result = text.upper()
    elif operation == "lower":
        result = text.lower()
    elif operation == "strip":
        result = text.strip()
    elif operation == "replace":
        if not find:
            raise ValueError("--find is required for replace operation")
        result = text.replace(find, replace_with)
    elif operation == "word_count":
        count  = len(text.split())
        result = str(count)
        extra  = {"word_count": count}
    else:
        raise ValueError(f"Unknown operation: {operation}. Use: upper, lower, strip, replace, word_count")

    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding="utf-8")

    return {"status": "OK", "output": str(out_path), **extra}


def main():
    parser = argparse.ArgumentParser(description="Apex muscle: text transform")
    parser.add_argument("--input",       required=True,  help="Source text file")
    parser.add_argument("--output",      required=True,  help="Output file path")
    parser.add_argument("--operation",   required=True,
                        choices=["upper", "lower", "strip", "replace", "word_count"])
    parser.add_argument("--find",        default="",     help="String to find (replace only)")
    parser.add_argument("--replace",     default="",     help="Replacement string (replace only)")
    parser.add_argument("--task-folder", default="",     help="Foreman task folder (unused)")
    args = parser.parse_args()

    try:
        result = muscle_text_transform(args.input, args.output, args.operation,
                                       find=args.find, replace_with=args.replace)
        print(json.dumps(result))
        sys.exit(0)
    except Exception as e:
        import traceback
        print(json.dumps({"status": "ERROR", "error": str(e), "traceback": traceback.format_exc()}))
        sys.exit(1)


if __name__ == "__main__":
    main()
