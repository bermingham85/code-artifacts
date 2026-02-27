"""
repo_audit.py
=============
Reads every repo under bermingham85 via GitHub API.
For each repo: fetches file tree, reads key files (README, package.json,
main .py/.ts/.js), extracts content signals, then cross-references all repos
to find genuine overlaps at the content level - not name/date guessing.

Output:
  audit_report.json  - full machine-readable data
  audit_report.md    - human-readable summary with overlap findings

Usage:
  python tools/repo_audit.py

Requires:
  GITHUB_TOKEN set in Windows PowerToys Environment Variables
  pip install requests

This script lives in code-artifacts/tools/ and should be re-run whenever
a consolidation decision is being considered. Never archive based on names alone.
"""

import os
import sys
import json
import base64
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    import requests
except ImportError:
    sys.exit("Run: pip install requests")

# ── Config ────────────────────────────────────────────────────────────────────

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    sys.exit("GITHUB_TOKEN not found in environment. Set it via Windows PowerToys Environment Variables.")

OWNER = "bermingham85"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Files worth reading for content signals
KEY_FILES = [
    "README.md", "readme.md", "Readme.md",
    "package.json", "pyproject.toml", "setup.py",
    "STATUS.md", "CLAUDE.md", "HANDOVER.md",
    "main.py", "index.ts", "index.js", "app.py",
]

# Max chars to read per file (keep it lean)
MAX_CHARS = 3000

# Rate limit: GitHub allows 5000 req/hr authenticated
SLEEP_BETWEEN_REPOS = 0.5


# ── GitHub API helpers ────────────────────────────────────────────────────────

def gh_get(url, params=None):
    """GET with basic rate-limit retry."""
    for attempt in range(3):
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if r.status_code == 403 and "rate limit" in r.text.lower():
            wait = int(r.headers.get("Retry-After", 60))
            print(f"  Rate limited. Waiting {wait}s...")
            time.sleep(wait)
            continue
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json()
    return None


def list_repos():
    """Return all repos for OWNER (paginates automatically)."""
    repos = []
    page = 1
    while True:
        data = gh_get(
            f"https://api.github.com/user/repos",
            params={"per_page": 100, "page": page, "type": "all"}
        )
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break
        page += 1
    return [r for r in repos if r["owner"]["login"] == OWNER]


def get_tree(repo_name, branch):
    """Get full recursive file tree for a repo."""
    data = gh_get(
        f"https://api.github.com/repos/{OWNER}/{repo_name}/git/trees/{branch}",
        params={"recursive": "1"}
    )
    if not data:
        return []
    return [item for item in data.get("tree", []) if item["type"] == "blob"]


def read_file(repo_name, path):
    """Read a file from GitHub, return decoded text (up to MAX_CHARS)."""
    data = gh_get(f"https://api.github.com/repos/{OWNER}/{repo_name}/contents/{path}")
    if not data or "content" not in data:
        return None
    try:
        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        return content[:MAX_CHARS]
    except Exception:
        return None


# ── Content analysis ──────────────────────────────────────────────────────────

DOMAIN_SIGNALS = {
    "jesse_content":    ["jesse", "beanstalk", "oz", "bean", "part one", "part two", "chapter"],
    "jesse_pipeline":   ["novel factory", "audiobook", "chapter factory", "production pipeline", "elevenlabs"],
    "balding_pig":      ["balding pig", "balding-pig", "printify", "pod", "print on demand", "satirical"],
    "orchestrator":     ["orchestrat", "meta-agent", "agent registry", "multi-agent", "coordinator"],
    "n8n_workflows":    ["n8n", "workflow", "trigger", "webhook", "automation flow"],
    "mcp_server":       ["model context protocol", "mcp server", "mcp tools", "tools: ["],
    "agent_framework":  ["agent", "task center", "dispatcher", "blueprint", "worker bee"],
    "media_production": ["elevenlabs", "fal.ai", "midjourney", "animation", "lip-sync", "museTalk", "video"],
    "airbnb_property":  ["bermech", "airbnb", "hampton wood", "property management"],
    "infrastructure":   ["qnap", "cloudflare tunnel", "postgres", "supabase", "docker"],
    "finance":          ["quickbooks", "transaction", "categoris", "invoice", "bookkeep"],
    "governance_docs":  ["governance", "rules", "protocol", "do not", "never", "always", "forbidden"],
    "telegram_bot":     ["telegram", "bot token", "sendMessage", "claudeclaw"],
    "asset_management": ["asset vault", "character asset", "fal.ai", "image generation", "asset-vault"],
    "raw_data_dump":    ["raw_export", "full fidelity export", "unprocessed", "chatgpt history", "conversation export"],
}


def score_signals(text):
    """Return dict of domain -> signal count found in text."""
    text_lower = text.lower()
    scores = {}
    for domain, signals in DOMAIN_SIGNALS.items():
        count = sum(1 for s in signals if s in text_lower)
        if count:
            scores[domain] = count
    return scores


def extract_file_types(tree):
    """Return summary of file extensions present."""
    ext_counts = defaultdict(int)
    for item in tree:
        suffix = Path(item["path"]).suffix.lower()
        if suffix:
            ext_counts[suffix] += 1
    return dict(sorted(ext_counts.items(), key=lambda x: -x[1]))


