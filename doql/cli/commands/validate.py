"""Validate command — validate .doql + .env."""
from __future__ import annotations

import sys
import argparse
import pathlib

from ... import parser as doql_parser


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate .doql file and .env configuration.
    
    Returns:
        0 if validation passes, 1 if there are errors
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    doql_file = root / (getattr(args, "file", None) or "app.doql")
    env_file = root / ".env"
    
    print(f"🔍 Validating {doql_file}...")
    
    try:
        spec = doql_parser.parse_file(doql_file)
        env_vars = doql_parser.parse_env(env_file)
        issues = doql_parser.validate(spec, env_vars, project_root=root)
    except doql_parser.DoqlParseError as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 1

    if not issues:
        print("✅ Everything looks good.")
        return 0

    errors = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")
    
    for issue in issues:
        level = "❌" if issue.severity == "error" else "⚠️ "
        print(f"{level} {issue.path}: {issue.message}")
    
    print(f"\n  {errors} error(s), {warnings} warning(s)")
    return 1 if errors > 0 else 0
