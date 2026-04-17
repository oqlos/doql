"""Build context and helper functions for doql CLI."""
from __future__ import annotations

import argparse
import pathlib
from dataclasses import dataclass
from typing import Optional

from .. import __version__
from .. import parser as doql_parser


@dataclass
class BuildContext:
    """Build context for doql commands."""
    root: pathlib.Path
    doql_file: pathlib.Path
    env_file: pathlib.Path
    build_dir: pathlib.Path
    target_env: str = "dev"


def build_context(args: argparse.Namespace) -> BuildContext:
    """Create BuildContext from CLI arguments."""
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    return BuildContext(
        root=root,
        doql_file=root / (getattr(args, "file", None) or "app.doql"),
        env_file=root / ".env",
        build_dir=root / "build",
    )


def load_spec(ctx: BuildContext) -> tuple:
    """Parse spec and env, return (spec, env_vars)."""
    spec = doql_parser.parse_file(ctx.doql_file)
    env_vars = doql_parser.parse_env(ctx.env_file)
    return spec, env_vars


def scaffold_from_template(template: str, target: pathlib.Path) -> None:
    """Copy scaffold template to target directory."""
    import shutil
    templates_dir = pathlib.Path(__file__).parent.parent / "scaffolds" / template
    if not templates_dir.exists():
        raise SystemExit(f"Template '{template}' not found")
    shutil.copytree(templates_dir, target)


def estimate_file_count(iface) -> int:
    """Rough estimate of file count per interface type."""
    if iface.type == "rest":
        return len(iface.entities) * 4 + 10  # model + schema + route + test + config
    if iface.type in ("spa", "react", "vue"):
        return len(iface.pages) * 2 + 20
    if iface.type == "pwa":
        return 10
    if iface.type in ("electron", "tauri"):
        return 15
    return 5
