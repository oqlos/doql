"""Docs command — generate documentation site."""
from __future__ import annotations

import argparse
import pathlib

from ... import parser as doql_parser
from ...generators import docs_gen


def cmd_docs(args: argparse.Namespace) -> int:
    """Generate documentation site from .doql spec."""
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    doql_file = root / (getattr(args, "file", None) or "app.doql")
    
    spec = doql_parser.parse_file(doql_file)
    out = root / "docs"
    
    docs_gen.generate(spec, out)
    print(f"📚 Docs generated in {out}")
    return 0
