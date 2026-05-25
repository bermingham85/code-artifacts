"""
claude_codex_loop.py - Claude builder / Codex reviewer loop
Ref:        APEX-MB-PY-00023
Version:    1.0
Author:     MB / SYS
Description: Runs a prepared Claude Code prompt, reviews changed files with
             codex_bridge.py, then feeds Codex findings back to Claude until
             Codex signs off or the attempt limit is reached.
Inputs:     --prompt-file PATH --phase ID --repo PATH --max-attempts N
Outputs:    audit/claude_codex_loop/<phase>/ with builder/reviewer logs and
             SIGNED_OFF.json on a clean Codex pass.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_CODEX_BRIDGE = Path(r"C:\Users\Owner\apex_governance\cc_runbook\codex_bridge.py")
DEFAULT_X_APEX = Path(r"\\192.168.50.246\Extra\Automations\apex")
TEXT_SUFFIXES = {
    ".bat",
    ".cmd",
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sql",
    ".toml",
    ".ts",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot_repo(repo: Path) -> dict[str, str]:
    snap: dict[str, str] = {}
    for path in repo.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo).as_posix()
        if rel.startswith(".git/") or "/.git/" in rel:
            continue
        try:
            snap[rel] = sha256_file(path)
        except OSError:
            continue
    return snap


def changed_files(repo: Path, before: dict[str, str], after: dict[str, str]) -> list[Path]:
    changed: list[Path] = []
    for rel, digest in after.items():
        if before.get(rel) != digest:
            changed.append(repo / rel)
    return changed


def reviewable(paths: list[Path]) -> list[Path]:
    keep: list[Path] = []
    for path in paths:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 1_500_000:
                continue
        except OSError:
            continue
        keep.append(path)
    return keep


def collect_review_paths(paths: list[str], repo: Path) -> list[Path]:
    collected: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if not path.is_absolute():
            path = repo / path
        if path.is_file():
            collected.append(path)
        elif path.is_dir():
            collected.extend(p for p in path.rglob("*") if p.is_file())

    deduped: list[Path] = []
    seen: set[str] = set()
    for path in reviewable(collected):
        key = str(path.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def safe_env_for_claude() -> dict[str, str]:
    env = os.environ.copy()
    for key in ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "OPENAI_API_KEY"):
        env.pop(key, None)
    env["CLAUDE_AUTH_MODE"] = "subscription"
    return env


def safe_env_for_codex() -> dict[str, str]:
    env = os.environ.copy()
    for key in ("ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "OPENAI_API_KEY"):
        env.pop(key, None)
    env["CODEX_AUTH_MODE"] = "subscription"
    env.setdefault("CODEX_MODEL", "gpt-5.2")
    return env


def run_claude(
    prompt: str,
    cwd: Path,
    repo: Path,
    x_apex: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[bytes]:
    claude = shutil.which("claude")
    if not claude:
        raise RuntimeError("claude CLI not found on PATH")
    cmd = [
        claude,
        "-p",
        "--permission-mode",
        "auto",
        "--add-dir",
        str(repo),
        "--add-dir",
        str(x_apex),
    ]
    try:
        return subprocess.run(
            cmd,
            input=prompt.encode("utf-8"),
            cwd=str(cwd),
            env=safe_env_for_claude(),
            capture_output=True,
            text=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stderr = (exc.stderr or b"") + f"\nTimed out after {timeout_seconds} seconds.\n".encode("utf-8")
        return subprocess.CompletedProcess(cmd, 124, stdout=exc.stdout or b"", stderr=stderr)


def run_codex_review(
    paths: list[Path],
    phase: str,
    bridge: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[bytes]:
    if not bridge.exists():
        raise RuntimeError(f"codex bridge not found: {bridge}")
    cmd = [sys.executable, str(bridge), "review"]
    cmd.extend(str(p) for p in paths)
    cmd.extend(["--phase", phase])
    try:
        return subprocess.run(
            cmd,
            env=safe_env_for_codex(),
            capture_output=True,
            text=False,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        stderr = (exc.stderr or b"") + f"\nTimed out after {timeout_seconds} seconds.\n".encode("utf-8")
        return subprocess.CompletedProcess(cmd, 124, stdout=exc.stdout or b"", stderr=stderr)


def decode(data: bytes | None) -> str:
    return (data or b"").decode("utf-8", errors="replace")


def write_attempt_log(out_dir: Path, attempt: int, name: str, proc: subprocess.CompletedProcess[bytes]) -> Path:
    path = out_dir / f"attempt_{attempt:02d}_{name}.txt"
    path.write_text(
        "\n".join(
            [
                f"timestamp: {utc_now()}",
                f"returncode: {proc.returncode}",
                "--- STDOUT ---",
                decode(proc.stdout),
                "--- STDERR ---",
                decode(proc.stderr),
            ]
        ),
        encoding="utf-8",
    )
    return path


def build_fix_prompt(original_prompt: str, changed: list[Path], review_out: str, review_err: str) -> str:
    changed_list = "\n".join(f"- {p}" for p in changed) or "- none detected"
    return f"""You are continuing the same APEX build task.

Codex reviewed your previous build attempt and found blocking issues.

Rules:
- Fix only the issues Codex reports.
- Do not start PH-10 or unrelated filesystem cleanup.
- Keep changes inside the APEX repo unless explicitly instructed by the original prompt.
- Preserve existing user changes.
- When finished, print a concise summary and list changed files.

