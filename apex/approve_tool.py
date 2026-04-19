"""
approve_tool.py — Tool Approval Gate
Ref:        APEX-MB-PY-00010  (assigned by doc_controller)
Version:    1.0
Author:     MB / SYS
Description: Validates that a muscle has all required docs and passing tests,
             then marks it approved in manifest.json and regenerates TOOL_INDEX.md.
             Only approved tools appear in TOOL_INDEX.md — the compact agent context file.

Usage:
    python approve_tool.py --tool muscle_health_check
    python approve_tool.py --tool muscle_health_check --force   # skip test-record check
    python approve_tool.py --list                               # show all tools + approval status
    python approve_tool.py --generate-index                     # regenerate TOOL_INDEX.md only
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
APEX_ROOT       = Path(__file__).parent
REGISTRY_DIR    = APEX_ROOT / "registry"
MANIFEST_FILE   = REGISTRY_DIR / "manifest.json"
DOCS_TOOLS_DIR  = APEX_ROOT / "docs" / "tools"
TOOL_INDEX_FILE = REGISTRY_DIR / "TOOL_INDEX.md"
NOTIFY_FILE     = APEX_ROOT / "store" / "pending_notifications.json"

# ── Required doc files ─────────────────────────────────────────────────────────
REQUIRED_DOCS = ["blueprint.md", "guidance.md", "test_record.md"]

# ── Category colours (for display only) ───────────────────────────────────────
CATEGORIES = {"system", "files", "data", "media", "comms", "ai", "util"}

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _load_manifest() -> dict:
    if not MANIFEST_FILE.exists():
        print("[approve] ERROR: manifest.json not found. Run: python indexer.py --scan")
        sys.exit(1)
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_manifest(manifest: dict):
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

def _check_docs(tool_name: str) -> tuple[bool, list[str]]:
    """Returns (all_present, list_of_missing)."""
    tool_dir = DOCS_TOOLS_DIR / tool_name
    missing = [d for d in REQUIRED_DOCS if not (tool_dir / d).exists()]
    return len(missing) == 0, missing

def _check_test_approval(tool_name: str) -> tuple[bool, str]:
    """
    Returns (approved, reason).
    Looks for 'Approved:** YES' in test_record.md.
    """
    test_record = DOCS_TOOLS_DIR / tool_name / "test_record.md"
    if not test_record.exists():
        return False, "test_record.md not found"
    content = test_record.read_text(encoding="utf-8")
    # Match any line containing both "Approved" and "YES" (handles **Approved:** YES, Approved: YES, etc.)
    if re.search(r"(?i)\bApproved\b[^\n]*\bYES\b", content):
        # Extract date if present
        date_match = re.search(r"\*{0,2}Approved\*{0,2}[:\s]+YES[^\n]*?(\d{4}-\d{2}-\d{2})", content)
        date_str = date_match.group(1) if date_match else _now_iso()[:10]
        return True, date_str
    if re.search(r"\*{0,2}Approved\*{0,2}[:\s]+NO", content, re.IGNORECASE):
        return False, "test_record.md says Approved: NO"
    return False, "No 'Approved: YES' stamp found in test_record.md"

def _get_tool_meta(tool_name: str) -> dict:
    """Extract ref_code, docstring, category from blueprint.md."""
    blueprint = DOCS_TOOLS_DIR / tool_name / "blueprint.md"
    ref_code  = "APEX-MB-PY-?????"
    category  = "util"
    one_liner = ""

    if blueprint.exists():
        content = blueprint.read_text(encoding="utf-8")
        # Extract ref code (handles **Ref Code** | VALUE | table format)
        ref_match = re.search(r"Ref Code[*\s]*\|\s*([A-Z]+-[A-Z]+-[A-Z]+-\d+)", content)
        if ref_match:
            ref_code = ref_match.group(1)
        # Extract category (handles **Category** | VALUE | table format)
        cat_match = re.search(r"Category[*\s]*\|\s*([a-z]+)", content)
        if cat_match:
            category = cat_match.group(1).lower()
        # Extract purpose (first line after ## Purpose)
        purpose_match = re.search(r"## Purpose\s+(.+)", content)
        if purpose_match:
            one_liner = purpose_match.group(1).strip()

    return {"ref_code": ref_code, "category": category, "one_liner": one_liner}

def _get_call_syntax(tool_name: str) -> str:
    """Extract the call syntax from guidance.md."""
    guidance = DOCS_TOOLS_DIR / tool_name / "guidance.md"
    if not guidance.exists():
        return f"python registry/{tool_name}.py"
    content = guidance.read_text(encoding="utf-8")
    # Find first code block with a python call
    match = re.search(r"```bash\s*(python registry/" + tool_name + r"[^\n]*)", content)
    if match:
        return match.group(1).strip()
    return f"python registry/{tool_name}.py"

def approve_tool(tool_name: str, force: bool = False) -> bool:
    """Run full approval gate. Returns True if approved."""
    print(f"\n[approve] Checking: {tool_name}")
    print(f"          Docs dir: {DOCS_TOOLS_DIR / tool_name}")

    # 1 — Check docs exist
    docs_ok, missing_docs = _check_docs(tool_name)
    if not docs_ok:
        print(f"[approve] FAIL — Missing documentation:")
        for d in missing_docs:
            print(f"          ✗ {d}")
        print(f"\n          Create docs at: docs/tools/{tool_name}/")
        print(f"          Templates in:    docs/templates/")
        return False
    print(f"[approve] Docs: OK (blueprint, guidance, test_record all present)")

    # 2 — Check test approval stamp
    if not force:
        test_ok, test_info = _check_test_approval(tool_name)
        if not test_ok:
            print(f"[approve] FAIL — Test record gate: {test_info}")
            print(f"          Add 'Approved: YES — YYYY-MM-DD' to test_record.md after all tests pass")
            return False
        print(f"[approve] Tests: APPROVED ({test_info})")
    else:
        print(f"[approve] Tests: SKIPPED (--force flag)")
        test_info = _now_iso()[:10]

    # 3 — Get tool metadata
    meta = _get_tool_meta(tool_name)
    call = _get_call_syntax(tool_name)

    # 4 — Update manifest.json
    manifest = _load_manifest()
    updated = False
    for skill in manifest.get("skills", []):
        if skill.get("name") == tool_name and skill.get("callable_as_muscle"):
            skill["approved"]      = True
            skill["approved_at"]   = test_info if "-" in test_info else _now_iso()[:10]
            skill["category"]      = meta["category"]
            skill["one_liner"]     = meta["one_liner"]
            skill["call_syntax"]   = call
            if meta["ref_code"] != "APEX-MB-PY-?????":
                skill["ref_code"] = meta["ref_code"]
            updated = True
            break

    if not updated:
        print(f"[approve] WARN — {tool_name} not found in manifest.json. Run indexer first.")
        print(f"          python indexer.py --scan")
        # Still continue — create a manual entry in the approved list
        manifest.setdefault("approved_tools", [])
        existing_refs = [t["name"] for t in manifest.get("approved_tools", [])]
        if tool_name not in existing_refs:
            manifest["approved_tools"].append({
                "name":        tool_name,
                "ref_code":    meta["ref_code"],
                "category":    meta["category"],
                "one_liner":   meta["one_liner"],
                "call_syntax": call,
                "approved":    True,
                "approved_at": test_info if "-" in test_info else _now_iso()[:10],
            })

    _save_manifest(manifest)
    print(f"[approve] manifest.json updated")

    # 5 — Regenerate TOOL_INDEX.md
    generate_tool_index(manifest)

    # 6 — Write notification for Brian
    _write_notification(tool_name, meta)

    print(f"\n[approve] APPROVED: {tool_name} is in TOOL_INDEX.md")
    return True


def generate_tool_index(manifest: dict | None = None):
    """Regenerate TOOL_INDEX.md from manifest. This is the file Brian reads."""
    if manifest is None:
        manifest = _load_manifest()

    approved   = []
    pending    = []
    all_muscles = []

    # Collect from main skills list
    for skill in manifest.get("skills", []):
        if not skill.get("callable_as_muscle"):
            continue
        name = skill.get("name", "")
        if not name.startswith("muscle_") and name not in ["main"]:
            continue
        if not name.startswith("muscle_"):
            continue
        if skill.get("approved"):
            approved.append(skill)
        else:
            pending.append(skill)

    # Also collect from approved_tools list (fallback for tools not yet indexed)
    indexed_names = {s.get("name") for s in approved}
    for tool in manifest.get("approved_tools", []):
        if tool.get("name") not in indexed_names:
            approved.append(tool)

    # Sort approved by ref_code
    approved.sort(key=lambda x: x.get("ref_code", ""))

    now        = _now_iso()
    total_musc = len(approved) + len(pending)

    lines = [
        f"# APEX TOOL INDEX",
        f"",
        f"**Generated:** {now}  |  **Approved:** {len(approved)}  |  **Pending:** {len(pending)}  |  **Total muscles:** {total_musc}",
        f"",
        f"> Brian reads this file. Only approved tools are safe to call in production.",
        f"> Regenerated by: `python approve_tool.py --generate-index`",
        f"",
        f"---",
        f"",
        f"## Approved Tools",
        f"",
        f"| Ref | Tool | Cat | What it does | Call |",
        f"|-----|------|-----|--------------|------|",
    ]

    for s in approved:
        ref      = s.get("ref_code", "—")
        name     = s.get("name", "?")
        cat      = s.get("category", "—")
        one_line = (s.get("one_liner") or s.get("docstring") or "—").split("\n")[0][:70]
        call     = s.get("call_syntax") or f"python registry/{name}.py"
        # Truncate call for readability
        call_short = call[:60] + "…" if len(call) > 60 else call
        lines.append(f"| `{ref}` | `{name}` | {cat} | {one_line} | `{call_short}` |")

    if pending:
        lines += [
            f"",
            f"---",
            f"",
            f"## Pending Approval (do NOT use in production)",
            f"",
            f"| Tool | Missing |",
            f"|------|---------|",
        ]
        for s in pending:
            name = s.get("name", "?")
            tool_dir = DOCS_TOOLS_DIR / name
            missing = [d for d in REQUIRED_DOCS if not (tool_dir / d).exists()]
            _, test_info = _check_test_approval(name) if not missing else (False, "docs missing")
            missing_str = ", ".join(missing) if missing else f"test approval ({test_info})"
            lines.append(f"| `{name}` | {missing_str} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## How to Use",
        f"",
        f"```bash",
        f"# Check a tool's blueprint",
        f"cat docs/tools/<tool_name>/blueprint.md",
        f"",
        f"# Approve a new tool",
        f"python approve_tool.py --tool muscle_name",
        f"",
        f"# List all tools + status",
        f"python approve_tool.py --list",
        f"",
        f"# Regenerate this file",
        f"python approve_tool.py --generate-index",
        f"",
        f"# Search for a tool",
        f"python indexer.py --search 'keyword'",
        f"```",
        f"",
        f"*Ref: APEX-MB-DOC-00000 | See docs/NAMING_CONVENTION.md (APEX-MB-DOC-00001) for standards*",
    ]

    TOOL_INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOOL_INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[approve] TOOL_INDEX.md written -> {TOOL_INDEX_FILE}")
    print(f"          {len(approved)} approved, {len(pending)} pending")


def _write_notification(tool_name: str, meta: dict):
    """Write a pending notification for Brian to pick up and send via Telegram."""
    NOTIFY_FILE.parent.mkdir(parents=True, exist_ok=True)
    notifications = []
    if NOTIFY_FILE.exists():
        try:
            notifications = json.loads(NOTIFY_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass

    notifications.append({
        "type":      "tool_approved",
        "tool":      tool_name,
        "ref_code":  meta.get("ref_code", ""),
        "category":  meta.get("category", ""),
        "one_liner": meta.get("one_liner", ""),
        "ts":        _now_iso(),
        "sent":      False,
    })
    NOTIFY_FILE.write_text(json.dumps(notifications, indent=2), encoding="utf-8")
    print(f"[approve] Notification queued for Brian")


def list_tools():
    """Print approval status of all muscles."""
    manifest = _load_manifest()
    muscles = [s for s in manifest.get("skills", [])
               if s.get("callable_as_muscle") and s.get("name", "").startswith("muscle_")]

    print(f"\nApex Tool Registry — {len(muscles)} muscles\n")
    print(f"{'Ref':<22} {'Tool':<30} {'Status':<12} {'Cat'}")
    print("-" * 80)

    for s in sorted(muscles, key=lambda x: x.get("ref_code", "")):
        name     = s.get("name", "?")
        ref      = s.get("ref_code", "—")
        approved = "✓ APPROVED" if s.get("approved") else "  pending"
        cat      = s.get("category", "—")
        print(f"{ref:<22} {name:<30} {approved:<12} {cat}")

    # Tools in approved_tools but not in manifest
    indexed = {s.get("name") for s in muscles}
    for t in manifest.get("approved_tools", []):
        if t.get("name") not in indexed:
            print(f"{t.get('ref_code','—'):<22} {t.get('name','?'):<30} {'✓ APPROVED':<12} {t.get('category','—')}")


def main():
    parser = argparse.ArgumentParser(description="Apex Tool Approval Gate")
    parser.add_argument("--tool",           type=str,  help="Tool name to approve (e.g. muscle_health_check)")
    parser.add_argument("--force",          action="store_true", help="Skip test-record check")
    parser.add_argument("--list",           action="store_true", help="List all tools and approval status")
    parser.add_argument("--generate-index", action="store_true", help="Regenerate TOOL_INDEX.md from manifest")
    args = parser.parse_args()

    if args.tool:
        ok = approve_tool(args.tool, force=args.force)
        sys.exit(0 if ok else 1)
    elif args.list:
        list_tools()
    elif args.generate_index:
        generate_tool_index()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
