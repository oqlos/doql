"""Tests for doql workspace command."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from doql.cli.commands.workspace import (
    DoqlProject,
    _discover_local,
    _parse_doql,
    PROJECT_MARKERS,
    EXCLUDED_FOLDERS,
)


def _make_doql_project(
    tmp_path: Path,
    name: str,
    app_name: str = None,
    app_version: str = "0.1.0",
    workflows: list[str] = None,
    entities: list[str] = None,
    databases: list[str] = None,
    with_taskfile: bool = False,
) -> Path:
    """Create a fake project with pyproject.toml + app.doql.css."""
    proj = tmp_path / name
    proj.mkdir()
    (proj / "pyproject.toml").write_text('[project]\nname = "test"\n')

    if with_taskfile:
        (proj / "Taskfile.yml").write_text(f"name: {name}\ntasks:\n  install:\n    cmds:\n    - echo\n")

    app_name = app_name or name
    workflows = workflows or ["install", "test"]
    entities = entities or []
    databases = databases or []

    lines = [
        "app {",
        f'  name: "{app_name}";',
        f'  version: "{app_version}";',
        "}",
        "",
    ]
    for db in databases:
        lines += [f'database[name="{db}"] {{', '  type: "postgresql";', '}', '']
    for ent in entities:
        lines += [f'entity[name="{ent}"] {{', '  id: int;', '}', '']
    for wf in workflows:
        lines += [
            f'workflow[name="{wf}"] {{',
            f'  step-1: run cmd=echo {wf};',
            '}',
            '',
        ]
    (proj / "app.doql.css").write_text("\n".join(lines))
    return proj


class TestParseDoql:
    def test_extracts_workflows(self):
        content = '''
workflow[name="install"] { step-1: run cmd=pip; }
workflow[name="test"] { step-1: run cmd=pytest; }
'''
        info = _parse_doql(content)
        assert info["workflows"] == ["install", "test"]

    def test_extracts_entities(self):
        content = '''
entity[name="Users"] { id: int; }
entity[name="Orders"] { id: int; }
'''
        info = _parse_doql(content)
        assert info["entities"] == ["Users", "Orders"]

    def test_extracts_databases(self):
        content = '''
database[name="main"] { type: "postgresql"; }
'''
        info = _parse_doql(content)
        assert info["databases"] == ["main"]

    def test_extracts_interfaces(self):
        content = '''
interface[type="cli"] { framework: click; }
interface[type="web"] { framework: react; }
'''
        info = _parse_doql(content)
        assert info["interfaces"] == ["cli", "web"]


class TestDiscoverLocal:
    def test_discovers_doql_projects(self, tmp_path):
        _make_doql_project(tmp_path, "alpha")
        _make_doql_project(tmp_path, "beta")

        projects = _discover_local(tmp_path, max_depth=1)
        names = {p.name for p in projects}
        assert {"alpha", "beta"} <= names
        assert len(projects) == 2
        assert all(p.has_doql for p in projects)

    def test_extracts_doql_metadata(self, tmp_path):
        _make_doql_project(
            tmp_path, "alpha",
            app_name="Alpha App", app_version="1.2.3",
            workflows=["install", "test", "deploy"],
            entities=["Users", "Orders"],
            databases=["main"],
        )
        projects = _discover_local(tmp_path, max_depth=1)
        assert len(projects) == 1
        p = projects[0]
        assert p.doql_app_name == "Alpha App"
        assert p.doql_app_version == "1.2.3"
        assert p.doql_workflows == ["install", "test", "deploy"]
        assert p.doql_entities == ["Users", "Orders"]
        assert p.doql_databases == ["main"]

    def test_respects_max_depth(self, tmp_path):
        _make_doql_project(tmp_path, "top")
        group = tmp_path / "group"
        group.mkdir()
        _make_doql_project(group, "nested")

        d1 = _discover_local(tmp_path, max_depth=1)
        assert {p.name for p in d1} == {"top"}

        d2 = _discover_local(tmp_path, max_depth=2)
        assert {p.name for p in d2} == {"top", "nested"}

    def test_excludes_logs_and_venv(self, tmp_path):
        _make_doql_project(tmp_path, "alpha")
        # Log folder with app.doql.css — should be skipped because of EXCLUDED_FOLDERS
        for excluded in ["iql-run-logs", "oql-run-logs", "venv", ".git"]:
            d = tmp_path / excluded
            d.mkdir()
            (d / "pyproject.toml").write_text("")

        projects = _discover_local(tmp_path, max_depth=2)
        names = {p.name for p in projects}
        assert "alpha" in names
        assert not (names & {"iql-run-logs", "oql-run-logs", "venv", ".git"})

    def test_does_not_dive_into_project(self, tmp_path):
        outer = _make_doql_project(tmp_path, "outer")
        inner = _make_doql_project(outer, "inner")

        projects = _discover_local(tmp_path, max_depth=3)
        names = {p.name for p in projects}
        assert "outer" in names
        assert "inner" not in names


class TestProjectMarkers:
    def test_markers_do_not_include_doql_css(self):
        """Prevent false-positive detection on docs/logs folders containing only app.doql.css."""
        assert "app.doql.css" not in PROJECT_MARKERS

    def test_excluded_contains_logs(self):
        assert "iql-run-logs" in EXCLUDED_FOLDERS
        assert "oql-run-logs" in EXCLUDED_FOLDERS
        assert "venv" in EXCLUDED_FOLDERS
