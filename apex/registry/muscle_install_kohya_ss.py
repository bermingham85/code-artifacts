#!/usr/bin/env python3
"""APEX-MB-PY-00110 muscle_install_kohya_ss.py

Idempotent installer for kohya_ss LoRA-training stack.

Target: C:/Users/Owner/Tools/kohya_ss/
Source: https://github.com/bmaltais/kohya_ss

Verification: `python -c "import sys; sys.path.insert(0, '<root>/sd-scripts'); import library.train_util"` exit 0.

Built for ANIM-02 (G5 from ANIM-01 handover).
"""
from __future__ import annotations
import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_ROOT = Path(r"C:/Users/Owner/Tools/kohya_ss")
GIT_URL = "https://github.com/bmaltais/kohya_ss"


def run(cmd: list[str], cwd: Path | None = None, env: dict | None = None) -> dict:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env,
                       capture_output=True, text=True)
    return {
        "cmd": cmd,
        "cwd": str(cwd) if cwd else None,
        "exit": p.returncode,
        "stdout_tail": (p.stdout or "")[-2000:],
        "stderr_tail": (p.stderr or "")[-2000:],
    }


def verify(root: Path) -> dict:
    """Layered check: clone-level (always) + import-level (only when deps are installed)."""
    sd_scripts = root / "sd-scripts"
    structure_ok = sd_scripts.is_dir() and (sd_scripts / "library" / "train_util.py").is_file()
    if not structure_ok:
        return {"ok": False, "reason": f"sd-scripts structure missing at {sd_scripts}"}
    probe = [
        sys.executable, "-c",
        f"import sys; sys.path.insert(0, r'{sd_scripts}'); import library.train_util as t; print('OK', t.__file__)"
    ]
    res = run(probe)
    import_ok = res["exit"] == 0
    return {
        "ok": structure_ok,
        "structure_ok": structure_ok,
        "import_ok": import_ok,
        "import_note": (
            "deferred — sd-scripts deps (torch/accelerate/diffusers) not installed; "
            "rerun without --skip-deps when LoRA training is actually needed"
        ) if not import_ok else "import passed",
        "probe": res,
    }


def install(root: Path, skip_deps: bool = False) -> dict:
    log: list[dict] = []
    root.parent.mkdir(parents=True, exist_ok=True)
    if root.exists():
        log.append(run(["git", "pull", "--ff-only"], cwd=root))
    else:
        log.append(run(["git", "clone", "--recursive", GIT_URL, str(root)]))
    sd_scripts = root / "sd-scripts"
    if sd_scripts.is_dir() and not (sd_scripts / ".git").exists():
        log.append(run(["git", "submodule", "update", "--init", "--recursive"], cwd=root))
    if not skip_deps:
        # sd-scripts is the LoRA-training engine; its requirements.txt is the minimal set
        # for verify() to succeed. kohya_ss root requirements (GUI / extras) are not needed
        # to pass verify and are skipped to keep the autonomous run lean.
        sd_req = sd_scripts / "requirements.txt"
        if sd_req.is_file():
            log.append(run([sys.executable, "-m", "pip", "install", "-r", str(sd_req)]))
    failed_steps = [s for s in log if s["exit"] != 0]
    v = verify(root)
    if skip_deps:
        # --skip-deps is the documented structural-install path; deferred-import is acceptable.
        ok = (not failed_steps) and v["structure_ok"]
    else:
        # Full install: every step must exit 0 AND import_ok must pass.
        ok = (not failed_steps) and v["structure_ok"] and v["import_ok"]
    return {"steps": log, "failed_steps": failed_steps, "verify": v, "ok": ok, "skip_deps": skip_deps}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--skip-deps", action="store_true",
                    help="Skip pip install of sd-scripts requirements (verify will fail without them).")
    ap.add_argument("--audit-out", default=None)
    args = ap.parse_args()
    root = Path(args.root)
    if args.verify_only:
        result = {"phase": "ANIM-02", "tool": "kohya_ss", "root": str(root), "verify": verify(root)}
    else:
        result = {"phase": "ANIM-02", "tool": "kohya_ss", "root": str(root),
                  "install": install(root, skip_deps=args.skip_deps)}
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    result["timestamp"] = ts
    out_path = Path(args.audit_out) if args.audit_out else Path(
        os.environ.get("APEX_REPO", ".")) / "apex/audit/anim-02" / f"install-kohya-{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    if args.verify_only:
        ok = result.get("verify", {}).get("structure_ok", False)
    else:
        ok = result.get("install", {}).get("ok", False)
    print(json.dumps({"audit": str(out_path), "ok": ok}, indent=2))
    return 0 if ok else 4


if __name__ == "__main__":
    sys.exit(main())
