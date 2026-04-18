"""Project scanner — detects services, frameworks, databases, deploy patterns.

Walks a project directory and builds a DoqlSpec by detecting:
- pyproject.toml / package.json → app metadata
- Python FastAPI/Flask → API interface
- React/Vue/Svelte → web interface
- Dockerfile / docker-compose.yml → deploy
- .env → env_refs
- models.py / schemas → entities (basic)
- Makefile / Taskfile.yml → workflows

.. deprecated::
    The monolithic scanner module is deprecated. Use the submodules in
    `doql.adopt.scanner` package for new code.
"""
from __future__ import annotations

# Re-export main entry point for backward compatibility
from .scanner import scan_project

# Re-export sub-modules for advanced use
from .scanner import (
    scan_metadata,
    scan_databases,
    scan_interfaces,
    scan_entities,
    scan_deploy,
    scan_environments,
    scan_integrations,
    scan_roles,
    scan_workflows,
)

__all__ = [
    "scan_project",
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
