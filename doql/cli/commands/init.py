"""Init command — create new project from template."""
from __future__ import annotations

import sys
import argparse
import pathlib

from ..context import scaffold_from_template


def cmd_init(args: argparse.Namespace) -> int:
    """Create new project from template.
    
    With --list-templates, shows available templates and exits.
    """
    if getattr(args, "list_templates", False):
        scaffolds_dir = pathlib.Path(__file__).parent.parent.parent / "scaffolds"
        templates = sorted(p.name for p in scaffolds_dir.iterdir() if p.is_dir())
        print("Available doql templates:")
        for t in templates:
            doql = scaffolds_dir / t / "app.doql"
            first_line = ""
            if doql.exists():
                with doql.open() as fh:
                    first_line = fh.readline().strip()
            print(f"  {t:24} — {first_line}")
        return 0

    template = args.template or "minimal"
    target = pathlib.Path(args.name)
    if target.exists():
        print(f"❌ Directory {target} already exists", file=sys.stderr)
        return 1

    print(f"📦 Scaffolding {target} from template '{template}'...")
    scaffold_from_template(template, target)
    print(f"✅ Created {target}/")
    print(f"   Next steps:")
    print(f"     cd {target}")
    print(f"     cp .env.example .env && $EDITOR .env")
    print(f"     doql validate")
    print(f"     doql build")
    return 0
