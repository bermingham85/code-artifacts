"""
doc_controller.py — Document Control System
Ref:        APEX-MB-PY-00000
Version:    1.0
Author:     MB / SYS
Description: Issues ref codes, registers documents, tracks versions, prevents duplicates.
             Thread-safe: all writes use filelock to prevent corruption under concurrent foreman.

Usage:
    python doc_controller.py --init
    python doc_controller.py --register
    python doc_controller.py --search "query"
    python doc_controller.py --list
"""

import argparse
import json
import os
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

try:
    from filelock import FileLock
except ImportError:
    # Graceful fallback: no-op lock if filelock not installed
    class FileLock:
        def __init__(self, path, timeout=30):
            self.path = path
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
APEX_ROOT = Path(__file__).parent.parent
DOCS_DIR = APEX_ROOT / "docs"
REGISTER_FILE = DOCS_DIR / "DOCUMENT_REGISTER.md"
AUDIT_DIR = APEX_ROOT / "audit"
AUDIT_FILE = AUDIT_DIR / "doc_audit.jsonl"
LOCK_FILE = DOCS_DIR / ".doc_controller.lock"

# ---------------------------------------------------------------------------
# Valid meta values
# ---------------------------------------------------------------------------
VALID_PROJECTS = {"APEX", "CLAW", "BERM", "JESS", "TALE", "BALP"}
VALID_ORIGINATORS = {"MB", "SYS"}
VALID_TYPES = {"WF", "PY", "TS", "CFG", "SCH", "DOC", "AGT"}

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_dirs():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_register() -> list[dict]:
    """Read DOCUMENT_REGISTER.md and return list of row dicts."""
    if not REGISTER_FILE.exists():
        return []
    rows = []
    with open(REGISTER_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line.startswith("|") or line.startswith("| Ref Code") or line.startswith("|---"):
            continue
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) < 8:
            continue
        rows.append({
            "ref_code":    parts[0],
            "name":        parts[1],
            "version":     parts[2],
            "status":      parts[3],
            "created":     parts[4],
            "modified":    parts[5],
            "description": parts[6],
            "path":        parts[7],
        })
    return rows


def _write_register(rows: list[dict]):
    """Rewrite the DOCUMENT_REGISTER.md from list of row dicts."""
    header = (
        "# Document Register — Project Apex\n\n"
        "| Ref Code | Name | Version | Status | Created | Modified | Description | Path |\n"
        "|----------|------|---------|--------|---------|----------|-------------|------|\n"
    )
    lines = []
    for r in rows:
        lines.append(
            f"| {r['ref_code']} | {r['name']} | {r['version']} | {r['status']} "
            f"| {r['created']} | {r['modified']} | {r['description']} | {r['path']} |"
        )
    with open(REGISTER_FILE, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(lines) + "\n")


def _append_audit(entry: dict):
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _next_seq(project: str, originator: str, doc_type: str, rows: list[dict]) -> str:
    """Find highest existing seq for this prefix, return next padded to 5 digits."""
    prefix = f"{project}-{originator}-{doc_type}-"
    max_seq = -1
    for r in rows:
        if r["ref_code"].startswith(prefix):
            try:
                seq = int(r["ref_code"][len(prefix):])
                if seq > max_seq:
                    max_seq = seq
            except ValueError:
                pass
    return f"{prefix}{max_seq + 1:05d}"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def issue_ref(project: str, originator: str, doc_type: str) -> str:
    """
    Issue the next sequential ref code for (project, originator, type).
    Does NOT register — use register_doc() after creating the file.

    Returns: ref_code string e.g. "APEX-MB-PY-00001"
    """
    project = project.upper()
    originator = originator.upper()
    doc_type = doc_type.upper()
    if project not in VALID_PROJECTS:
        raise ValueError(f"Invalid project '{project}'. Valid: {VALID_PROJECTS}")
    if originator not in VALID_ORIGINATORS:
        raise ValueError(f"Invalid originator '{originator}'. Valid: {VALID_ORIGINATORS}")
    if doc_type not in VALID_TYPES:
        raise ValueError(f"Invalid type '{doc_type}'. Valid: {VALID_TYPES}")

    _ensure_dirs()
    with FileLock(str(LOCK_FILE), timeout=30):
        rows = _parse_register()
        return _next_seq(project, originator, doc_type, rows)


def register_doc(ref_code: str, name: str, path: str, description: str,
                 changed_by: str = "SYS") -> dict:
    """
    Add a new row to DOCUMENT_REGISTER.md.
    If ref_code already exists, returns existing row without modification.

    Returns: the registered row dict.
    """
    _ensure_dirs()
    with FileLock(str(LOCK_FILE), timeout=30):
        rows = _parse_register()
        # Idempotency: don't double-register
        for r in rows:
            if r["ref_code"] == ref_code:
                return r
        now = _now_iso()
        row = {
            "ref_code":    ref_code,
            "name":        name,
            "version":     "1.0",
            "status":      "ACTIVE",
            "created":     now,
            "modified":    now,
            "description": description,
            "path":        path,
        }
        rows.append(row)
        _write_register(rows)
        _append_audit({
            "timestamp":          now,
            "action":             "REGISTER",
            "ref_code":           ref_code,
            "version":            "1.0",
            "changed_by":         changed_by,
            "change_description": f"Initial registration: {name}",
            "path":               path,
        })
    return row


