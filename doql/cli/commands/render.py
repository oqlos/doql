"""Render command — render a template with data."""
from __future__ import annotations

import sys
import argparse
import pathlib


def cmd_render(args: argparse.Namespace) -> int:
    """Render a template with DATA sources.
    
    Template path can be relative to current directory or project root.
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    template_path = pathlib.Path(args.template)
    
    if not template_path.exists():
        template_path = root / args.template
    if not template_path.exists():
        print(f"❌ Template not found: {args.template}", file=sys.stderr)
        return 1

    print(f"🎨 Rendering {template_path.name}...")
    # TODO: Faza 1 — Jinja2 render with DATA sources
    print("⚠️  Renderer not yet implemented — stub only.")
    return 0
