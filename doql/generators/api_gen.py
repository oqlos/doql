"""Generate FastAPI + SQLAlchemy backend from DoqlSpec.

DEPRECATED: This module is kept for backward compatibility.
Please use `doql.generators.api_gen` (the package) instead.

The generator has been refactored into a modular package:
  - doql.generators.api_gen.common    — Type mappings and utilities
  - doql.generators.api_gen.database  — Database configuration
  - doql.generators.api_gen.models    — SQLAlchemy ORM models
  - doql.generators.api_gen.schemas   — Pydantic schemas
  - doql.generators.api_gen.routes    — CRUD endpoints
  - doql.generators.api_gen.auth      — JWT authentication
  - doql.generators.api_gen.alembic   — Migration files
  - doql.generators.api_gen.main      — FastAPI app and requirements
"""
from __future__ import annotations

# Re-export from the new package for backward compatibility
from .api_gen import generate, export_openapi  # noqa: F401

# Also export the internal functions that were previously importable
from .api_gen.common import TYPE_MAP, sa_type, py_type, py_default, safe_name, snake  # noqa: F401
