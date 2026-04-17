"""Deploy command — deploy to environment."""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

from ...generators import deploy as deploy_gen
from ..context import BuildContext, build_context, load_spec


def _run_directive(label: str, command: str) -> int:
    """Run a shell command as a deploy directive."""
    print(f"  ▶ @{label}: {command}")
    return subprocess.call(command, shell=True)


def cmd_deploy(args: argparse.Namespace) -> int:
    """Deploy project to target environment.
    
    Supports @local/@push/@remote directives from the deploy block.
    Falls back to docker-compose if no directives are defined.
    """
    ctx = build_context(args)
    spec, env_vars = load_spec(ctx)

    target_env = getattr(args, "env", None) or "prod"
    print(f"🚀 Deploying to {target_env}...")

    deploy = spec.deploy
    directives = deploy.directives

    if directives:
        # Execute directives in order: local → push → remote
        for phase in ("local", "push", "remote"):
            cmd = directives.get(phase)
            if not cmd:
                continue
            rc = _run_directive(phase, cmd)
            if rc != 0:
                print(f"❌ @{phase} failed (exit {rc})", file=sys.stderr)
                return rc
        print("✅ Deploy complete.")
        return 0

    # Fallback: docker-compose deploy
    return deploy_gen.run(ctx, target_env=target_env)
