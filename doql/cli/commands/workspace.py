"""doql workspace — multi-project operations for .doql projects.

Discovers projects under a given path that contain app.doql.css manifests
and runs group operations (list, analyze, validate, fix, doctor, sync, build).

Powered by taskfile.workspace when available; falls back to a pure-Python
minimal implementation otherwise (no extra dependencies required for
the core `list`/`analyze` commands).
"""
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    from rich import box
    from rich.console import Console
    from rich.table import Table
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

# Try the canonical implementation from taskfile if installed
try:
    from taskfile.workspace import (
        Project as TaskfileProject,
        discover_projects as _tf_discover,
        filter_projects as _tf_filter,
        analyze_project as _tf_analyze,
        validate_project as _tf_validate,
        fix_project as _tf_fix,
    )
    _HAS_TASKFILE = True
except ImportError:
    _HAS_TASKFILE = False


console = Console() if _HAS_RICH else None


# Fallback: minimal local implementation focused on .doql.css discovery

EXCLUDED_FOLDERS = frozenset({
    'venv', '.venv', 'node_modules', '__pycache__',
    '.git', '.idea', '.pytest_cache', '.ruff_cache',
    'dist', 'build', '.code2llm_cache', 'logs',
    'iql-run-logs', 'oql-run-logs', 'refactor_output',
})

# Markers that identify a real project (not a docs/logs folder)
PROJECT_MARKERS = (
    'pyproject.toml', 'package.json', 'Dockerfile',
    'setup.py', 'Makefile', 'Taskfile.yml',
)


@dataclass
class DoqlProject:
    """Minimal project descriptor (used when taskfile is not installed)."""
    path: Path
    name: str
    has_doql: bool = False
    has_taskfile: bool = False
    doql_workflows: list[str] = field(default_factory=list)
    doql_entities: list[str] = field(default_factory=list)
    doql_databases: list[str] = field(default_factory=list)
    doql_interfaces: list[str] = field(default_factory=list)
    doql_app_name: str = ""
    doql_app_version: str = ""


def _is_project(d: Path) -> bool:
    return any((d / m).exists() for m in PROJECT_MARKERS)


def _parse_doql(content: str) -> dict:
    return {
        "workflows": re.findall(r'workflow\[name="([^"]+)"\]', content),
        "entities": re.findall(r'entity\[name="([^"]+)"\]', content),
        "databases": re.findall(r'database\[name="([^"]+)"\]', content),
        "interfaces": re.findall(r'interface\[type="([^"]+)"\]', content),
        "app_name": (re.search(r'app\s*\{[^}]*name:\s*"([^"]+)"', content) or [""])[0],
        "app_version": (re.search(r'app\s*\{[^}]*version:\s*"([^"]+)"', content, re.DOTALL) or [""])[0],
    }


def _discover_local(root: Path, max_depth: int = 2) -> list[DoqlProject]:
    """Walk `root` up to `max_depth` levels, collect projects with manifests."""
    projects: list[DoqlProject] = []

    def _walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return
        try:
            entries = list(current.iterdir())
        except (PermissionError, OSError):
            return
        for entry in entries:
            if not entry.is_dir():
                continue
            if entry.name.startswith('.'):
                continue
            if entry.name in EXCLUDED_FOLDERS:
                continue
            if _is_project(entry):
                proj = DoqlProject(path=entry, name=entry.name)
                proj.has_taskfile = (entry / 'Taskfile.yml').exists()
                doql_path = entry / 'app.doql.css'
                proj.has_doql = doql_path.exists()
                if proj.has_doql:
                    try:
                        info = _parse_doql(doql_path.read_text())
                        proj.doql_workflows = info["workflows"]
                        proj.doql_entities = info["entities"]
                        proj.doql_databases = info["databases"]
                        proj.doql_interfaces = info["interfaces"]
                        m_name = re.search(r'app\s*\{[^}]*name:\s*"([^"]+)"', proj.path.joinpath('app.doql.css').read_text(), re.DOTALL)
                        if m_name:
                            proj.doql_app_name = m_name.group(1)
                        m_ver = re.search(r'app\s*\{[^}]*version:\s*"([^"]+)"', proj.path.joinpath('app.doql.css').read_text(), re.DOTALL)
                        if m_ver:
                            proj.doql_app_version = m_ver.group(1)
                    except OSError:
                        pass
                projects.append(proj)
            elif depth < max_depth:
                _walk(entry, depth + 1)

    _walk(root.resolve(), 1)
    projects.sort(key=lambda p: str(p.path))
    return projects


# ─── Command implementation ──────────────────────────


def _print(msg: str) -> None:
    if console:
        console.print(msg)
    else:
        # Strip rich markup for plain print
        print(re.sub(r'\[[^\]]+\]', '', msg))


def _cmd_list(args: argparse.Namespace) -> int:
    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        _print(f"[red]Error:[/] Path not found: {root}")
        return 1

    projects = _discover_local(root, max_depth=args.depth)
    if args.doql_only:
        projects = [p for p in projects if p.has_doql]
    if args.has_workflow:
        projects = [p for p in projects if args.has_workflow in p.doql_workflows]

    if not projects:
        _print("[yellow]No projects match the filters.[/]")
        return 0

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

    _print(f"[dim]Scanned:[/] {root}  [bold]{len(projects)}[/] projects  "
           f"[cyan]{sum(1 for p in projects if p.has_doql)}[/] with app.doql.css")
    return 0


def _analyze_workflow_issues(content: str) -> list[str]:
    """Detect empty workflows in doql content."""
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


def _cmd_run(args: argparse.Namespace) -> int:
    """Run `doql <action>` in each project with app.doql.css."""
    root = Path(args.root).expanduser().resolve()
    projects = _discover_local(root, max_depth=args.depth)
    projects = [p for p in projects if p.has_doql]

    if args.name:
        pattern = re.compile(args.name, re.IGNORECASE)
        projects = [p for p in projects if pattern.search(p.name)]

    if not projects:
        _print("[yellow]No projects with app.doql.css match the filters[/]")
        return 0

    _print(f"[bold]Running 'doql {args.action}' in {len(projects)} project(s)[/]")

    if args.dry_run:
        for p in projects:
            _print(f"  cd {p.path} && doql {args.action}")
        return 0

    success = 0
    for i, p in enumerate(projects, 1):
        _print(f"\n[bold cyan]━━━ [{i}/{len(projects)}] {p.name} ━━━[/]")
        result = subprocess.run(
            ["doql", args.action],
            cwd=str(p.path),
            capture_output=True,
            text=True,
            timeout=args.timeout,
        )
        if result.returncode == 0:
            _print("[green]  ✓ OK[/]")
            success += 1
        else:
            _print(f"[red]  ✗ FAILED (rc={result.returncode})[/]")
            for line in (result.stderr or '').strip().splitlines()[-3:]:
                _print(f"[red]    {line}[/]")
            if args.fail_fast:
                break

    _print(f"\n[bold]Summary: [green]{success}[/]/{len(projects)}[/]")
    return 0 if success == len(projects) else 1


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
