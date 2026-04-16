"""Generate FastAPI + SQLAlchemy backend from DoqlSpec.

DEPRECATED: This module is kept for backward compatibility.
Please use `doql.generators.api_gen` (the package) instead.
"""
from __future__ import annotations

# Re-export from the new package for backward compatibility
from .api_gen import generate, export_openapi
from .api_gen.common import TYPE_MAP, sa_type, py_type, py_default, safe_name, snake
from .api_gen.database import gen_database
from .api_gen.models import gen_models
from .api_gen.schemas import gen_schemas
from .api_gen.routes import gen_routes
from .api_gen.auth import gen_auth
from .api_gen.alembic import gen_alembic_ini, gen_alembic_env, gen_initial_migration
from .api_gen.main import gen_main, gen_requirements

__all__ = [
    "generate", "export_openapi",
    "TYPE_MAP", "sa_type", "py_type", "py_default", "safe_name", "snake",
    "gen_database", "gen_models", "gen_schemas", "gen_routes",
    "gen_auth", "gen_alembic_ini", "gen_alembic_env", "gen_initial_migration",
    "gen_main", "gen_requirements",
]
