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


_IMAGE_DB_MAP: list[tuple[str, str, str]] = [
    ("postgres", "postgres",  "postgresql", "env.DATABASE_URL"),
    ("mysql",    "mysql",      "mysql",       "env.DATABASE_URL"),
    ("mariadb",  "mysql",      "mysql",       "env.DATABASE_URL"),
    ("redis",    "redis",      "redis",       "env.REDIS_URL"),
    ("mongo",    "mongodb",    "mongodb",      "env.MONGO_URL"),
]


def _db_from_image(svc_name: str, image: str) -> Database | None:
    """Return a Database for *svc_name*/*image* if a known engine matches."""
    for keyword, db_alias, db_type, url in _IMAGE_DB_MAP:
        if keyword in image:
            return Database(name=_db_name(svc_name, db_alias), type=db_type, url=url)
    return None


def _scan_compose_databases(root: Path, spec: DoqlSpec) -> None:
    compose = find_compose(root)
    if not compose:
        return
    data = load_yaml(compose)
    if not data:
        return
    for svc_name, svc in data.get("services", {}).items():
        db = _db_from_image(svc_name, svc.get("image", ""))
        if db:
            spec.databases.append(db)


def scan_databases(root: Path, spec: DoqlSpec) -> None:
    """Detect database setup from docker-compose, .env, config files."""
    _scan_compose_databases(root, spec)

    # Check for SQLite references in .env
    for ref in spec.env_refs:
        if "SQLITE" in ref.upper() or "DB_PATH" in ref.upper():
            if not any(db.type == "sqlite" for db in spec.databases):
                spec.databases.append(Database(
                    name="main", type="sqlite",
                    url=f"env.{ref}",
                ))
