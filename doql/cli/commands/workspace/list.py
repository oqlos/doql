"""Workspace `list` subcommand."""
from __future__ import annotations

import argparse
from pathlib import Path

from .discovery import DoqlProject, _discover_local, _filter_projects
from .output import _HAS_RICH, _print

if _HAS_RICH:
    from rich import box
    from rich.table import Table
    from rich.console import Console
    console = Console()
else:
    console = None


def _print_project_table(projects: list[DoqlProject], root: Path) -> None:
    """Print projects as rich table or plain text."""
    if _HAS_RICH:
        table = Table(title=f"doql projects in {root}", box=box.ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="green")
        table.add_column("Path", style="dim")
        table.add_column("doql", justify="center")
        table.add_column("Workflows", justify="right")
        table.add_column("Entities", justify="right")
        table.add_column("DBs", justify="right")
        table.add_column("UIs", justify="right")
        for i, p in enumerate(projects, 1):
            table.add_row(
                str(i), p.name, str(p.path),
                "✓" if p.has_doql else "—",
                str(len(p.doql_workflows)),
                str(len(p.doql_entities)),
                str(len(p.doql_databases)),
                str(len(p.doql_interfaces)),
            )
        console.print(table)
    else:
        for p in projects:
            print(f"{p.name}\t{p.path}\tworkflows={len(p.doql_workflows)}")


def _cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        _print(f"[red]Error:[/] Path not found: {root}")
        return 1

    projects = _discover_local(root, max_depth=args.depth)
    projects = _filter_projects(projects, args.doql_only, args.has_workflow)

    if not projects:
        _print("[yellow]No projects match the filters.[/]")
        return 0

    _print_project_table(projects, root)

    _print(f"[dim]Scanned:[/] {root}  [bold]{len(projects)}[/] projects  "
           f"[cyan]{sum(1 for p in projects if p.has_doql)}[/] with app.doql.css")
    return 0