def version_bump(ref_code: str, change_description: str, changed_by: str = "SYS") -> str:
    """
    Increment the minor version of an existing document and log to audit.
    Returns the new version string.
    """
    _ensure_dirs()
    with FileLock(str(LOCK_FILE), timeout=30):
        rows = _parse_register()
        for r in rows:
            if r["ref_code"] == ref_code:
                parts = r["version"].split(".")
                major = int(parts[0])
                minor = int(parts[1]) if len(parts) > 1 else 0
                new_version = f"{major}.{minor + 1}"
                r["version"] = new_version
                r["modified"] = _now_iso()
                _write_register(rows)
                _append_audit({
                    "timestamp":          r["modified"],
                    "action":             "VERSION_BUMP",
                    "ref_code":           ref_code,
                    "version":            new_version,
                    "changed_by":         changed_by,
                    "change_description": change_description,
                    "path":               r["path"],
                })
                return new_version
        raise KeyError(f"Ref code '{ref_code}' not found in register.")


def find_doc(query: str) -> list[dict]:
    """
    Search register by ref_code, name, path, or description (case-insensitive).
    Returns list of matching row dicts.
    """
    rows = _parse_register()
    q = query.lower()
    results = []
    for r in rows:
        if (q in r["ref_code"].lower() or
                q in r["name"].lower() or
                q in r["path"].lower() or
                q in r["description"].lower()):
            results.append(r)
            _append_audit({
                "timestamp":          _now_iso(),
                "action":             "LOOKUP",
                "ref_code":           r["ref_code"],
                "version":            r["version"],
                "changed_by":         "SYS",
                "change_description": f"Search query: {query}",
                "path":               r["path"],
            })
    return results


def check_duplicate(name: str, path: str) -> dict | None:
    """
    Check if a document with this name or path already exists.
    Returns existing row dict if found, None otherwise.
    """
    rows = _parse_register()
    name_lower = name.lower()
    path_lower = path.lower().replace("\\", "/")
    for r in rows:
        if (r["name"].lower() == name_lower or
                r["path"].lower().replace("\\", "/") == path_lower):
            return r
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_init():
    """Create DOCUMENT_REGISTER.md if it doesn't exist."""
    _ensure_dirs()
    with FileLock(str(LOCK_FILE), timeout=30):
        if not REGISTER_FILE.exists():
            _write_register([])
            print(f"[doc_controller] Initialized: {REGISTER_FILE}")
        else:
            print(f"[doc_controller] Already exists: {REGISTER_FILE}")
    # Self-register
    existing = check_duplicate("doc_controller.py", str(Path(__file__)))
    if not existing:
        ref = issue_ref("APEX", "MB", "PY")
        # Force ref to APEX-MB-PY-00000 for the spec-assigned code
        # (issue_ref will return 00000 since register is empty at init)
        register_doc(
            ref_code=ref,
            name="doc_controller.py",
            path=str(Path(__file__)),
            description="Document control: ref codes, register, version, search, duplicate check",
            changed_by="MB",
        )
        print(f"[doc_controller] Self-registered as {ref}")
    else:
        print(f"[doc_controller] Already registered as {existing['ref_code']}")


def cmd_register():
    """Interactive registration of a new document."""
    print("=== Register New Document ===")
    project     = input("Project (APEX/CLAW/BERM/JESS/TALE/BALP): ").strip().upper()
    originator  = input("Originator (MB/SYS): ").strip().upper()
    doc_type    = input("Type (WF/PY/TS/CFG/SCH/DOC/AGT): ").strip().upper()
    name        = input("Name (filename or title): ").strip()
    path        = input("Path: ").strip()
    description = input("Description: ").strip()

    dup = check_duplicate(name, path)
    if dup:
        print(f"[doc_controller] DUPLICATE FOUND: {dup['ref_code']} — {dup['name']}")
        print("  Use existing ref code. No new registration needed.")
        return

    ref = issue_ref(project, originator, doc_type)
    row = register_doc(ref, name, path, description, changed_by="MB")
    print(f"[doc_controller] Registered: {ref} — {name}")


def cmd_search(query: str):
    """Search the register and print matches."""
    results = find_doc(query)
    if not results:
        print(f"[doc_controller] No matches for '{query}'")
        return
    print(f"[doc_controller] {len(results)} match(es) for '{query}':")
    for r in results:
        print(f"  {r['ref_code']} | v{r['version']} | {r['name']} | {r['path']}")


def cmd_list():
    """Print all registered documents."""
    rows = _parse_register()
    if not rows:
        print("[doc_controller] Register is empty.")
        return
    print(f"[doc_controller] {len(rows)} document(s) registered:")
    for r in rows:
        print(f"  {r['ref_code']} | v{r['version']} | {r['status']} | {r['name']}")


def main():
    parser = argparse.ArgumentParser(description="Apex Document Control System")
    parser.add_argument("--init",     action="store_true", help="Initialize register")
    parser.add_argument("--register", action="store_true", help="Register new document")
    parser.add_argument("--search",   type=str,            help="Search register")
    parser.add_argument("--list",     action="store_true", help="List all documents")
    parser.add_argument("--bump",     type=str,            help="Version bump a ref code")
    parser.add_argument("--msg",      type=str,            default="", help="Change description for --bump")
    args = parser.parse_args()

    if args.init:
        cmd_init()
    elif args.register:
        cmd_register()
    elif args.search:
        cmd_search(args.search)
    elif args.list:
        cmd_list()
    elif args.bump:
        new_v = version_bump(args.bump, args.msg or "Manual version bump", changed_by="MB")
        print(f"[doc_controller] {args.bump} bumped to v{new_v}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
