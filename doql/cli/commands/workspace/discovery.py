"""Project discovery and minimal DoQL parsing for workspace commands."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


EXCLUDED_FOLDERS = frozenset({
    'venv', '.venv', 'node_modules', '__pycache__',
    '.git', '.idea', '.pytest_cache', '.ruff_cache',
    'dist', 'build', '.code2llm_cache', 'logs',
    'iql-run-logs', 'oql-run-logs', 'refactor_output',
})

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


def _load_project_doql(proj: "DoqlProject") -> None:
    """Parse the project's app.doql.css and update proj fields in-place."""
    doql_path = proj.path / 'app.doql.css'
    try:
        content = doql_path.read_text()
        info = _parse_doql(content)
        proj.doql_workflows = info["workflows"]
        proj.doql_entities = info["entities"]
        proj.doql_databases = info["databases"]
        proj.doql_interfaces = info["interfaces"]
        m_name = re.search(r'app\s*\{[^}]*name:\s*"([^"]+)"', content, re.DOTALL)
        if m_name:
            proj.doql_app_name = m_name.group(1)
        m_ver = re.search(r'app\s*\{[^}]*version:\s*"([^"]+)"', content, re.DOTALL)
        if m_ver:
            proj.doql_app_version = m_ver.group(1)
    except OSError:
        pass


def _walk_projects(
    current: Path, projects: list, max_depth: int, depth: int
) -> None:
    """Recursively collect DoQL projects under *current*."""
    if depth > max_depth:
        return
    try:
        entries = list(current.iterdir())
    except (PermissionError, OSError):
        return
    for entry in entries:
        if not entry.is_dir() or entry.name.startswith('.') or entry.name in EXCLUDED_FOLDERS:
            continue
        if _is_project(entry):
            proj = DoqlProject(path=entry, name=entry.name)
            proj.has_taskfile = (entry / 'Taskfile.yml').exists()
            doql_path = entry / 'app.doql.css'
            proj.has_doql = doql_path.exists()
            if proj.has_doql:
                _load_project_doql(proj)
            projects.append(proj)
        elif depth < max_depth:
            _walk_projects(entry, projects, max_depth, depth + 1)


def _discover_local(root: Path, max_depth: int = 2) -> list[DoqlProject]:
    """Walk `root` up to `max_depth` levels, collect projects with manifests."""
    projects: list[DoqlProject] = []
    _walk_projects(root.resolve(), projects, max_depth, 1)
    projects.sort(key=lambda p: str(p.path))
    return projects


def _filter_projects(
    projects: list[DoqlProject], doql_only: bool, has_workflow: str | None
) -> list[DoqlProject]:
    """Apply filters to discovered projects."""
    if doql_only:
        projects = [p for p in projects if p.has_doql]
    if has_workflow:
        projects = [p for p in projects if has_workflow in p.doql_workflows]
    return projects
