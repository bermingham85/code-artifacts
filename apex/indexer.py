"""
indexer.py — Registry Indexer
Ref:        APEX-MB-PY-00001
Version:    1.0
Author:     MB / SYS
Description: Scans local folders and GitHub repos. Builds manifest.json.
             Enforces Reuse > Research > Create via AST-based skill discovery.
             Incremental: skips files unchanged since last index (mtime cache).

Usage:
    python indexer.py --scan               # Full re-index (incremental)
    python indexer.py --scan --force       # Re-index everything regardless of mtime
    python indexer.py --search "keyword"   # Ranked keyword search
    python indexer.py --stats              # Summary stats
    python indexer.py --watch              # Hot-reload: watch registry/ for changes
"""

import argparse
import ast
import fnmatch
import hashlib
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
APEX_ROOT     = Path(__file__).parent
REGISTRY_DIR  = APEX_ROOT / "registry"
MANIFEST_FILE = REGISTRY_DIR / "manifest.json"
SOURCES_FILE  = REGISTRY_DIR / "sources.json"
LOG_FILE      = APEX_ROOT / "logs" / "indexer.log"
CLONES_DIR    = REGISTRY_DIR / "clones"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("indexer")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_sources() -> dict:
    if not SOURCES_FILE.exists():
        log.error(f"sources.json not found at {SOURCES_FILE}")
        sys.exit(1)
    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_manifest() -> dict:
    if not MANIFEST_FILE.exists():
        return {"last_indexed": None, "skills": [], "duplicates": []}
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_manifest(manifest: dict):
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def _is_excluded(path: Path, patterns: list[str]) -> bool:
    path_str = path.as_posix()
    for pat in patterns:
        if fnmatch.fnmatch(path_str, pat):
            return True
        # Also check each component
        for part in path.parts:
            if fnmatch.fnmatch(part, pat.strip("*/")):
                return True
    return False


def _mtime_iso(path: Path) -> str:
    try:
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    except Exception:
        return _now_iso()


def _ast_hash(source: str) -> str:
    """SHA-256 of the AST dump — catches renamed-but-identical functions."""
    try:
        tree = ast.parse(source)
        return hashlib.sha256(ast.dump(tree).encode()).hexdigest()
    except SyntaxError:
        return hashlib.sha256(source.encode()).hexdigest()


