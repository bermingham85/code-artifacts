"""
generate_repo_menu.py - Apex Repository Menu Generator
Ref:        APEX-MB-PY-00027
Version:    1.0
Author:     MB / SYS
Description: Scans local repository roots and writes compact repo menus for
             future Claude/Codex contexts.
Inputs:     --root PATH       Root folder to scan, repeatable
            --output-md PATH  Markdown output path
            --output-json PATH JSON output path
            --max-depth N     Directory depth below root to discover repos
Outputs:    JSON status on stdout.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


APEX_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = [Path(r"C:\Users\Owner\Repos")]
DEFAULT_OUTPUT_MD = APEX_ROOT / "docs" / "APEX_REPO_MENU.md"
DEFAULT_OUTPUT_JSON = APEX_ROOT / "docs" / "APEX_REPO_MENU.json"
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".next",
    "dist",
    "build",
    "target",
    "clones",
}
KEY_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "llms.txt",
    "README.md",
    "package.json",
    "pyproject.toml",
    "Cargo.toml",
    "go.mod",
    "docs/APEX_CONTEXT_INDEX.md",
    "docs/APEX_TOOL_MENU.md",
    "docs/APEX_WORKSPACE_MENU.md",
    "docs/DOCUMENT_REGISTER.md",
    "registry/TOOL_INDEX.md",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_git(repo: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo),
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except Exception:
        return ""


def depth_from(root: Path, path: Path) -> int:
    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        return 999


def looks_like_project(path: Path) -> bool:
    return any((path / marker).exists() for marker in [
        ".git",
        "AGENTS.md",
        "CLAUDE.md",
        "llms.txt",
        "package.json",
        "pyproject.toml",
        "README.md",
        "Cargo.toml",
        "go.mod",
        "docs/APEX_CONTEXT_INDEX.md",
    ])


def discover_projects(root: Path, max_depth: int) -> list[Path]:
    projects: set[Path] = set()
    if not root.exists():
        return []
    if looks_like_project(root):
        projects.add(root)
    queue = [root]
    while queue:
        current = queue.pop(0)
        if depth_from(root, current) > max_depth:
            continue
        try:
            children = [p for p in current.iterdir() if p.is_dir()]
        except OSError:
            continue
        for child in children:
            if child.name in SKIP_DIRS:
                continue
            if looks_like_project(child):
                projects.add(child)
            if depth_from(root, child) < max_depth:
                queue.append(child)
    return sorted(projects, key=lambda p: str(p).lower())


def count_extensions(repo: Path, max_files: int = 5000) -> dict[str, int]:
    counts: Counter[str] = Counter()
    seen = 0
    for path in repo.rglob("*"):
        if seen >= max_files:
            break
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            seen += 1
            suffix = path.suffix.lower() or "[none]"
            counts[suffix] += 1
    return dict(counts.most_common(8))


def git_state(repo: Path) -> dict:
    is_git = run_git(repo, ["rev-parse", "--is-inside-work-tree"]) == "true"
    if not is_git:
        return {"is_git": False}
    branch = run_git(repo, ["branch", "--show-current"])
    status = run_git(repo, ["status", "--short", "--", "."])
    lines = [line for line in status.splitlines() if line.strip()]
    return {
        "is_git": True,
        "branch": branch,
        "dirty": bool(lines),
        "dirty_count": len(lines),
        "status_preview": lines[:12],
    }


def classify_project(repo: Path, key_files: list[str]) -> str:
    if "docs/APEX_CONTEXT_INDEX.md" in key_files or "registry/TOOL_INDEX.md" in key_files:
        return "APEX_GOVERNED"
    if "package.json" in key_files:
        return "NODE_APP"
    if "pyproject.toml" in key_files:
        return "PYTHON_PROJECT"
    if "Cargo.toml" in key_files:
        return "RUST_PROJECT"
    if "go.mod" in key_files:
        return "GO_PROJECT"
    if "README.md" in key_files:
        return "DOCUMENTED_REPO"
    return "UNKNOWN_PROJECT"


def summarize_project(repo: Path, root: Path) -> dict:
    present = [file for file in KEY_FILES if (repo / file).exists()]
    git = git_state(repo)
    ext_counts = count_extensions(repo)
    rel = str(repo.relative_to(root)) if repo != root and repo.is_relative_to(root) else repo.name
    return {
        "name": repo.name,
        "path": str(repo),
        "root": str(root),
        "relative_path": rel,
        "class": classify_project(repo, present),
        "key_files": present,
        "git": git,
        "extension_counts": ext_counts,
        "recommended_entry": choose_entry(present),
        "next_action": choose_next_action(present, git),
    }


def choose_entry(present: list[str]) -> str:
    for preferred in ["docs/APEX_CONTEXT_INDEX.md", "AGENTS.md", "CLAUDE.md", "llms.txt", "README.md"]:
        if preferred in present:
            return preferred
    return "inspect project root"


def choose_next_action(present: list[str], git: dict) -> str:
    if "docs/APEX_CONTEXT_INDEX.md" in present:
        return "Use Apex context/menu files before deeper reads."
    if "AGENTS.md" not in present and "CLAUDE.md" not in present and "llms.txt" not in present:
        return "Consider adding low-token AGENTS.md or llms.txt."
    if git.get("dirty"):
        return "Review dirty files before new work."
    return "Use recommended entry file."


def write_markdown(data: dict, output: Path) -> None:
    lines = [
        "# Apex Repository Menu",
        "",
        "| Field | Value |",
        "|---|---|",
        "| Ref Code | APEX-MB-DOC-00025 |",
        "| Version | 1.0 |",
        "| Status | ACTIVE |",
        "| Purpose | Low-token repository selection and state menu |",
        f"| Generated | {data['generated_at']} |",
        "",
        "## How To Use",
        "",
        "1. Pick the repo by purpose/state.",
        "2. Open only its `recommended_entry` first.",
        "3. If the repo is dirty, read its status preview before changing files.",
        "4. Add or update low-token context files for repos that lack them.",
        "",
        "## Repository Selection",
        "",
        "| Repo | Class | Git | Dirty | Entry | Next action |",
        "|---|---|---|---:|---|---|",
    ]
    for repo in data["projects"]:
        git = repo["git"]
        git_label = git.get("branch") if git.get("is_git") else "not-git"
        dirty = git.get("dirty_count", 0) if git.get("is_git") else 0
        lines.append(
            f"| `{repo['relative_path']}` | {repo['class']} | `{git_label}` | {dirty} | `{repo['recommended_entry']}` | {repo['next_action']} |"
        )
    lines += [
        "",
        "## Dirty Repo Details",
        "",
        "| Repo | Status preview |",
        "|---|---|",
    ]
    for repo in data["projects"]:
        preview = repo["git"].get("status_preview", [])
        if preview:
            joined = "<br>".join(line.replace("|", "\\|") for line in preview)
            lines.append(f"| `{repo['relative_path']}` | {joined} |")
    lines += [
        "",
        "## Source Of Truth",
        "",
        "| Need | Source |",
        "|---|---|",
        "| Machine-readable repo menu | `docs/APEX_REPO_MENU.json` |",
        "| Regenerate menu | `python registry/generate_repo_menu.py --root C:\\\\Users\\\\Owner\\\\Repos` |",
        "| Apex workspace artifacts | `docs/APEX_WORKSPACE_MENU.md` |",
        "| Apex tools | `docs/APEX_TOOL_MENU.md` |",
        "",
    ]
    output.write_text("\n".join(lines), encoding="utf-8")


def build(roots: list[Path], max_depth: int) -> dict:
    projects: list[dict] = []
    for root in roots:
        for project in discover_projects(root, max_depth):
            projects.append(summarize_project(project, root))
    seen: set[str] = set()
    unique_projects = []
    for project in projects:
        if project["path"] in seen:
            continue
        seen.add(project["path"])
        unique_projects.append(project)
    return {
        "version": "1.0",
        "generated_at": now_iso(),
        "roots": [str(root) for root in roots],
        "project_count": len(unique_projects),
        "projects": unique_projects,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate low-token repository menus.")
    parser.add_argument("--root", action="append", default=None, help="Root to scan. Repeatable.")
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--max-depth", type=int, default=2)
    args = parser.parse_args()

    roots = [Path(root).resolve() for root in (args.root or [str(path) for path in DEFAULT_ROOTS])]
    output_md = Path(args.output_md)
    output_json = Path(args.output_json)
    data = build(roots, args.max_depth)
    output_json.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    write_markdown(data, output_md)
    print(json.dumps({"status": "OK", "projects": data["project_count"], "output_md": str(output_md), "output_json": str(output_json)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
