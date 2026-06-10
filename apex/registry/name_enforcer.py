#!/usr/bin/env python3
"""
APEX Name Enforcer — Reference Code Assignment & Registration

Reference: APEX-SYS-PY-00008
Assigns valid reference codes to new files and appends them to DOCUMENT_REGISTER.md.

Usage:
    python name_enforcer.py <filename> <originator> <type> "<description>"

Example:
    python name_enforcer.py my_report.md MB RPRT "Monthly progress report"
"""

import re
import sys
import os
from datetime import date

# --- Configuration ---

APEX_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
REGISTER_PATH = os.path.join(APEX_ROOT, "docs", "DOCUMENT_REGISTER.md")
PROJECT_CODE = "APEX"

# Validation pattern: [PROJECT]-[ORIGINATOR]-[TYPE]-[SEQ5]
REF_PATTERN = re.compile(r"^[A-Z]{2,10}-[A-Z]{2,4}-[A-Z]{2,4}-\d{5}$")

VALID_TYPES = {"SPEC", "LOG", "CFG", "RPRT", "WF", "PY", "MD"}
VALID_ORIGINATORS = {"MB", "SYS"}


def read_register(path: str) -> str:
    """Read the full contents of DOCUMENT_REGISTER.md."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_current_sequence(register_text: str) -> int:
    """Extract the next available sequence number from the Sequence Tracker."""
    match = re.search(r"\| Next Available Sequence \| (\d{5}) \|", register_text)
    if not match:
        print("ERROR: Could not find Sequence Tracker in DOCUMENT_REGISTER.md")
        sys.exit(1)
    return int(match.group(1))


def validate_inputs(originator: str, doc_type: str) -> list[str]:
    """Validate originator and type codes. Returns list of errors (empty = valid)."""
    errors = []
    if originator.upper() not in VALID_ORIGINATORS:
        errors.append(
            f"Unknown originator '{originator}'. "
            f"Valid: {', '.join(sorted(VALID_ORIGINATORS))}"
        )
    if doc_type.upper() not in VALID_TYPES:
        errors.append(
            f"Unknown type '{doc_type}'. "
            f"Valid: {', '.join(sorted(VALID_TYPES))}"
        )
    return errors


def validate_ref_code(ref_code: str) -> bool:
    """Check if a reference code matches the canonical pattern."""
    return bool(REF_PATTERN.match(ref_code))


def build_ref_code(originator: str, doc_type: str, sequence: int) -> str:
    """Construct a reference code from its components."""
    return f"{PROJECT_CODE}-{originator.upper()}-{doc_type.upper()}-{sequence:05d}"


def append_to_register(
    register_path: str,
    register_text: str,
    ref_code: str,
    filename: str,
    location: str,
    doc_type: str,
    description: str,
    next_seq: int,
) -> str:
    """Append a new row to the Document Register table and bump the sequence."""

    # Build the new table row, padded to align with existing columns
    new_row = (
        f"| {ref_code:<18} "
        f"| {filename:<31} "
        f"| {location:<23} "
        f"| {doc_type:<4} "
        f"| {description:<56} |"
    )

    # Insert the new row before the separator line that follows the table
    # Find the last table row (line starting with "| APEX-")
    lines = register_text.splitlines()
    insert_index = None
    for i, line in enumerate(lines):
        if line.startswith("| APEX-"):
            insert_index = i + 1  # after the last data row

    if insert_index is None:
        print("ERROR: Could not locate the document register table.")
        sys.exit(1)

    lines.insert(insert_index, new_row)

    # Update the Sequence Tracker
    updated = "\n".join(lines)
    old_tracker = re.search(
        r"\| Next Available Sequence \| \d{5} \|", updated
    ).group(0)
    new_tracker = f"| Next Available Sequence | {next_seq:05d} |"
    updated = updated.replace(old_tracker, new_tracker)

    # Update the Last Updated date
    today = date.today().isoformat()
    updated = re.sub(
        r"\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}",
        f"**Last Updated:** {today}",
        updated,
    )

    # Write back
    with open(register_path, "w", encoding="utf-8") as f:
        f.write(updated)
        if not updated.endswith("\n"):
            f.write("\n")

    return updated


def main():
    if len(sys.argv) < 5:
        print("Usage: python name_enforcer.py <filename> <originator> <type> <description>")
        print('Example: python name_enforcer.py report.md MB RPRT "Monthly report"')
        sys.exit(1)

    filename = sys.argv[1]
    originator = sys.argv[2].upper()
    doc_type = sys.argv[3].upper()
    description = sys.argv[4]

    # Validate
    errors = validate_inputs(originator, doc_type)
    if errors:
        for e in errors:
            print(f"VALIDATION ERROR: {e}")
        sys.exit(1)

    # Read register
    if not os.path.exists(REGISTER_PATH):
        print(f"ERROR: Register not found at {REGISTER_PATH}")
        sys.exit(1)

    register_text = read_register(REGISTER_PATH)

    # Get next sequence
    current_seq = get_current_sequence(register_text)
    ref_code = build_ref_code(originator, doc_type, current_seq)

    # Validate the generated code
    if not validate_ref_code(ref_code):
        print(f"ERROR: Generated code '{ref_code}' fails validation.")
        sys.exit(1)

    # Determine location (default to registry/ for scripts, docs/ for docs)
    location = "./"

    # Append to register
    next_seq = current_seq + 1
    append_to_register(
        REGISTER_PATH,
        register_text,
        ref_code,
        filename,
        location,
        doc_type,
        description,
        next_seq,
    )

    print(f"Reference code assigned: {ref_code}")
    print(f"Registered in DOCUMENT_REGISTER.md")
    print(f"Next available sequence: {next_seq:05d}")


if __name__ == "__main__":
    main()
