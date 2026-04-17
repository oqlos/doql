"""Run command — run locally in dev mode."""
from __future__ import annotations

import sys
import subprocess
import argparse
import pathlib


def cmd_run(args: argparse.Namespace) -> int:
    """Run project locally in dev mode.

    Without --target: runs full stack via docker-compose.
    With --target: runs a specific interface (api, web, mobile, desktop).

    Requires existing build (run `doql build` first).
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    build_dir = root / "build"
    target = getattr(args, "target", None)

    if target:
        return _run_target(build_dir, target)

    compose = build_dir / "infra" / "docker-compose.yml"
    if not compose.exists():
        print("❌ No build found. Run `doql build` first.", file=sys.stderr)
        return 1
    return subprocess.call(["docker", "compose", "-f", str(compose), "up", "--build"])


def _run_target(build_dir: pathlib.Path, target: str) -> int:
    """Run a specific interface target."""
    target_dir = build_dir / target
    if not target_dir.exists():
        print(f"❌ Target '{target}' not found in build/. Run `doql build` first.", file=sys.stderr)
        return 1

    if target == "api":
        req = target_dir / "requirements.txt"
        if req.exists():
            subprocess.call([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)])
        print(f"🚀 Starting API: http://localhost:8000")
        return subprocess.call(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
            cwd=target_dir,
        )

    if target == "web":
        pkg = target_dir / "package.json"
        if not pkg.exists():
            print("❌ build/web/package.json not found.", file=sys.stderr)
            return 1
        subprocess.call(["npm", "install"], cwd=target_dir)
        print(f"🚀 Starting Web: http://localhost:5173")
        return subprocess.call(["npm", "run", "dev"], cwd=target_dir)

    if target == "mobile":
        print(f"🚀 Starting Mobile (PWA): http://localhost:8091")
        return subprocess.call(
            [sys.executable, "-m", "http.server", "8091"],
            cwd=target_dir,
        )

    if target == "desktop":
        pkg = target_dir / "package.json"
        if not pkg.exists():
            print("❌ build/desktop/package.json not found.", file=sys.stderr)
            return 1
        subprocess.call(["npm", "install"], cwd=target_dir)
        print(f"🚀 Starting Desktop (Tauri)...")
        return subprocess.call(["npm", "run", "dev"], cwd=target_dir)

    print(f"❌ Unknown target '{target}'. Use: api, web, mobile, desktop", file=sys.stderr)
    return 1
