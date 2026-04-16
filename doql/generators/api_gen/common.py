"""Common utilities for API code generation."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...parsers.models import EntityField


# Type mapping: doql type → (SQLAlchemy, Python/Pydantic)
TYPE_MAP: dict[str, tuple[str, str]] = {
    "uuid":     ("String(36)",  "str"),
    "string":   ("String(255)", "str"),
    "text":     ("Text",        "str"),
    "int":      ("Integer",     "int"),
    "float":    ("Float",       "float"),
    "bool":     ("Boolean",     "bool"),
    "date":     ("Date",        "date"),
    "datetime": ("DateTime",    "datetime"),
    "json":     ("JSON",        "dict"),
    "image":    ("String(512)", "str"),
    "pdf":      ("String(512)", "str"),
    "oql":      ("String(255)", "str"),
    "enum":     ("String(64)",  "str"),
}


_PY_KEYWORDS = frozenset({
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return",
    "try", "while", "with", "yield", "type",
})


def sa_type(f: EntityField) -> str:
    """Get SQLAlchemy type for a field."""
    return TYPE_MAP.get(f.type, ("String(255)", "str"))[0]


def py_type(f: EntityField) -> str:
    """Get Python/Pydantic type for a field."""
    base = TYPE_MAP.get(f.type, ("", "str"))[1]
    if f.ref:
        base = "str"
    # Wrap in Optional whenever the value can legally be None at runtime
    # (non-required DB column, or auto-generated — None on create payload).
    if f.auto or not f.required:
        return f"Optional[{base}]"
    return base


def py_default(f: EntityField) -> str:
    """Get default value assignment for a field."""
    if f.auto:
        return " = None"
    if f.default:
        val = f.default
        if f.type == "bool":
            return f" = {val.capitalize()}"
        if f.type == "int":
            return f" = {val}"
        return f' = "{val}"'
    if not f.required:
        return " = None"
    return ""


def safe_name(name: str) -> str:
    """Escape Python reserved keywords by appending underscore."""
    return f"{name}_" if name in _PY_KEYWORDS else name


def snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
