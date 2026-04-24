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


def _extract_authors(project: dict, spec: DoqlSpec) -> None:
    authors = project.get("authors", [])
    if not authors:
        return
    spec.authors = [
        f'{a.get("name", "")} <{a.get("email", "")}>' if a.get("email") else a.get("name", "")
        for a in authors
        if isinstance(a, dict) and a.get("name")
    ]


def _extract_keywords(project: dict, spec: DoqlSpec) -> None:
    keywords = project.get("keywords", [])
    if keywords:
        spec.keywords = keywords if isinstance(keywords, list) else [keywords]


def _extract_urls(project: dict, spec: DoqlSpec) -> None:
    urls = project.get("urls", {})
    spec.homepage = urls.get("Homepage", spec.homepage)
    spec.repository = urls.get("Repository", urls.get("Source", spec.repository))


def _extract_dependencies(project: dict, spec: DoqlSpec) -> None:
    deps = project.get("dependencies", [])
    if deps:
        spec.dependencies["runtime"] = ", ".join(deps)
    opt_deps = project.get("optional-dependencies", {})
    dev_deps = opt_deps.get("dev", opt_deps.get("test", []))
    if dev_deps:
        spec.dependencies["dev"] = ", ".join(dev_deps)


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
    spec.description = project.get("description", spec.description)
    spec.license = (
        project.get("license", {}).get("text")
        if isinstance(project.get("license"), dict)
        else project.get("license", spec.license)
    )

    _extract_authors(project, spec)
    _extract_keywords(project, spec)
    _extract_urls(project, spec)
    spec.python_requires = project.get("requires-python", spec.python_requires)
    _extract_dependencies(project, spec)


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
