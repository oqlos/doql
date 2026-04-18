"""Utility functions for project scanning."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> dict[str, Any] | None:
    """Safely load a YAML file."""
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return None


def find_compose(root: Path) -> Path | None:
    """Find docker-compose file."""
    candidates = [
        root / "docker-compose.yml",
        root / "docker-compose.yaml",
        root / "infra" / "docker-compose.yml",
        root / "infra" / "docker" / "prod" / "docker-compose.prod.yml",
        root / "infra" / "docker" / "dev" / "docker-compose.dev.yml",
        root / "docker" / "docker-compose.yml",
        root / "docker" / "docker-compose.dev.yml",
        root / "docker" / "docker-compose.prod.yml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def find_dockerfiles(root: Path) -> list[Path]:
    """Find all Dockerfiles."""
    results = []
    for p in root.rglob("Dockerfile*"):
        if ".venv" not in str(p) and "venv" not in str(p) and "node_modules" not in str(p):
            results.append(p)
    return results


def camel_to_kebab(name: str) -> str:
    """Convert CamelCase/PascalCase to kebab-case."""
    name = name.removesuffix("Page").removesuffix("View")
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(w.capitalize() for w in name.split("_"))


def normalize_python_type(t: str) -> str:
    """Normalize Python type annotations to DOQL types."""
    t = t.strip()
    t = re.sub(r'Optional\[(.+)\]', r'\1', t)
    mapping = {
        "str": "string", "int": "int", "float": "float",
        "bool": "bool", "datetime": "datetime", "date": "date",
        "UUID": "uuid", "uuid": "uuid", "dict": "json",
        "list": "json", "List": "json", "Dict": "json",
        "Any": "json",
    }
    return mapping.get(t, t)


def normalize_sqlalchemy_type(t: str) -> str:
    """Normalize SQLAlchemy Column types to DOQL types."""
    mapping = {
        "String": "string", "Integer": "int", "Float": "float",
        "Boolean": "bool", "DateTime": "datetime", "Date": "date",
        "Text": "text", "JSON": "json", "UUID": "uuid",
    }
    return mapping.get(t, t.lower())


def normalize_sql_type(t: str) -> str:
    """Normalize SQL column types to DOQL types."""
    t = t.upper()
    if "VARCHAR" in t or "TEXT" in t or "CHAR" in t:
        return "string"
    if "INT" in t:
        return "int"
    if "FLOAT" in t or "REAL" in t or "DOUBLE" in t or "NUMERIC" in t:
        return "float"
    if "BOOL" in t:
        return "bool"
    if "DATE" in t or "TIME" in t:
        return "datetime"
    if "UUID" in t:
        return "uuid"
    if "JSON" in t:
        return "json"
    if "BLOB" in t or "BYTE" in t:
        return "binary"
    return t.lower()
