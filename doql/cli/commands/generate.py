"""Generate command — generate a single document/artifact."""
from __future__ import annotations

import sys
import argparse
import pathlib

from ... import parser as doql_parser


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate a single document/artifact.
    
    The artifact name must match a DOCUMENT defined in the .doql file.
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    doql_file = root / (getattr(args, "file", None) or "app.doql")
    
    spec = doql_parser.parse_file(doql_file)
    artifact = args.artifact

    # Find matching DOCUMENT in spec
    doc = next((d for d in spec.documents if d.name == artifact), None)
    if not doc:
        available = [d.name for d in spec.documents]
        print(f"❌ Unknown artifact '{artifact}'. Available: {available}", file=sys.stderr)
        return 1

    print(f"📄 Generating {artifact} ({doc.type})...")
    # TODO: Faza 1 — Jinja2 + WeasyPrint pipeline
    print(f"   Template: {doc.template or '(none)'}")
    print(f"   Output: {doc.output or f'{artifact}.{doc.type}'}")
    print("⚠️  Generator not yet implemented — stub only.")
    return 0
