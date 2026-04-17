"""Run command — run locally in dev mode."""
from __future__ import annotations

import sys
import subprocess
import argparse
import pathlib


def cmd_run(args: argparse.Namespace) -> int:
    """Run project locally in dev mode using docker-compose.
    
    Requires existing build (run `doql build` first).
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    build_dir = root / "build"
    compose = build_dir / "infra" / "docker-compose.yml"
    
    if not compose.exists():
        print("❌ No build found. Run `doql build` first.", file=sys.stderr)
        return 1
    
    return subprocess.call([
        "docker", "compose", "-f", str(compose), "up", "--build"
    ])
