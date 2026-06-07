#!/usr/bin/env python3
"""APEX-MB-PY-00116 agen_recovery_extract.py

Verbatim extractor for AGEN-* agent artifacts inlined in Codex review
transcripts. Per doctrine R20 (no invention / preserve detail) and WO
APEX-ANIM-MB-WO-00001 §3 ("recover from … Codex review transcripts
(verbatim recovery, not invention)").

Transcripts inline each reviewed file between two markers:
    === FILE: <absolute path> ===
    <body>
    === END FILE ===

This tool extracts named files byte-for-byte and writes them to a
caller-specified live directory. Path-escape is closed: every output
path must resolve under the configured --out-dir.

Built for ANIM-08 (AGEN-Verification restore). Reusable by ANIM-09+
for the other four AGEN agents (Builder, Specification, Architecture,
Router) whose codex transcripts use the same marker convention.

Usage:
    python agen_recovery_extract.py \\
        --transcript <path-to-codex-runs/*.txt> \\
        --out-dir <path-to-live-AGEN-dir> \\
        --restore <basename1> [--restore <basename2> ...] \\
        [--dry-run]
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

# Byte-mode regex: matches the marker pair on the raw transcript bytes so
# offsets are true byte offsets and bodies are the exact captured byte slice
# (no newline normalisation, no errors='replace' substitutions, no text-mode
# decoding). Per doctrine R20 (verbatim recovery) this is the only valid mode
# for the "byte-exact" provenance claim.
MARKER = re.compile(
    rb"=== FILE: (.+?) ===\r?\n(.*?)\r?\n=== END FILE ===",
    re.DOTALL,
)


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def extract(transcript_path: Path) -> list[dict]:
    """Return [{src_path, basename, body_bytes, sha256, byte_start, byte_end}].

    transcript_path is read as raw bytes; the body returned is the exact byte
    slice between the markers; byte_start/byte_end are true byte offsets into
    the raw transcript.
    """
    raw = transcript_path.read_bytes()
    out: list[dict] = []
    for m in MARKER.finditer(raw):
        src_path = m.group(1).strip().decode("utf-8", errors="strict")
        body_bytes = m.group(2)
        basename = src_path.replace("\\", "/").rsplit("/", 1)[-1]
        out.append({
            "src_path_in_transcript": src_path,
            "basename": basename,
            "body_bytes": body_bytes,
            "sha256": sha256_hex(body_bytes),
            "byte_start": m.start(2),
            "byte_end": m.end(2),
            "size_bytes": len(body_bytes),
        })
    return out


def contained_under(target: Path, root: Path) -> bool:
    try:
        r_target = target.resolve(strict=False)
        r_root = root.resolve(strict=False)
        return Path(os.path.commonpath([str(r_target), str(r_root)])) == r_root
    except (ValueError, OSError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path,
                    help="Live directory to write into. Every output path must resolve under this.")
    ap.add_argument("--restore", action="append", default=[],
                    help="Basename to restore. Repeatable. If omitted, lists all candidates and exits.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="Allow overwrite of an existing destination whose bytes DIFFER from the "
                         "transcript slice. Without --force, a mismatch is rejected (SHA_MISMATCH). "
                         "An existing destination whose bytes already match is always a no-op.")
    args = ap.parse_args()

    if not args.transcript.is_file():
        print(json.dumps({"status": "TRANSCRIPT_NOT_FOUND", "transcript": str(args.transcript)}, indent=2))
        return 2
    if not args.out_dir.is_dir():
        print(json.dumps({"status": "OUT_DIR_NOT_FOUND", "out_dir": str(args.out_dir)}, indent=2))
        return 2

    candidates = extract(args.transcript)
    if not args.restore:
        print(json.dumps({
            "status": "LISTED",
            "transcript": str(args.transcript),
            "transcript_sha256": sha256_hex(args.transcript.read_bytes()),
            "candidates": [{"basename": c["basename"], "size_bytes": c["size_bytes"], "sha256": c["sha256"]}
                           for c in candidates],
        }, indent=2))
        return 0

    want = set(args.restore)
    written: list[dict] = []
    no_op_idempotent: list[dict] = []
    skipped: list[dict] = []
    rejected: list[dict] = []
    for c in candidates:
        if c["basename"] not in want:
            skipped.append({"basename": c["basename"], "reason": "not in --restore set"})
            continue
        dst = args.out_dir / c["basename"]
        if not contained_under(dst, args.out_dir):
            rejected.append({"basename": c["basename"], "reason": "PATH_ESCAPE_REJECTED",
                             "resolved": str(dst.resolve(strict=False)),
                             "out_dir_resolved": str(args.out_dir.resolve(strict=False))})
            continue
        # Existence + SHA guard per ANIM-08 round-3 fix (reversibility / idempotency):
        # - existing destination whose bytes match the transcript slice -> no-op (idempotent).
        # - existing destination whose bytes differ -> reject unless --force.
        # - destination absent -> normal write.
        action = "write"
        if dst.exists():
            try:
                existing_sha = sha256_hex(dst.read_bytes())
            except OSError as e:
                rejected.append({"basename": c["basename"], "reason": "DST_READ_FAILED",
                                 "dst": str(dst), "error": str(e)})
                continue
            if existing_sha == c["sha256"]:
                action = "no_op_idempotent"
                no_op_idempotent.append({
                    "basename": c["basename"],
                    "dst": str(dst),
                    "size_bytes": c["size_bytes"],
                    "sha256": c["sha256"],
                    "note": "Destination already byte-identical to transcript slice; no write performed.",
                })
                continue
            elif not args.force:
                rejected.append({"basename": c["basename"], "reason": "SHA_MISMATCH",
                                 "dst": str(dst), "existing_sha256": existing_sha,
                                 "transcript_sha256": c["sha256"],
                                 "hint": "rerun with --force to overwrite the divergent destination"})
                continue
            else:
                action = "overwrite_forced"
        if not args.dry_run:
            dst.write_bytes(c["body_bytes"])
        written.append({
            "basename": c["basename"],
            "dst": str(dst),
            "size_bytes": c["size_bytes"],
            "sha256": c["sha256"],
            "transcript_byte_start": c["byte_start"],
            "transcript_byte_end": c["byte_end"],
            "src_path_in_transcript": c["src_path_in_transcript"],
            "action": action,
        })
    missing = sorted(want - {c["basename"] for c in candidates})

    result = {
        "status": "OK" if not rejected and not missing else "PARTIAL",
        "dry_run": args.dry_run,
        "force": args.force,
        "transcript": str(args.transcript),
        "transcript_sha256": sha256_hex(args.transcript.read_bytes()),
        "out_dir": str(args.out_dir),
        "written": written,
        "no_op_idempotent": no_op_idempotent,
        "skipped": skipped,
        "rejected": rejected,
        "missing_from_transcript": missing,
    }
    print(json.dumps(result, indent=2))
    if rejected or missing:
        return 6
    return 0


if __name__ == "__main__":
    sys.exit(main())
