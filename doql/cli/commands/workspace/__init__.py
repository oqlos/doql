"""doql workspace — multi-project operations for .doql projects.

Discovers projects under a given path that contain app.doql.css manifests
and runs group operations (list, analyze, validate, fix, doctor, sync, build).

Powered by taskfile.workspace when available; falls back to a pure-Python
minimal implementation otherwise (no extra dependencies required for
the core `list`/`analyze` commands).
"""
from __future__ import annotations

import argparse

# Re-export core symbols for backward compatibility
from .discovery import (
    DoqlProject,
    EXCLUDED_FOLDERS,
    PROJECT_MARKERS,
    _discover_local,
    _parse_doql,
)
from .output import _print
from .list import _cmd_list
from .analyze import _cmd_analyze, _cmd_validate, _cmd_fix
from .run import _cmd_run

__all__ = [
    "cmd_workspace",
    "register_parser",
    "DoqlProject",
    "EXCLUDED_FOLDERS",
    "PROJECT_MARKERS",
    "_discover_local",
    "_parse_doql",
]


def cmd_workspace(args: argparse.Namespace) -> int:
    """Dispatch to the right workspace subcommand."""
    sub = getattr(args, 'workspace_cmd', None)
    if not sub:
        _print("[red]Error:[/] no workspace subcommand given. Try 'doql workspace --help'.")
        return 2
    handler = {
        'list': _cmd_list,
        'analyze': _cmd_analyze,
        'validate': _cmd_validate,
        'fix': _cmd_fix,
        'run': _cmd_run,
    }.get(sub)
    if not handler:
        _print(f"[red]Unknown workspace subcommand: {sub}[/]")
        return 2
    return handler(args)


def register_parser(sub: argparse._SubParsersAction) -> None:
    """Register `workspace` subcommands on the main doql parser."""
    ws = sub.add_parser(
        "workspace",
        help="Multi-project operations over app.doql.css manifests",
        description="Discover projects with app.doql.css and run group operations.",
    )
    ws_sub = ws.add_subparsers(dest="workspace_cmd")

    def _add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--root", "-r", default=".", help="Base path to scan (default: .)")
        p.add_argument("--depth", "-d", type=int, default=2, help="Max scan depth (default: 2)")

    # list
    p = ws_sub.add_parser("list", help="List projects with app.doql.css")
    _add_common(p)
    p.add_argument("--doql-only", action="store_true", help="Only projects with app.doql.css")
    p.add_argument("--has-workflow", help="Only projects with this workflow name")
    p.set_defaults(func=cmd_workspace)

    # analyze
    p = ws_sub.add_parser("analyze", help="Analyze all projects (table or CSV)")
    _add_common(p)
    p.add_argument("-o", "--output", help="Write CSV to file instead of stdout table")
    p.set_defaults(func=cmd_workspace)

    # validate
    p = ws_sub.add_parser("validate", help="Validate app.doql.css manifests")
    _add_common(p)
    p.add_argument("--strict", action="store_true", help="Exit 1 on any issue")
    p.set_defaults(func=cmd_workspace)

    # fix
    p = ws_sub.add_parser("fix", help="Fix common manifest errors (requires taskfile package)")
    _add_common(p)
    p.add_argument("--name", help="Filter projects by name (regex)")
    p.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    p.set_defaults(func=cmd_workspace)

    # run
    p = ws_sub.add_parser("run", help="Run `doql <action>` in every project")
    _add_common(p)
    p.add_argument("action", help="doql action to run in each project (e.g. validate, build, doctor)")
    p.add_argument("--name", help="Filter projects by name (regex)")
    p.add_argument("--timeout", type=int, default=300, help="Per-project timeout (seconds)")
    p.add_argument("--dry-run", action="store_true", help="Preview commands without executing")
    p.add_argument("--fail-fast", action="store_true", help="Stop on first failure")
    p.set_defaults(func=cmd_workspace)
