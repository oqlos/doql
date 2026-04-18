"""Database scanning — docker-compose, .env detection."""
from __future__ import annotations

from pathlib import Path

from ...parsers.models import Database, DoqlSpec
from .utils import find_compose, load_yaml

_GENERIC_DB_NAMES = {"db", "database", "pg", "sql", "data"}


def _db_name(svc_name: str, db_type: str) -> str:
    """Return a meaningful DB block name. Generic compose service names like
    ``db`` / ``database`` are replaced with the concrete engine type so the
    generated ``.doql.css`` is self-documenting."""
    if svc_name.lower() in _GENERIC_DB_NAMES:
        return db_type
    return svc_name


def scan_databases(root: Path, spec: DoqlSpec) -> None:
    """Detect database setup from docker-compose, .env, config files."""
    compose = find_compose(root)
    if compose:
        data = load_yaml(compose)
        if data:
            services = data.get("services", {})
            for svc_name, svc in services.items():
                image = svc.get("image", "")
                if "postgres" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "postgres"), type="postgresql",
                        url=f"env.DATABASE_URL",
                    ))
                elif "mysql" in image or "mariadb" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "mysql"), type="mysql",
                        url="env.DATABASE_URL",
                    ))
                elif "redis" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "redis"), type="redis",
                        url="env.REDIS_URL",
                    ))
                elif "mongo" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "mongodb"), type="mongodb",
                        url="env.MONGO_URL",
                    ))

    # Check for SQLite references in .env
    for ref in spec.env_refs:
        if "SQLITE" in ref.upper() or "DB_PATH" in ref.upper():
            if not any(db.type == "sqlite" for db in spec.databases):
                spec.databases.append(Database(
                    name="main", type="sqlite",
                    url=f"env.{ref}",
                ))
