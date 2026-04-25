"""Workspace `run` subcommand."""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from .discovery import DoqlProject, _discover_local
from .output import _print


def _select_run_projects(
    root: Path, max_depth: int, name_pattern: str | None
) -> list[DoqlProject]:
    """Discover and filter projects for run command."""
    projects = _discover_local(root, max_depth=max_depth)
    projects = [p for p in projects if p.has_doql]
    if name_pattern:
        pattern = re.compile(name_pattern, re.IGNORECASE)
        projects = [p for p in projects if pattern.search(p.name)]
    return projects


def _execute_single_project(
    project: DoqlProject, action: str, timeout: int, index: int, total: int
) -> tuple[bool, int]:
    """Execute doql action on a single project. Returns (success, should_break)."""
    _print(f"\n[bold cyan]━━━ [{index}/{total}] {project.name} ━━━[/]")
    try:
        result = subprocess.run(
            ["doql", action],
            cwd=str(project.path),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        _print(f"[red]  ✗ TIMEOUT after {timeout}s[/]")
        return False, False

    if result.returncode == 0:
        _print("[green]  ✓ OK[/]")
        return True, False
    else:
        _print(f"[red]  ✗ FAILED (rc={result.returncode})[/]")
        for line in (result.stderr or "").strip().splitlines()[-3:]:
            _print(f"[red]    {line}[/]")
        return False, False


def _print_dry_run_commands(projects: list[DoqlProject], action: str) -> None:
    """Print dry-run preview of commands."""
    for p in projects:
        _print(f"  cd {p.path} && doql {action}")


def _print_run_summary(success: int, total: int) -> int:
    """Print run summary and return exit code."""
    _print(f"\n[bold]Summary: [green]{success}[/]/{total}[/]")
    return 0 if success == total else 1


def _cmd_run(args: argparse.Namespace) -> int:
    """Run `doql <action>` in each project with app.doql.css."""
    root = Path(args.root).expanduser().resolve()
    projects = _select_run_projects(root, args.depth, args.name)

    if not projects:
        _print("[yellow]No projects with app.doql.css match the filters[/]")
        return 0

    _print(f"[bold]Running 'doql {args.action}' in {len(projects)} project(s)[/]")

    if args.dry_run:
        _print_dry_run_commands(projects, args.action)
        return 0

    success = 0
    for i, p in enumerate(projects, 1):
        ok, _ = _execute_single_project(p, args.action, args.timeout, i, len(projects))
        if ok:
            success += 1
        elif args.fail_fast:
            break

    return _print_run_summary(success, len(projects))
