"""CSS formatting helpers — indentation, property lines, field rendering."""
from __future__ import annotations

from ...parsers.models import EntityField


def _indent(lines: list[str], level: int = 1) -> str:
    prefix = "  " * level
    return "\n".join(f"{prefix}{line}" for line in lines) + "\n"


def _prop(key: str, value, quote_str: bool = True) -> str:
    """Format a CSS property line."""
    if isinstance(value, bool):
        return f"{key}: {'true' if value else 'false'};"
    if isinstance(value, (int, float)):
        return f"{key}: {value};"
    s = str(value)
    if quote_str and not s.startswith("env.") and not s.startswith("$") and not s.startswith("@"):
        return f'{key}: "{s}";'
    return f"{key}: {s};"


def _field_line(f: EntityField) -> str:
    """Render an entity field as a CSS property."""
    parts = [f.type]
    if f.required:
        parts[0] += "!"
    if f.unique:
        parts.append("unique")
    if f.auto:
        parts.append("auto")
    if f.computed:
        parts.append("computed")
    if f.ref:
        parts.append(f"ref={f.ref}")
    if f.default is not None:
        parts.append(f"default={f.default}")
    return f"{f.name}: {' '.join(parts)};"