def find_notable_files(tree):
    """Flag files that indicate content type (manuscripts, workflows, scripts)."""
    flags = set()
    for item in tree:
        p = item["path"].lower()
        if p.endswith(".docx") or p.endswith(".pdf"):
            flags.add("manuscript_or_docs")
        if "workflow" in p and p.endswith(".json"):
            flags.add("n8n_workflow_json")
        if "supabase" in p or "seed" in p:
            flags.add("database_seed")
        if p.endswith(".wav") or p.endswith(".mp3"):
            flags.add("audio_files")
        if "blueprint" in p:
            flags.add("blueprints")
        if ".env" in p and "example" not in p:
            flags.add("env_file_present")
        if "node_modules" in p:
            flags.add("has_node_modules")
    return sorted(flags)


# ── Main audit ────────────────────────────────────────────────────────────────

def audit_repo(repo):
    """Full content audit of a single repo. Returns structured dict."""
    name = repo["name"]
    branch = repo["default_branch"]
    print(f"  Auditing: {name} [{branch}]")

    result = {
        "name": name,
        "description": repo.get("description") or "",
        "language": repo.get("language") or "unknown",
        "updated_at": repo["updated_at"][:10],
        "created_at": repo["created_at"][:10],
        "archived": repo.get("archived", False),
        "private": repo.get("private", False),
        "open_issues": repo.get("open_issues_count", 0),
        "fork": repo.get("fork", False),
        "file_count": 0,
        "file_types": {},
        "notable_flags": [],
        "key_file_content": {},
        "domain_scores": {},
        "top_domains": [],
        "raw_text_sample": "",
    }

    # File tree
    tree = get_tree(name, branch)
    result["file_count"] = len(tree)
    result["file_types"] = extract_file_types(tree)
    result["notable_flags"] = find_notable_files(tree)

    # Key file content
    tree_paths = {item["path"] for item in tree}
    all_text = result["description"] + " "

    for key_file in KEY_FILES:
        if key_file in tree_paths:
            content = read_file(name, key_file)
            if content:
                result["key_file_content"][key_file] = content
                all_text += content + " "
                time.sleep(0.1)

    # Domain scoring
    result["domain_scores"] = score_signals(all_text)
    result["top_domains"] = sorted(
        result["domain_scores"], key=lambda d: -result["domain_scores"][d]
    )[:3]
    result["raw_text_sample"] = all_text[:500].strip()

    return result


def find_overlaps(audits):
    """
    Cross-reference all repos by domain scores.
    For each domain, list repos that scored in it, ordered by score.
    Flags where 2+ repos share the same primary domain = genuine overlap candidate.
    """
    domain_to_repos = defaultdict(list)
    for a in audits:
        for domain in a["top_domains"]:
            domain_to_repos[domain].append({
                "name": a["name"],
                "score": a["domain_scores"].get(domain, 0),
                "flags": a["notable_flags"],
                "updated": a["updated_at"],
            })

    overlaps = {}
    for domain, repos in domain_to_repos.items():
        if len(repos) > 1:
            overlaps[domain] = sorted(repos, key=lambda r: -r["score"])

    return overlaps


def write_markdown(audits, overlaps, path):
    lines = [
        "# Repo Audit Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Total repos audited: {len(audits)}",
        "",
        "---",
        "",
        "## Overlap Analysis",
        "_Repos sharing the same primary domain — review before any consolidation decision._",
        "",
    ]

    for domain, repos in sorted(overlaps.items()):
        lines.append(f"### Domain: `{domain}` ({len(repos)} repos)")
        for r in repos:
            lines.append(f"- **{r['name']}** (updated {r['updated']}, score {r['score']})")
            if r["flags"]:
                lines.append(f"  - flags: {', '.join(r['flags'])}")
        lines.append("")

    lines += [
        "---",
        "",
        "## All Repos — Content Summary",
        "",
    ]

    for a in sorted(audits, key=lambda x: x["updated_at"], reverse=True):
        lines.append(f"### {a['name']}")
        lines.append(f"- Updated: {a['updated_at']} | Language: {a['language']} | Files: {a['file_count']}")
        lines.append(f"- Description: {a['description'] or '_(none)_'}")
        lines.append(f"- Top domains: {', '.join(a['top_domains']) or '_(unclear)_'}")
        if a["notable_flags"]:
            lines.append(f"- Notable: {', '.join(a['notable_flags'])}")
        if a["archived"]:
            lines.append("- **ALREADY ARCHIVED**")
        lines.append("")

    Path(path).write_text("\n".join(lines), encoding="utf-8")


def write_json(audits, overlaps, path):
    data = {
        "generated": datetime.now().isoformat(),
        "owner": OWNER,
        "total_repos": len(audits),
        "overlaps": overlaps,
        "repos": audits,
    }
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print(f"Fetching repo list for {OWNER}...")
    repos = list_repos()
    print(f"Found {len(repos)} repos.\n")

    audits = []
    for i, repo in enumerate(repos, 1):
        print(f"[{i}/{len(repos)}]", end=" ")
        try:
            audit = audit_repo(repo)
            audits.append(audit)
        except Exception as e:
            print(f"  ERROR on {repo['name']}: {e}")
        time.sleep(SLEEP_BETWEEN_REPOS)

    print("\nCross-referencing for overlaps...")
    overlaps = find_overlaps(audits)

    out_json = "audit_report.json"
    out_md = "audit_report.md"
    write_json(audits, overlaps, out_json)
    write_markdown(audits, overlaps, out_md)

    print(f"\nDone.")
    print(f"  {out_json}  — full data")
    print(f"  {out_md}   — readable summary")
    print(f"\nOverlap domains found: {len(overlaps)}")
    for domain, repos in sorted(overlaps.items()):
        names = [r['name'] for r in repos]
        print(f"  {domain}: {', '.join(names)}")


if __name__ == "__main__":
    main()
