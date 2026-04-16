"""Deploy generated application to target environment."""
from __future__ import annotations

import subprocess
import sys


def run(ctx, target_env: str = "prod") -> int:
    """Deploy the built application."""
    compose = ctx.build_dir / "infra" / "docker-compose.yml"
    if not compose.exists():
        print("❌ No build found. Run `doql build` first.", file=sys.stderr)
        return 1

    print(f"🚀 Deploying {ctx.root.name} to {target_env}...")
    # TODO: Faza 1 — proper deploy with env switching, health checks
    return subprocess.call([
        "docker", "compose", "-f", str(compose),
        "up", "-d", "--build",
    ])
