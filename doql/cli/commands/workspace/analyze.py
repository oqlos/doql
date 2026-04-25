"""Workspace `analyze`, `validate`, and `fix` subcommands."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .discovery import DoqlProject, _discover_local, _load_project_doql
from .output import _HAS_RICH, _HAS_TASKFILE, _print

if _HAS_RICH:
    from rich import box
    from rich.table import Table
    from rich.console import Console
    console = Console()
else:
    console = None


def _analyze_workflow_issues(content: str) -> list[str]:
    """Detect empty workflows in doql content."""
    import re
    issues = []
    for wf_match in re.finditer(
        r'workflow\[name="([^"]+)"\]\s*\{([^}]*)\}',
        content, re.DOTALL,
    ):
        wf_name, wf_body = wf_match.group(1), wf_match.group(2)
        if 'step-1:' not in wf_body and 'step-' not in wf_body:
            issues.append(f"Empty workflow '{wf_name}'")
    return issues


def _analyze_content_issues(content: str) -> list[str]:
    """Detect structural issues in doql content."""
    issues = []
    if 'app {' not in content:
        issues.append("Missing app { } section")
    return issues


def _analyze_content_recs(content: str, project: DoqlProject) -> list[str]:
    """Generate recommendations based on doql content."""
    recs = []
    if 'deploy {' not in content:
        recs.append("Consider adding deploy { } section")
    if not project.doql_databases and project.doql_entities:
        recs.append("Has entities but no database section")
    return recs


def _analyze_project(project: DoqlProject) -> dict:
    """Analyze a single project and return analysis row."""
    issues = []
    recs = []
    
    if not project.has_doql:
        issues.append("Missing app.doql.css")
    else:
        try:
            content = (project.path / "app.doql.css").read_text()
        except OSError:
            content = ""
        issues.extend(_analyze_workflow_issues(content))
        issues.extend(_analyze_content_issues(content))
        recs.extend(_analyze_content_recs(content, project))

    return {
        'path': str(project.path),
        'name': project.name,
        'app_name': project.doql_app_name,
        'app_version': project.doql_app_version,
        'workflows': len(project.doql_workflows),
        'entities': len(project.doql_entities),
        'databases': len(project.doql_databases),
        'interfaces': len(project.doql_interfaces),
        'has_taskfile': project.has_taskfile,
        'issues': issues,
        'recommendations': recs,
    }


def _output_csv(rows: list[dict], output_path: str) -> None:
    """Write analysis results to CSV file."""
    fieldnames = [
        'path', 'name', 'app_name', 'app_version',
        'workflows', 'entities', 'databases', 'interfaces',
        'has_taskfile', 'issues', 'recommendations',
    ]
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            r = dict(r)
            r['issues'] = ' | '.join(r['issues'])
            r['recommendations'] = ' | '.join(r['recommendations'])
            w.writerow(r)
    _print(f"[green]Wrote CSV:[/] {output_path}  ({len(rows)} rows)")


def _output_table(rows: list[dict]) -> None:
    """Print analysis results as formatted table."""
    if _HAS_RICH:
        table = Table(title=f"doql analysis — {len(rows)} projects", box=box.ROUNDED)
        table.add_column("#", style="dim", width=4)
        table.add_column("Project", style="green")
        table.add_column("App (version)", style="cyan")
        table.add_column("WF", justify="right")
        table.add_column("Ent", justify="right")
        table.add_column("DB", justify="right")
        table.add_column("Issues", style="red")
        table.add_column("Recs", style="yellow")
        total_issues = 0
        total_recs = 0
        for i, r in enumerate(rows, 1):
            total_issues += len(r['issues'])
            total_recs += len(r['recommendations'])
            issues_str = '; '.join(r['issues']) if r['issues'] else '—'
            recs_str = '; '.join(r['recommendations']) if r['recommendations'] else '—'
            if len(issues_str) > 40:
                issues_str = issues_str[:37] + '...'
            if len(recs_str) > 40:
                recs_str = recs_str[:37] + '...'
            app_info = r['app_name']
            if r['app_version']:
                app_info += f" ({r['app_version']})"
            table.add_row(
                str(i), r['name'], app_info or '—',
                str(r['workflows']), str(r['entities']), str(r['databases']),
                issues_str, recs_str,
            )
        console.print(table)
        console.print(
            f"\n[bold]{len(rows)} projects · "
            f"[red]{total_issues} issues[/] · "
            f"[yellow]{total_recs} recommendations[/]"
        )
    else:
        for r in rows:
            print(r)


def _cmd_analyze(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        _print(f"[red]Error:[/] Path not found: {root}")
        return 1

    projects = _discover_local(root, max_depth=args.depth)
    rows = [_analyze_project(p) for p in projects]

    if args.output:
        _output_csv(rows, args.output)
        return 0

    _output_table(rows)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    if _HAS_TASKFILE:
        from .output import _tf_discover, _tf_validate
        root = Path(args.root).expanduser().resolve()
        projects = _tf_discover(root, max_depth=args.depth)
        total = 0
        for p in projects:
            issues = _tf_validate(p)
            if issues:
                total += len(issues)
                _print(f"[red]{p.name}[/]: {'; '.join(issues)}")
            else:
                _print(f"[green]{p.name}[/]: ok")
        _print(f"\n[bold]{total} issue(s) across {len(projects)} project(s)[/]")
        return 1 if (args.strict and total > 0) else 0

    # Fallback
    args.output = None
    return _cmd_analyze(args)


def _cmd_fix(args: argparse.Namespace) -> int:
    if not _HAS_TASKFILE:
        _print("[red]Error:[/] `doql workspace fix` requires the `taskfile` package.")
        _print("[dim]Install with: pip install taskfile[/]")
        return 1

    from .output import _tf_discover, _tf_filter, _tf_fix
    root = Path(args.root).expanduser().resolve()
    projects = _tf_discover(root, max_depth=args.depth)
    if args.name:
        projects = _tf_filter(projects, name_pattern=args.name)

    changed = 0
    for p in projects:
        if args.dry_run:
            issues = _tf_validate(p)
            if issues:
                _print(f"[cyan]{p.name}[/]: {'; '.join(issues)}")
                changed += 1
            continue
        result = _tf_fix(p)
        if result.changed:
            _print(f"[green]{p.name}[/]: {result.summary()}")
            changed += 1

    _print(f"\n[bold]Fixed {changed}/{len(projects)} project(s)[/]")
    return 0
