"""
muscle_work_gate.py - Apex Work Authority Gate
Ref:        APEX-MB-PY-00029
Version:    1.0
Author:     MB / SYS
Description: Checks repo and artifact authority before normal or fallback work.
Inputs:     --repo PATH       Repository/workspace path to inspect
            --mode MODE       normal, fallback, or auto
            --intent INTENT   read, write, or promote
            --allow-dirty     Permit write-mode continuation after inspecting dirty work
Outputs:    JSON gate report on stdout and optional audit file
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


APEX_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = APEX_ROOT / "docs" / "APEX_AUTHORITY_MANIFEST.json"
DEFAULT_AUDIT_DIR = APEX_ROOT / "audit" / "work_gate"
PROTECTED_BRANCHES = {"main", "master", "release", "production"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(repo: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def load_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def git_info(repo: Path, fetch: bool) -> dict[str, Any]:
    info: dict[str, Any] = {
        "path": str(repo),
        "is_git_repo": False,
        "fetch_attempted": fetch,
        "fetch_ok": None,
        "fetch_error": None,
    }

    code, root, err = run_git(repo, ["rev-parse", "--show-toplevel"])
    if code != 0:
        info["error"] = err or "not a git repository"
        return info

    repo_root = Path(root)
    info["is_git_repo"] = True
    info["root"] = str(repo_root)

    if fetch:
        code, _, err = run_git(repo_root, ["fetch", "--all", "--prune"])
        info["fetch_ok"] = code == 0
        if code != 0:
            info["fetch_error"] = err

    commands = {
        "branch": ["branch", "--show-current"],
        "head": ["rev-parse", "HEAD"],
        "upstream": ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        "remote_url": ["config", "--get", "remote.origin.url"],
        "status_short": ["status", "--short"],
    }
    for key, cmd in commands.items():
        code, out, err = run_git(repo_root, cmd)
        info[key] = out if code == 0 else None
        if key == "upstream" and code != 0:
            info["upstream_error"] = err

    info["dirty"] = bool(info.get("status_short"))
    upstream = info.get("upstream")
    if upstream:
        code, out, _ = run_git(repo_root, ["rev-list", "--left-right", "--count", f"HEAD...{upstream}"])
        if code == 0:
            left, right = out.split()
            info["ahead"] = int(left)
            info["behind"] = int(right)
    return info


def decide(
    mode: str,
    intent: str,
    info: dict[str, Any],
    manifest: dict[str, Any],
    allow_dirty: bool,
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    protected = set(manifest.get("protected_branches", [])) | PROTECTED_BRANCHES
    branch = info.get("branch")

    if not info.get("is_git_repo"):
        blockers.append("repo path is not a git repository")
    if intent in {"write", "promote"} and branch in protected:
        blockers.append(f"current branch '{branch}' is protected; create a task branch first")
    if intent in {"write", "promote"} and info.get("is_git_repo") and not info.get("upstream"):
        blockers.append("upstream branch is required before official write or promotion")
    if intent == "write" and mode == "normal" and not info.get("fetch_ok"):
        blockers.append("normal write requires successful remote fetch/latest check")
    if intent in {"write", "promote"} and info.get("behind", 0) > 0:
        blockers.append("local branch is behind its upstream; reconcile before official work")
    if intent == "promote" and info.get("dirty"):
        blockers.append("working tree has uncommitted changes; commit or archive before promotion")
    if intent == "write" and info.get("dirty") and not allow_dirty:
        blockers.append("working tree is dirty; inspect existing changes or rerun with --allow-dirty after approval")
    if intent == "promote" and not info.get("fetch_ok"):
        blockers.append("promotion requires a successful remote fetch/latest check")

    if not info.get("upstream") and info.get("is_git_repo"):
        warnings.append("no upstream branch is configured; remote freshness cannot be proven")
    if info.get("dirty") and intent != "promote" and allow_dirty:
        warnings.append("working tree is dirty; inspect user changes before editing")
    if mode == "fallback":
        warnings.append("fallback work is provisional until reconciled through GitHub and the X drive manifest")
        if not info.get("fetch_ok"):
            warnings.append("remote fetch did not prove latest state; write only to a task branch or inbox")

    promotion_allowed = not blockers and intent == "promote"
    official_write_allowed = not blockers and intent == "write" and mode == "normal"
    provisional_write_allowed = not blockers and intent == "write" and mode == "fallback"

    if blockers:
        status = "BLOCK"
    elif warnings:
        status = "WARN"
    else:
        status = "OK"

    return {
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "promotion_allowed": promotion_allowed,
        "official_write_allowed": official_write_allowed,
        "provisional_write_allowed": provisional_write_allowed,
        "required_route": route_for(mode, intent, blockers),
    }


def route_for(mode: str, intent: str, blockers: list[str]) -> list[str]:
    if intent == "read":
        return ["read manifest", "read repo state", "do not modify files"]
    if blockers:
        return ["stop official work", "create/update task branch or resolve blockers", "rerun work gate"]
    if mode == "fallback":
        return [
            "create or use codex/* or agent/* task branch",
            "write outputs to local workspace or X:/Apex/Inbox/<station>",
            "run gate again with --intent promote before anything becomes official",
        ]
    return [
        "work on task branch",
        "commit locally",
        "push branch or open PR; do not push directly to protected branches",
    ]


def write_audit(report: dict[str, Any], audit_dir: Path) -> Path:
    audit_dir.mkdir(parents=True, exist_ok=True)
    safe_project = report.get("project") or "unscoped"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    path = audit_dir / f"{stamp}-{safe_project}.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Apex authority gate before work or promotion.")
    parser.add_argument("--repo", default=".", help="Repository/workspace path to inspect.")
    parser.add_argument("--project", default="APEX", help="Project label for the report.")
    parser.add_argument("--mode", choices=("auto", "normal", "fallback"), default="auto")
    parser.add_argument("--intent", choices=("read", "write", "promote"), default="write")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--audit-dir", default=str(DEFAULT_AUDIT_DIR))
    parser.add_argument("--fetch", action="store_true", help="Run git fetch --all --prune before checking state.")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow write-mode continuation after dirty worktree review.")
    parser.add_argument("--no-audit", action="store_true", help="Do not write audit/work_gate report.")
    args = parser.parse_args()

    manifest = load_manifest(Path(args.manifest))
    mode = args.mode
    if mode == "auto":
        mode = os.environ.get("APEX_WORK_MODE", manifest.get("default_mode", "normal"))

    repo = Path(args.repo).resolve()
    info = git_info(repo, args.fetch)
    decision = decide(mode, args.intent, info, manifest, args.allow_dirty)

    report: dict[str, Any] = {
        "tool": "muscle_work_gate",
        "ref_code": "APEX-MB-PY-00029",
        "version": "1.0",
        "timestamp": utc_now(),
        "project": args.project,
        "station": platform.node(),
        "mode": mode,
        "intent": args.intent,
        "allow_dirty": args.allow_dirty,
        "authority": manifest.get("authority", {}),
        "repo": info,
        **decision,
    }

    if not args.no_audit:
        report["audit_path"] = str(write_audit(report, Path(args.audit_dir)))

    print(json.dumps(report, indent=2))
    return 2 if report["status"] == "BLOCK" else 0


if __name__ == "__main__":
    raise SystemExit(main())
