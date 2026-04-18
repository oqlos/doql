"""Project scanner — detects services, frameworks, databases, deploy patterns.

Walks a project directory and builds a DoqlSpec by detecting:
- pyproject.toml / package.json → app metadata
- Python FastAPI/Flask → API interface
- React/Vue/Svelte → web interface
- Dockerfile / docker-compose.yml → deploy
- .env → env_refs
- models.py / schemas → entities (basic)
- Makefile / Taskfile.yml → workflows
"""
from __future__ import annotations

from pathlib import Path

from ...parsers.models import DoqlSpec

from .metadata import scan_metadata
from .databases import scan_databases
from .interfaces import scan_interfaces
from .entities import scan_entities
from .deploy import scan_deploy
from .environments import scan_environments
from .integrations import scan_integrations
from .roles import scan_roles
from .workflows import scan_workflows

__all__ = [
    "scan_project",
    # Sub-modules for advanced use
    "scan_metadata",
    "scan_databases",
    "scan_interfaces",
    "scan_entities",
    "scan_deploy",
    "scan_environments",
    "scan_integrations",
    "scan_roles",
    "scan_workflows",
]


def scan_project(root: str | Path) -> DoqlSpec:
    """Scan *root* directory and return a reverse-engineered DoqlSpec."""
    root = Path(root).resolve()
    spec = DoqlSpec()

    scan_metadata(root, spec)
    scan_databases(root, spec)
    scan_environments(root, spec)  # must run before interfaces to populate env_refs for auth detection
    scan_deploy(root, spec)
    scan_interfaces(root, spec)
    scan_integrations(root, spec)
    scan_entities(root, spec)
    scan_roles(root, spec)
    scan_workflows(root, spec)

    return spec