Changed files from the previous attempt:
{changed_list}

Codex review stdout:
{review_out}

Codex review stderr:
{review_err}

Original build prompt:
{original_prompt}
"""


def run_loop(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    prompt_file = Path(args.prompt_file)
    phase = args.phase

    if not repo.is_dir():
        raise SystemExit(f"Repo not found: {repo}")
    if not prompt_file.exists():
        raise SystemExit(f"Prompt file not found: {prompt_file}")

    out_dir = Path(args.out_dir) / phase
    out_dir.mkdir(parents=True, exist_ok=True)

    original_prompt = prompt_file.read_text(encoding="utf-8", errors="replace").strip()
    prompt = original_prompt
    baseline = snapshot_repo(repo)

    summary = {
        "phase": phase,
        "prompt_file": str(prompt_file),
        "repo": str(repo),
        "started": utc_now(),
        "attempts": [],
        "status": "running",
    }

    for attempt in range(1, args.max_attempts + 1):
        print(f"[loop] attempt {attempt}: running Claude builder")
        builder = run_claude(
            prompt,
            Path(args.claude_cwd).resolve(),
            repo,
            Path(args.x_apex),
            args.builder_timeout_minutes * 60,
        )
        builder_log = write_attempt_log(out_dir, attempt, "claude_builder", builder)

        after = snapshot_repo(repo)
        changed = changed_files(repo, baseline, after)
        to_review = []
        for path in reviewable(changed):
            rel = path.relative_to(repo).as_posix()
            if rel.startswith("audit/claude_codex_loop/"):
                continue
            to_review.append(path)
        seen_review = {str(path.resolve()).lower() for path in to_review}
        for path in collect_review_paths(args.review_path, repo):
            key = str(path.resolve()).lower()
            if key in seen_review:
                continue
            seen_review.add(key)
            to_review.append(path)
        changed_manifest = out_dir / f"attempt_{attempt:02d}_changed_files.json"
        changed_manifest.write_text(
            json.dumps(
                {
                    "changed_files": [str(p) for p in changed],
                    "reviewed_files": [str(p) for p in to_review],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        attempt_row = {
            "attempt": attempt,
            "builder_returncode": builder.returncode,
            "builder_log": str(builder_log),
            "changed_manifest": str(changed_manifest),
            "changed_files": [str(p) for p in changed],
            "reviewed_files": [str(p) for p in to_review],
        }

        if builder.returncode != 0:
            summary["status"] = "builder_failed"
            summary["attempts"].append(attempt_row)
            break

        if not to_review:
            summary["status"] = "no_reviewable_changes"
            summary["attempts"].append(attempt_row)
            break

        print(f"[loop] attempt {attempt}: running Codex review on {len(to_review)} file(s)")
        reviewer = run_codex_review(
            to_review,
            phase,
            Path(args.codex_bridge),
            args.reviewer_timeout_minutes * 60,
        )
        reviewer_log = write_attempt_log(out_dir, attempt, "codex_review", reviewer)
        attempt_row["reviewer_returncode"] = reviewer.returncode
        attempt_row["reviewer_log"] = str(reviewer_log)
        summary["attempts"].append(attempt_row)

        if reviewer.returncode == 0:
            summary["status"] = "signed_off"
            summary["completed"] = utc_now()
            (out_dir / "SIGNED_OFF.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
            print(f"[loop] Codex signed off. Wrote {out_dir / 'SIGNED_OFF.json'}")
            return 0

        if reviewer.returncode == 1:
            print("[loop] Codex found issues; preparing Claude fix prompt")
            prompt = build_fix_prompt(
                original_prompt,
                to_review,
                decode(reviewer.stdout),
                decode(reviewer.stderr),
            )
            continue

        summary["status"] = "reviewer_failed"
        break

    if summary["status"] == "running":
        summary["status"] = "max_attempts_exhausted"
    summary["completed"] = utc_now()
    (out_dir / "LOOP_FAILED.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[loop] loop ended with status={summary['status']}. Wrote {out_dir / 'LOOP_FAILED.json'}")
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Claude build + Codex review until sign-off.")
    parser.add_argument("--prompt-file", required=True, help="Prepared Claude build prompt.")
    parser.add_argument("--phase", required=True, help="Review phase/job label, e.g. AGEN-spec-agent.")
    parser.add_argument("--repo", default=str(Path.cwd()), help="APEX repo path.")
    parser.add_argument("--claude-cwd", default=str(Path.cwd()), help="Working directory for Claude.")
    parser.add_argument("--x-apex", default=str(DEFAULT_X_APEX), help="Shared APEX estate path.")
    parser.add_argument("--codex-bridge", default=str(DEFAULT_CODEX_BRIDGE), help="codex_bridge.py path.")
    parser.add_argument("--out-dir", default="audit/claude_codex_loop", help="Loop log root.")
    parser.add_argument("--max-attempts", type=int, default=5, help="Maximum Claude/Codex iterations.")
    parser.add_argument("--builder-timeout-minutes", type=int, default=120, help="Timeout for each Claude build attempt.")
    parser.add_argument("--reviewer-timeout-minutes", type=int, default=60, help="Timeout for each Codex review attempt.")
    parser.add_argument("--review-path", action="append", default=[], help="Extra file or directory to include in every Codex review.")
    return parser


def main(argv: list[str] | None = None) -> int:
    return run_loop(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
