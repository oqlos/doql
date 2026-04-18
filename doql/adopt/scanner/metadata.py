"""Metadata scanning — pyproject.toml, package.json, goal.yaml."""
from __future__ import annotations

import json
from pathlib import Path

from ...parsers.models import DoqlSpec


def scan_metadata(root: Path, spec: DoqlSpec) -> None:
    """Extract app name, version, domain from config files."""
    pyproj = root / "pyproject.toml"
    if pyproj.exists():
        _parse_pyproject(pyproj, spec)

    pkg = root / "package.json"
    if pkg.exists():
        _parse_package_json(pkg, spec)

    goal = root / "goal.yaml"
    if goal.exists():
        _parse_goal_yaml(goal, spec)

    version_file = root / "VERSION"
    if version_file.exists():
        v = version_file.read_text().strip()
        if v:
            spec.version = v


def _parse_pyproject(path: Path, spec: DoqlSpec) -> None:
    """Extract metadata from pyproject.toml (stdlib tomllib)."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    spec.app_name = project.get("name", spec.app_name)
    spec.version = project.get("version", spec.version)

    # Detect entry points (CLI scripts)
    scripts = project.get("scripts", {})
    for name, ep in scripts.items():
        if "api" in name or "server" in name:
            # Likely an API service entry point
            pass  # handled by interface scan


def _parse_package_json(path: Path, spec: DoqlSpec) -> None:
    """Extract metadata from package.json."""
    data = json.loads(path.read_text())
    spec.app_name = data.get("name", spec.app_name)
    spec.version = data.get("version", spec.version)


def _parse_goal_yaml(path: Path, spec: DoqlSpec) -> None:
    """Extract metadata from goal.yaml if present."""
    try:
        import yaml
        data = yaml.safe_load(path.read_text()) or {}
        if "name" in data:
            spec.app_name = data["name"]
    except Exception:
        pass
