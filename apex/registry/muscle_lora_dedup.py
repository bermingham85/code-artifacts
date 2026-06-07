#!/usr/bin/env python3
"""APEX-MB-PY-00109 muscle_lora_dedup.py

SHA256+size LoRA dedup for C:/ComfyUI/models/loras/.

Modes:
  --dry-run                   Report duplicates only.
  --quarantine <phase-id>     Move duplicates to _quarantine/<phase-id>/ and write a manifest.
  --restore <manifest.json>   Move files from quarantine back to their original locations.

Built for ANIM-02 (G1 from ANIM-01 handover).
"""
from __future__ import annotations
import argparse
import datetime
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

DEFAULT_ROOT = Path(r"C:/ComfyUI/models/loras")


def sha256_of(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def index_loras(root: Path) -> dict[tuple[str, int], list[Path]]:
    by_key: dict[tuple[str, int], list[Path]] = {}
    for entry in sorted(root.iterdir()):
        if not entry.is_file() or entry.suffix.lower() not in {".safetensors", ".pt", ".ckpt"}:
            continue
        key = (sha256_of(entry), entry.stat().st_size)
        by_key.setdefault(key, []).append(entry)
    return by_key


def pick_canonical(group: list[Path]) -> Path:
    # Prefer the filename without " (N)" Windows-copy suffix; fall back to oldest mtime.
    plain = [p for p in group if " (" not in p.name]
    if plain:
        return sorted(plain, key=lambda p: p.stat().st_mtime)[0]
    return sorted(group, key=lambda p: p.stat().st_mtime)[0]


def report(by_key: dict[tuple[str, int], list[Path]]) -> list[dict]:
    findings = []
    for (sha, size), group in by_key.items():
        if len(group) < 2:
            continue
        canonical = pick_canonical(group)
        duplicates = [p for p in group if p != canonical]
        findings.append({
            "sha256": sha,
            "size": size,
            "canonical": str(canonical),
            "duplicates": [str(p) for p in duplicates],
        })
    return findings


def quarantine(root: Path, findings: list[dict], phase: str) -> dict:
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    qroot = root / "_quarantine" / phase
    qroot.mkdir(parents=True, exist_ok=True)
    moved = []
    for f in findings:
        for src in f["duplicates"]:
            srcp = Path(src)
            dst = qroot / srcp.name
            shutil.move(str(srcp), str(dst))
            moved.append({
                "original": src,
                "quarantine": str(dst),
                "sha256": f["sha256"],
                "size": f["size"],
                "moved_at": ts,
            })
    return {"phase": phase, "moved_at": ts, "moves": moved}


def restore(manifest_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    restored = []
    for m in manifest.get("moves", []):
        src = Path(m["quarantine"])
        dst = Path(m["original"])
        if not src.exists():
            restored.append({**m, "status": "missing-in-quarantine"})
            continue
        shutil.move(str(src), str(dst))
        restored.append({**m, "status": "restored"})
    return {"manifest": str(manifest_path), "restored": restored}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quarantine", metavar="PHASE")
    ap.add_argument("--restore", metavar="MANIFEST")
    ap.add_argument("--audit-out", default=None)
    args = ap.parse_args()

    if args.restore:
        out = restore(Path(args.restore))
        print(json.dumps(out, indent=2))
        return 0

    root = Path(args.root)
    if not root.is_dir():
        print(f"ERROR: root not a directory: {root}", file=sys.stderr)
        return 2

    by_key = index_loras(root)
    findings = report(by_key)

    if args.dry_run or not args.quarantine:
        print(json.dumps({"root": str(root), "duplicate_groups": findings}, indent=2))
        return 0

    manifest = quarantine(root, findings, args.quarantine)
    out_path = Path(args.audit_out) if args.audit_out else Path(
        os.environ.get("APEX_REPO", ".")
    ) / "apex/audit/anim-02/lora-dedup.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"manifest": str(out_path), "moves": len(manifest["moves"])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
