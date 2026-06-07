#!/usr/bin/env python3
"""APEX-MB-PY-00111 muscle_install_hunyuanvideo.py

Idempotent installer for ComfyUI-HunyuanVideoWrapper custom nodes.

Target: C:/ComfyUI/custom_nodes/ComfyUI-HunyuanVideoWrapper/
Source: https://github.com/kijai/ComfyUI-HunyuanVideoWrapper

Nodes-only install completes without weight downloads. Weights are gated behind
--download-weights to keep the multi-GB pull off the autonomous path; operator
runs that flag explicitly once bandwidth/time permits.

Built for ANIM-02 (G4 from ANIM-01 handover).
"""
from __future__ import annotations
import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_CUSTOM_NODES = Path(r"C:/ComfyUI/custom_nodes")
NODE_DIR_NAME = "ComfyUI-HunyuanVideoWrapper"
GIT_URL = "https://github.com/kijai/ComfyUI-HunyuanVideoWrapper"

# Weight URLs — listed for operator-gated --download-weights run.
WEIGHTS = [
    {
        "name": "hunyuan_video_720_cfgdistill_fp8_e4m3fn.safetensors",
        "url": "https://huggingface.co/Kijai/HunyuanVideo_comfy/resolve/main/hunyuan_video_720_cfgdistill_fp8_e4m3fn.safetensors",
        "dest_subdir": "diffusion_models",
        "approx_size_gb": 13,
    },
    {
        "name": "hunyuan_video_vae_bf16.safetensors",
        "url": "https://huggingface.co/Kijai/HunyuanVideo_comfy/resolve/main/hunyuan_video_vae_bf16.safetensors",
        "dest_subdir": "vae",
        "approx_size_gb": 1,
    },
]
COMFY_MODELS_ROOT = Path(r"C:/ComfyUI/models")


def run(cmd: list[str], cwd: Path | None = None) -> dict:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    return {"cmd": cmd, "cwd": str(cwd) if cwd else None, "exit": p.returncode,
            "stdout_tail": (p.stdout or "")[-2000:], "stderr_tail": (p.stderr or "")[-2000:]}


def verify(node_dir: Path) -> dict:
    if not node_dir.is_dir():
        return {"ok": False, "reason": f"node dir missing: {node_dir}"}
    has_init = (node_dir / "__init__.py").is_file()
    has_nodes = any(node_dir.glob("nodes*.py")) or (node_dir / "nodes.py").is_file()
    return {"ok": has_init and has_nodes,
            "node_dir": str(node_dir),
            "has_init_py": has_init,
            "has_nodes_py": has_nodes}


def install_nodes(custom_nodes_root: Path, python_exe: str) -> dict:
    custom_nodes_root.mkdir(parents=True, exist_ok=True)
    node_dir = custom_nodes_root / NODE_DIR_NAME
    log: list[dict] = []
    if node_dir.exists():
        log.append(run(["git", "pull", "--ff-only"], cwd=node_dir))
    else:
        log.append(run(["git", "clone", GIT_URL, str(node_dir)]))
    req = node_dir / "requirements.txt"
    if req.is_file():
        log.append(run([python_exe, "-m", "pip", "install", "-r", str(req)]))
    return {"steps": log, "verify": verify(node_dir), "python_used": python_exe}


def download_weights(target_root: Path) -> dict:
    target_root.mkdir(parents=True, exist_ok=True)
    log: list[dict] = []
    for w in WEIGHTS:
        dest_dir = target_root / w["dest_subdir"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / w["name"]
        if dest.is_file():
            log.append({"weight": w["name"], "status": "already-present", "path": str(dest)})
            continue
        # Use curl; resumes via -C - if interrupted on retry.
        log.append(run(["curl", "-L", "-C", "-", "-o", str(dest), w["url"]]))
    return {"steps": log}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--custom-nodes-root", default=str(DEFAULT_CUSTOM_NODES))
    ap.add_argument("--python", default=sys.executable,
                    help="Python interpreter to install requirements into. "
                         "Defaults to sys.executable (this box's ComfyUI uses system Python; "
                         "override when a venv is introduced).")
    ap.add_argument("--download-weights", action="store_true",
                    help="Operator-gated: pull multi-GB weight files from HuggingFace.")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--audit-out", default=None)
    args = ap.parse_args()
    root = Path(args.custom_nodes_root)
    node_dir = root / NODE_DIR_NAME
    result: dict = {"phase": "ANIM-02", "tool": "HunyuanVideoWrapper"}
    if args.verify_only:
        result["verify"] = verify(node_dir)
    else:
        result["install"] = install_nodes(root, args.python)
        if args.download_weights:
            result["weights"] = download_weights(COMFY_MODELS_ROOT)
        else:
            result["weights_deferred"] = {"reason": "operator-gated; rerun with --download-weights",
                                          "urls": WEIGHTS}
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    result["timestamp"] = ts
    out_path = Path(args.audit_out) if args.audit_out else Path(
        os.environ.get("APEX_REPO", ".")) / "apex/audit/anim-02" / f"install-hunyuanvideo-{ts}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    ok = (result.get("verify") or result.get("install", {}).get("verify") or {}).get("ok", False)
    print(json.dumps({"audit": str(out_path), "ok": ok}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
