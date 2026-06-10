"""
muscle_compliance_check.py - APEX Read-Only Compliance Checker
Ref:        APEX-SYS-PY-00001
Version:    1.0
Author:     SYS
Description: Read-only governance compliance checker. Verifies document register
             integrity, ref-code uniqueness, header/register agreement, disk
             coverage, three-doc rule for muscles, naming convention, and stale
             path roots. Exits non-zero on violations.
Inputs:     --root PATH        APEX repo root (default: parent of this file's dir)
            --report-dir PATH  Where to write JSON detail (default: <root>/audit/compliance)
            --quiet            Suppress human-readable stdout
            --strict           Treat warnings as failures
Outputs:    Human report to stdout + JSON detail to <report-dir>/<ts>.json.
            Exit codes: 0 = clean, 1 = violations, 2 = errors during check.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REF_FORMAT = re.compile(r"^[A-Z]{2,6}-[A-Z]{2,4}-[A-Z]{2,4}-\d{5}$")
HEADER_REF = re.compile(r"^Ref:\s*([A-Z][A-Z0-9-]+)\s*$", re.MULTILINE)
APPROVED = re.compile(
    r"(?:\*\*Approved(?:\s+for\s+registry)?\*\*\s*\|\s*YES|\*\*Approved(?:\s+for\s+registry)?:\*\*\s*YES)",
    re.IGNORECASE,
)
APPROVAL_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")

STALE_PREFIXES = (
    r"C:\Users\bermi\Projects\apex",
    r"\\192.168.50.246\Automations\apex",
    r"\\\\192.168.50.246\\Automations\\apex",
    "/shegoo/",
    "/apex/",
    r"C:\Users\Owner\apex_governance",
)

EXTERNAL_REF_PREFIXES = ("CLAW-", "SHEGOO-", "BERM-", "JESS-", "TALE-", "BALP-")


@dataclass
class RegisterRow:
    ref: str
    name: str
    version: str
    status: str
    created: str
    modified: str
    description: str
    raw_path: str
    resolved: Path | None = None
    resolution: str = ""  # ok | remapped | external | missing | no-path | stale-path-missing


@dataclass
class Findings:
    root: str = ""
    timestamp: str = ""
    register_entries: int = 0
    summary: dict = field(default_factory=dict)
    duplicate_refs: list = field(default_factory=list)
    header_register_mismatches: list = field(default_factory=list)
    invalid_ref_format: list = field(default_factory=list)
    registered_missing: list = field(default_factory=list)
    registered_stale_path: list = field(default_factory=list)
    registered_external: list = field(default_factory=list)
    unregistered_disk_files: list = field(default_factory=list)
    muscles_missing_docs: list = field(default_factory=list)
    muscles_unapproved: list = field(default_factory=list)
    secrets_on_disk: list = field(default_factory=list)


def parse_register(register_md: Path) -> list[RegisterRow]:
    text = register_md.read_text(encoding="utf-8", errors="replace")
    rows: list[RegisterRow] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 8:
            continue
        if cells[0].lower() in ("ref code", "----------") or cells[0].startswith("---"):
            continue
        rows.append(
            RegisterRow(
                ref=cells[0],
                name=cells[1],
                version=cells[2],
                status=cells[3],
                created=cells[4],
                modified=cells[5],
                description=cells[6],
                raw_path=cells[7],
            )
        )
    return rows


def remap_path(raw: str, root: Path) -> tuple[Path | None, str]:
    if not raw or raw in {"-", "—", "—"}:
        return None, "no-path"

    if raw.upper().startswith("N/A") or raw.startswith("<external>"):
        return None, "external"

    p = raw.replace("\\", "/").rstrip("/")

    bermi = "C:/Users/bermi/Projects/apex"
    qnap = "//192.168.50.246/Automations/apex"
    apex_governance = "C:/Users/Owner/apex_governance"

    candidate: Path | None = None
    note = "ok"

    if p.startswith(bermi):
        rel = p[len(bermi):].lstrip("/")
        candidate = root / rel
        note = "remapped" if candidate.exists() else "stale-path-missing"
    elif p.startswith(qnap):
        rel = p[len(qnap):].lstrip("/")
        candidate = root / rel
        note = "remapped" if candidate.exists() else "stale-path-missing"
    elif p == "/shegoo" or p.startswith("/shegoo/"):
        note = "stale-path-missing"
    elif p.startswith("/apex/"):
        rel = p[len("/apex/"):]
        candidate = root / rel
        note = "remapped" if candidate.exists() else "stale-path-missing"
    elif p.startswith("apex/"):
        rel = p[len("apex/"):]
        candidate = root / rel
        note = "remapped" if candidate.exists() else "stale-path-missing"
    elif p.startswith(apex_governance):
        rel = p[len(apex_governance):].lstrip("/")
        candidate = Path(raw)
        note = "external"
    elif Path(raw).is_absolute():
        candidate = Path(raw)
        note = "ok" if candidate.exists() else "missing"
    else:
        candidate = root / p
        note = "ok" if candidate.exists() else "missing"

    return candidate, note


def is_external_ref(ref: str) -> bool:
    return ref.startswith(EXTERNAL_REF_PREFIXES)


def collect_disk_files(root: Path) -> set[Path]:
    out: set[Path] = set()

    skip_parts = {"compliance", "clones"}
    for pattern in [
        "*.py",
        "*.md",
        "*.ps1",
        "templates/*.json",
        "registry/muscle_*.py",
        "registry/manifest.json",
        "registry/sources.json",
        "registry/TOOL_INDEX.md",
        "registry/muscles/manifest.json",
        "supervisor/*.py",
        "watchdog/*.py",
        "watchdog/*.bat",
        "docs/*.md",
        "docs/spec/*.md",
        "docs/policy/*.md",
        "docs/doctrine/*.md",
        "docs/doctrine/media/*.md",
        "docs/tools/*/*.md",
        "audit/*.json",
        "audit/*/*.json",
        "audit/*/**/*.json",
        "audit/health/*.json",
        "hub/WO-*.json",
    ]:
        for f in root.glob(pattern):
            if f.is_file() and not (skip_parts & set(f.parts)):
                out.add(f.resolve())

    return out


def find_secrets(root: Path) -> list[Path]:
    secrets: list[Path] = []
    for name in (".env", "credentials.json", "service_account.json"):
        for f in root.rglob(name):
            if f.is_file() and "node_modules" not in f.parts and ".git" not in f.parts:
                secrets.append(f)
    return secrets


def extract_header_ref(py_file: Path) -> str | None:
    try:
        with py_file.open("r", encoding="utf-8", errors="replace") as fh:
            head = fh.read(2048)
    except OSError:
        return None
    m = HEADER_REF.search(head)
    return m.group(1) if m else None


def check_three_doc(muscle_py: Path, root: Path) -> tuple[bool, bool, list[str]]:
    """Returns (all_three_present, approved, missing_docs)."""
    stem = muscle_py.stem  # e.g., muscle_health_check
    folder = root / "docs" / "tools" / stem
    needed = ["blueprint.md", "guidance.md", "test_record.md"]
    missing = [n for n in needed if not (folder / n).is_file()]
    if missing:
        return False, False, missing
    tr = folder / "test_record.md"
    text = tr.read_text(encoding="utf-8", errors="replace")
    approved = bool(APPROVED.search(text)) and bool(APPROVAL_DATE.search(text))
    return True, approved, []


def run(root: Path, report_dir: Path, strict: bool) -> tuple[int, Findings]:
    findings = Findings(
        root=str(root),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    register_md = root / "docs" / "DOCUMENT_REGISTER.md"
    if not register_md.is_file():
        print(f"FATAL: register not found at {register_md}", file=sys.stderr)
        return 2, findings

    rows = parse_register(register_md)
    findings.register_entries = len(rows)

    # 1. Resolve register paths and find duplicates / invalid refs
    by_ref: dict[str, list[RegisterRow]] = {}
    for r in rows:
        if not REF_FORMAT.match(r.ref):
            findings.invalid_ref_format.append({"ref": r.ref, "name": r.name})
        r.resolved, r.resolution = remap_path(r.raw_path, root)
        if is_external_ref(r.ref) and r.resolution in {
            "no-path",
            "missing",
            "stale-path-missing",
        }:
            r.resolved = None
            r.resolution = "external"
        by_ref.setdefault(r.ref, []).append(r)

    for ref, group in by_ref.items():
        if len(group) > 1:
            findings.duplicate_refs.append(
                {
                    "ref": ref,
                    "uses": [
                        {
                            "name": g.name,
                            "path": g.raw_path,
                            "resolution": g.resolution,
                        }
                        for g in group
                    ],
                }
            )

    # 2. Bucket register entries by resolution state
    for r in rows:
        if r.resolution == "stale-path-missing":
            findings.registered_stale_path.append(
                {"ref": r.ref, "name": r.name, "path": r.raw_path}
            )
        elif r.resolution == "missing":
            findings.registered_missing.append(
                {"ref": r.ref, "name": r.name, "path": r.raw_path}
            )
        elif r.resolution == "no-path":
            findings.registered_missing.append(
                {"ref": r.ref, "name": r.name, "path": "(blank)"}
            )
        elif r.resolution == "external":
            findings.registered_external.append(
                {"ref": r.ref, "name": r.name, "path": r.raw_path}
            )

    # 3. Header vs register agreement (Python files)
    py_files = list(root.glob("registry/*.py")) + list(root.glob("*.py"))
    py_files = [p for p in py_files if "clones" not in p.parts]

    header_index: dict[str, list[Path]] = {}
    for f in py_files:
        ref = extract_header_ref(f)
        if not ref:
            continue
        header_index.setdefault(ref, []).append(f)

    for ref, files in header_index.items():
        if len(files) > 1:
            findings.duplicate_refs.append(
                {
                    "ref": ref,
                    "uses": [
                        {"name": f.name, "path": str(f), "resolution": "header"}
                        for f in files
                    ],
                    "source": "header",
                }
            )

    register_paths_by_ref = {
        r.ref: r.resolved for r in rows if r.resolved is not None
    }

    for ref, files in header_index.items():
        reg_resolved = register_paths_by_ref.get(ref)
        if reg_resolved is None:
            findings.header_register_mismatches.append(
                {
                    "ref": ref,
                    "header_files": [str(f) for f in files],
                    "issue": "ref in header but not in register (or register path unresolved)",
                }
            )
            continue
        try:
            same = any(f.resolve() == reg_resolved.resolve() for f in files)
        except OSError:
            same = False
        if not same:
            findings.header_register_mismatches.append(
                {
                    "ref": ref,
                    "header_files": [str(f) for f in files],
                    "register_path": str(reg_resolved),
                    "issue": "header file != register-resolved file",
                }
            )

    # 4. Disk files not registered
    registered_resolved: set[Path] = set()
    for r in rows:
        if r.resolved and r.resolution in {"ok", "remapped"}:
            try:
                registered_resolved.add(r.resolved.resolve())
            except OSError:
                pass

    for f in collect_disk_files(root):
        try:
            rf = f.resolve()
        except OSError:
            continue
        if rf in registered_resolved:
            continue
        findings.unregistered_disk_files.append(str(f.relative_to(root)))

    # 5. Three-doc rule for muscles
    for muscle in sorted(root.glob("registry/muscle_*.py")):
        ok, approved, missing = check_three_doc(muscle, root)
        if not ok:
            findings.muscles_missing_docs.append(
                {"muscle": muscle.name, "missing": missing}
            )
        elif not approved:
            findings.muscles_unapproved.append(
                {"muscle": muscle.name, "reason": "test_record lacks YES + date"}
            )

    # 6. Secrets on disk
    for s in find_secrets(root):
        findings.secrets_on_disk.append(str(s.relative_to(root)))

    # 7. Summary
    findings.summary = {
        "register_entries": findings.register_entries,
        "registered_resolved": len(registered_resolved),
        "registered_missing": len(findings.registered_missing),
        "registered_stale_path": len(findings.registered_stale_path),
        "registered_external": len(findings.registered_external),
        "duplicate_refs": len(findings.duplicate_refs),
        "header_register_mismatches": len(findings.header_register_mismatches),
        "invalid_ref_format": len(findings.invalid_ref_format),
        "unregistered_disk_files": len(findings.unregistered_disk_files),
        "muscles_missing_docs": len(findings.muscles_missing_docs),
        "muscles_unapproved": len(findings.muscles_unapproved),
        "secrets_on_disk": len(findings.secrets_on_disk),
    }

    fails = (
        findings.summary["duplicate_refs"]
        + findings.summary["header_register_mismatches"]
        + findings.summary["registered_missing"]
        + findings.summary["invalid_ref_format"]
    )
    warns = (
        findings.summary["registered_stale_path"]
        + findings.summary["unregistered_disk_files"]
        + findings.summary["muscles_missing_docs"]
        + findings.summary["muscles_unapproved"]
        + findings.summary["secrets_on_disk"]
    )

    report_dir.mkdir(parents=True, exist_ok=True)
    out_file = report_dir / (
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ") + ".json"
    )
    out_file.write_text(
        json.dumps(
            {
                "root": findings.root,
                "timestamp": findings.timestamp,
                "summary": findings.summary,
                "fails": fails,
                "warns": warns,
                "details": {
                    "duplicate_refs": findings.duplicate_refs,
                    "header_register_mismatches": findings.header_register_mismatches,
                    "invalid_ref_format": findings.invalid_ref_format,
                    "registered_missing": findings.registered_missing,
                    "registered_stale_path": findings.registered_stale_path,
                    "registered_external": findings.registered_external,
                    "unregistered_disk_files": findings.unregistered_disk_files,
                    "muscles_missing_docs": findings.muscles_missing_docs,
                    "muscles_unapproved": findings.muscles_unapproved,
                    "secrets_on_disk": findings.secrets_on_disk,
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    exit_code = 1 if fails or (strict and warns) else 0
    return exit_code, findings


def print_report(findings: Findings, json_path: Path) -> None:
    s = findings.summary
    print(f"APEX Compliance Check  -  root: {findings.root}")
    print(f"timestamp: {findings.timestamp}")
    print()
    print("SUMMARY")
    for k, v in s.items():
        print(f"  {k:<30} {v}")
    print()
    print(f"  detail JSON: {json_path}")

    def show(title: str, items: list, key=None, limit: int = 10) -> None:
        if not items:
            return
        print()
        print(f"{title} ({len(items)} total, showing up to {limit}):")
        for i in items[:limit]:
            if key is None:
                print(f"  - {i}")
            else:
                print(f"  - {key(i)}")
        if len(items) > limit:
            print(f"  ... {len(items) - limit} more in JSON detail")

    show(
        "FAIL: duplicate refs",
        findings.duplicate_refs,
        key=lambda d: f"{d['ref']}: " + ", ".join(u['name'] for u in d['uses']),
    )
    show(
        "FAIL: header/register mismatches",
        findings.header_register_mismatches,
        key=lambda d: f"{d['ref']}: {d['issue']}",
    )
    show(
        "FAIL: invalid ref format",
        findings.invalid_ref_format,
        key=lambda d: f"{d['ref']} ({d['name']})",
    )
    show(
        "FAIL: registered but missing on disk",
        findings.registered_missing,
        key=lambda d: f"{d['ref']} {d['name']} -> {d['path']}",
    )
    show(
        "WARN: stale-path register entries",
        findings.registered_stale_path,
        key=lambda d: f"{d['ref']} {d['name']} -> {d['path']}",
    )
    show(
        "WARN: muscles missing 3-doc set",
        findings.muscles_missing_docs,
        key=lambda d: f"{d['muscle']} missing {','.join(d['missing'])}",
    )
    show(
        "WARN: muscles unapproved (3 docs but no YES+date)",
        findings.muscles_unapproved,
        key=lambda d: f"{d['muscle']}: {d['reason']}",
    )
    show("WARN: unregistered disk files", findings.unregistered_disk_files)
    show("WARN: secrets on disk", findings.secrets_on_disk)


def main(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="APEX read-only compliance checker")
    parser.add_argument("--root", type=Path, default=here)
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=None,
        help="default: <root>/audit/compliance",
    )
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    report_dir = (args.report_dir or (root / "audit" / "compliance")).resolve()

    code, findings = run(root, report_dir, args.strict)

    if report_dir.is_dir():
        reports = sorted(report_dir.glob("*.json"))
        json_path = reports[-1] if reports else report_dir
    else:
        json_path = report_dir
    if not args.quiet:
        print_report(findings, json_path)

    return code


if __name__ == "__main__":
    sys.exit(main())
