"""Entity scanning — from Python models and SQL files."""
from __future__ import annotations

import re
from pathlib import Path

from ...parsers.models import DoqlSpec, Entity, EntityField
from .utils import snake_to_pascal, normalize_python_type, normalize_sqlalchemy_type, normalize_sql_type

# Suffixes that indicate a class is a transient API DTO rather than a
# persistent domain entity. We strip these from the candidate pool so that
# generated specs stay focused on the data model the user actually owns.
_DTO_SUFFIXES = (
    "Request", "Response", "Result", "Create", "Update", "Patch",
    "Delete", "In", "Out", "Schema", "DTO", "Dto", "Params", "Query",
    "Payload", "Body", "Form", "Reply",
)

# SQLAlchemy / SQLModel / Django bases imply a persistent entity even if the
# class name happens to end with a DTO-looking suffix.
_PERSISTENT_BASES = (
    "Base", "db.Model", "SQLModel", "DeclarativeBase",
    "models.Model",
)

# Pydantic / generic bases produce *candidate* entities that we then filter by
# name to weed out request/response wrappers.
_DTO_BASES = ("BaseModel", "Model")


def _is_dto_name(name: str) -> bool:
    """Return True when *name* looks like an API DTO rather than an entity."""
    return any(name.endswith(suffix) for suffix in _DTO_SUFFIXES)


def scan_entities(root: Path, spec: DoqlSpec) -> None:
    """Detect entities from Python models / schemas or SQL files."""
    # Check for models.py / schemas.py in common locations
    model_files: list[Path] = []
    for pattern in ("**/models.py", "**/schemas.py", "**/models/*.py"):
        model_files.extend(root.glob(pattern))

    seen: set[str] = set()
    for mf in model_files:
        mf_str = str(mf)
        if (".venv" in mf_str or "venv" in mf_str
                or "node_modules" in mf_str
                or "/build/" in mf_str or mf_str.endswith("/build")
                or "/.doql/" in mf_str or mf_str.endswith("/.doql")
                or "/dist/" in mf_str):
            continue
        _extract_entities_from_python(mf, spec, seen)

    # Check SQL init files
    for sql in root.rglob("*.sql"):
        sql_str = str(sql)
        if (".venv" in sql_str or "venv" in sql_str
                or "/build/" in sql_str or "/.doql/" in sql_str):
            continue
        _extract_entities_from_sql(sql, spec, seen)


def _extract_entities_from_python(path: Path, spec: DoqlSpec, seen: set[str]) -> None:
    """Extract entity names from Python class definitions.

    Persistent classes (SQLAlchemy / SQLModel / Django) are always kept.
    Pydantic / dataclass-style classes are kept only when their name does
    *not* match a known DTO suffix (Request/Response/Result/...).
    """
    try:
        text = path.read_text()
    except Exception:
        return

    for m in re.finditer(r'class\s+(\w+)\s*\((.*?)\)\s*:', text):
        name = m.group(1)
        bases_raw = m.group(2)
        if name in seen or name.startswith("_"):
            continue

        # Tokenise the comma-separated base list so "Base" does not match
        # "BaseModel" (subclass of Pydantic), only an actual ``Base`` parent.
        base_tokens = {
            b.split("[", 1)[0].strip() for b in bases_raw.split(",") if b.strip()
        }
        is_persistent = bool(base_tokens & set(_PERSISTENT_BASES))
        is_dto_base = bool(base_tokens & set(_DTO_BASES))

        if not (is_persistent or is_dto_base):
            continue

        # Filter out obvious DTOs unless they inherit from a persistent base.
        if not is_persistent and _is_dto_name(name):
            continue

        entity = Entity(name=name)
        _extract_fields(text, m.end(), entity)
        spec.entities.append(entity)
        seen.add(name)


def _extract_annotation_fields(
    stripped: str, entity: Entity
) -> EntityField | None:
    """Extract field from type annotation pattern: field_name: type = ..."""
    field_match = re.match(r"\s+(\w+)\s*:\s*([\w\[\], |]+)", stripped)
    if not field_match:
        return None
    fname = field_match.group(1)
    ftype = field_match.group(2).strip()
    if fname.startswith("_") or fname in ("model_config", "Config"):
        return None
    ef = EntityField(name=fname, type=normalize_python_type(ftype))
    ef.required = not ("Optional" in ftype or "None" in ftype)
    return ef


def _extract_sqlalchemy_fields(stripped: str, entity: Entity) -> None:
    """Extract field from SQLAlchemy Column pattern: field_name = Column(...)"""
    col_match = re.match(r"\s+(\w+)\s*=\s*Column\(\s*(\w+)", stripped)
    if not col_match:
        return
    fname = col_match.group(1)
    ftype = col_match.group(2)
    if not fname.startswith("_"):
        entity.fields.append(
            EntityField(name=fname, type=normalize_sqlalchemy_type(ftype))
        )


def _extract_fields(text: str, start: int, entity: Entity) -> None:
    """Extract field definitions from a Python class body."""
    lines = text[start:].split("\n")
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith('"""'):
            continue
        if line and not line[0].isspace():
            break

        annotation_field = _extract_annotation_fields(stripped, entity)
        if annotation_field:
            entity.fields.append(annotation_field)
        else:
            _extract_sqlalchemy_fields(stripped, entity)


def _extract_entities_from_sql(path: Path, spec: DoqlSpec, seen: set[str]) -> None:
    """Extract entities from CREATE TABLE statements."""
    try:
        text = path.read_text()
    except Exception:
        return

    for m in re.finditer(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?(\w+)["`]?\s*\((.*?)\)',
        text, re.IGNORECASE | re.DOTALL
    ):
        table_name = m.group(1)
        if table_name in seen:
            continue
        entity = Entity(name=snake_to_pascal(table_name))
        body = m.group(2)
        for col_match in re.finditer(
            r'["`]?(\w+)["`]?\s+([\w()]+)',
            body
        ):
            col_name = col_match.group(1)
            col_type = col_match.group(2)
            if col_name.upper() in ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK",
                                     "CONSTRAINT", "INDEX", "KEY", "NOT",
                                     "DEFAULT", "IF", "CREATE", "TABLE",
                                     "REFERENCES", "ON", "CASCADE", "SET",
                                     "NULL", "RESTRICT", "NO", "ACTION"):
                continue
            entity.fields.append(EntityField(
                name=col_name,
                type=normalize_sql_type(col_type),
            ))
        if entity.fields:
            spec.entities.append(entity)
            seen.add(table_name)