def _extract_skills(file_path: Path, source_label: str, repo: str | None,
                    exclude_patterns: list[str]) -> list[dict]:
    """
    Parse a .py file with AST, return list of skill dicts.
    Each top-level function becomes a skill entry.
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        log.warning(f"Cannot read {file_path}: {e}")
        return []

    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        log.warning(f"Syntax error in {file_path}: {e}")
        return []

    skills = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        # Only top-level functions (parent is Module)
        # ast.walk doesn't give parent, use a simpler heuristic:
        # if col_offset == 0 it's top-level
        if node.col_offset != 0:
            continue

        docstring = ast.get_docstring(node) or ""
        imports = [
            ast.unparse(n)
            for n in ast.walk(tree)
            if isinstance(n, (ast.Import, ast.ImportFrom))
        ][:20]  # cap at 20 to avoid noise

        # Hash the function body source
        try:
            func_src = ast.get_source_segment(text, node) or ""
            func_hash = hashlib.sha256(func_src.encode()).hexdigest()
        except Exception:
            func_hash = _ast_hash(text)

        # callable_as_muscle: true if it has argparse in imports or "argparse" in source
        callable_as_muscle = "argparse" in text or node.name.startswith("muscle_")

        skills.append({
            "id":               str(uuid.uuid4()),
            "ref_code":         "APEX-SYS-PY-00000",  # placeholder; doc_controller assigns real one
            "name":             node.name,
            "file":             str(file_path),
            "source":           source_label,
            "repo":             repo,
            "docstring":        docstring[:500],
            "imports":          list(set(imports)),
            "ast_hash":         func_hash,
            "last_modified":    _mtime_iso(file_path),
            "tags":             [],
            "callable_as_muscle": callable_as_muscle,
        })

    return skills


def _collect_py_files(base_path: Path, exclude_patterns: list[str]) -> list[Path]:
    files = []
    if not base_path.exists():
        log.warning(f"Path does not exist, skipping: {base_path}")
        return files
    for py_file in base_path.rglob("*.py"):
        if not _is_excluded(py_file, exclude_patterns):
            files.append(py_file)
    return files


def _clone_or_pull(repo_url: str) -> Path | None:
    """Clone repo into registry/clones/. Pull if already cloned."""
    repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    dest = CLONES_DIR / repo_name
    CLONES_DIR.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        log.info(f"Pulling {repo_name}...")
        result = subprocess.run(
            ["git", "pull"], cwd=str(dest), capture_output=True, text=True
        )
        if result.returncode != 0:
            log.warning(f"git pull failed for {repo_name}: {result.stderr.strip()}")
        return dest
    else:
        log.info(f"Cloning {repo_url} into {dest}...")
        result = subprocess.run(
            ["git", "clone", repo_url, str(dest)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            log.warning(f"git clone failed for {repo_url}: {result.stderr.strip()}")
            return None
        return dest


# ---------------------------------------------------------------------------
# Core scan
# ---------------------------------------------------------------------------

def run_scan(force: bool = False) -> dict:
    """
    Full index pass. Returns the new manifest dict.
    """
    t_start = time.time()
    sources = _load_sources()
    exclude_patterns = sources.get("exclude_patterns", [])

    # Build mtime cache from existing manifest for incremental indexing
    existing = _load_manifest()
    mtime_cache: dict[str, str] = {}  # file_path -> last_modified
    if not force:
        for skill in existing.get("skills", []):
            f = skill.get("file", "")
            if f:
                mtime_cache[f] = skill.get("last_modified", "")

    all_skills: list[dict] = []
    total_files = 0

    # ---- Local paths ----
    for local_path_str in sources.get("local_paths", []):
        local_path = Path(local_path_str)
        py_files = _collect_py_files(local_path, exclude_patterns)
        for py_file in py_files:
            total_files += 1
            current_mtime = _mtime_iso(py_file)
            if not force and mtime_cache.get(str(py_file)) == current_mtime:
                # Unchanged — carry forward existing skills for this file
                for s in existing.get("skills", []):
                    if s.get("file") == str(py_file):
                        all_skills.append(s)
                continue
            skills = _extract_skills(py_file, "local", None, exclude_patterns)
            all_skills.extend(skills)
            log.debug(f"Indexed {py_file} → {len(skills)} skill(s)")

    # ---- GitHub repos ----
    for repo_url in sources.get("github_repos", []):
        repo_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
        clone_path = _clone_or_pull(repo_url)
        if clone_path is None:
            continue
        py_files = _collect_py_files(clone_path, exclude_patterns)
        for py_file in py_files:
            total_files += 1
            current_mtime = _mtime_iso(py_file)
            if not force and mtime_cache.get(str(py_file)) == current_mtime:
                for s in existing.get("skills", []):
                    if s.get("file") == str(py_file):
                        all_skills.append(s)
                continue
            skills = _extract_skills(py_file, "github", repo_name, exclude_patterns)
            all_skills.extend(skills)

    # ---- Deduplicate by AST hash ----
    seen_hashes: dict[str, str] = {}
    duplicates: list[dict] = []
    deduped: list[dict] = []
    for skill in all_skills:
        h = skill["ast_hash"]
        if h in seen_hashes:
            duplicates.append({
                "hash":    h,
                "name":    skill["name"],
                "file":    skill["file"],
                "clash_with": seen_hashes[h],
            })
        else:
            seen_hashes[h] = skill["file"]
            deduped.append(skill)

    duration = round(time.time() - t_start, 2)
    manifest = {
        "last_indexed":          _now_iso(),
        "index_duration_seconds": duration,
        "total_skills":          len(deduped),
        "total_files":           total_files,
        "skills":                deduped,
        "duplicates":            duplicates,
    }
    _save_manifest(manifest)
    log.info(
        f"Index complete: {len(deduped)} skills, {total_files} files, "
        f"{len(duplicates)} duplicate(s), {duration}s"
    )
    return manifest


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_search(query: str):
    manifest = _load_manifest()
    q = query.lower()
    results = []
    for skill in manifest.get("skills", []):
        score = 0
        if q in skill["name"].lower():
            score += 3
        if q in skill.get("docstring", "").lower():
            score += 2
        if q in skill.get("file", "").lower():
            score += 1
        if score > 0:
            results.append((score, skill))
    results.sort(key=lambda x: x[0], reverse=True)
    if not results:
        print(f"[indexer] No matches for '{query}'")
        return
    print(f"[indexer] {len(results)} match(es) for '{query}':")
    for score, s in results[:20]:
        print(f"  [{score}] {s['name']} — {s['file']}")
        if s.get("docstring"):
            print(f"       {s['docstring'][:100]}")


def cmd_stats():
    manifest = _load_manifest()
    print(f"[indexer] Last indexed:  {manifest.get('last_indexed', 'never')}")
    print(f"[indexer] Total skills:  {manifest.get('total_skills', 0)}")
    print(f"[indexer] Total files:   {manifest.get('total_files', 0)}")
    print(f"[indexer] Duplicates:    {len(manifest.get('duplicates', []))}")
    print(f"[indexer] Index time:    {manifest.get('index_duration_seconds', 0)}s")
    # Foreman heartbeat age
    heartbeat = APEX_ROOT / "hub" / ".heartbeat"
    if heartbeat.exists():
        age = time.time() - heartbeat.stat().st_mtime
        print(f"[indexer] Heartbeat age: {int(age)}s")
    else:
        print(f"[indexer] Heartbeat:     not found")


def cmd_watch():
    """Hot-reload: re-index whenever a .py file in registry/ changes."""
    log.info("[indexer] Watch mode started (Ctrl+C to stop)")
    last_scan = 0.0
    try:
        while True:
            # Check if any .py in registry changed more recently than last scan
            changed = False
            for py_file in REGISTRY_DIR.rglob("*.py"):
                if py_file.stat().st_mtime > last_scan:
                    changed = True
                    break
            if changed:
                log.info("[indexer] Change detected — re-indexing...")
                run_scan()
                last_scan = time.time()
            time.sleep(5)
    except KeyboardInterrupt:
        log.info("[indexer] Watch mode stopped")


def main():
    parser = argparse.ArgumentParser(description="Apex Registry Indexer")
    parser.add_argument("--scan",   action="store_true", help="Run index scan")
    parser.add_argument("--force",  action="store_true", help="Force full re-index (ignore mtime cache)")
    parser.add_argument("--search", type=str,            help="Search skills by keyword")
    parser.add_argument("--stats",  action="store_true", help="Print index statistics")
    parser.add_argument("--watch",  action="store_true", help="Hot-reload watch mode")
    args = parser.parse_args()

    if args.scan:
        run_scan(force=args.force)
    elif args.search:
        cmd_search(args.search)
    elif args.stats:
        cmd_stats()
    elif args.watch:
        cmd_watch()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
