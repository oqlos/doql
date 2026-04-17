"""Deploy command — deploy to environment."""
from __future__ import annotations

import argparse
import pathlib

from ...generators import deploy as deploy_gen
from ..context import BuildContext


def cmd_deploy(args: argparse.Namespace) -> int:
    """Deploy project to target environment.
    
    Delegates to infra_gen's deploy script.
    """
    ctx = BuildContext(
        root=pathlib.Path(getattr(args, "dir", None) or ".").resolve(),
        doql_file=pathlib.Path(getattr(args, "dir", None) or ".").resolve() / (getattr(args, "file", None) or "app.doql"),
        env_file=pathlib.Path(getattr(args, "dir", None) or ".").resolve() / ".env",
        build_dir=pathlib.Path(getattr(args, "dir", None) or ".").resolve() / "build",
        target_env=getattr(args, "env", None) or "prod",
    )
    
    print(f"🚀 Deploying to {ctx.target_env}...")
    return deploy_gen.run(ctx, target_env=ctx.target_env)
