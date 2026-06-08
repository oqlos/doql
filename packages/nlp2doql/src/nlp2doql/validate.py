"""Validate DOQL via doql parser."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _result_from_spec(spec: Any, issues: list[Any]) -> dict[str, Any]:
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity != "error"]
    parse_errors = [e for e in spec.parse_errors if e.severity == "error"]
    parse_warnings = [e for e in spec.parse_errors if e.severity != "error"]
    return {
        "ok": not errors and not parse_errors,
        "errors": [f"{i.path}: {i.message}" for i in errors],
        "warnings": [f"{i.path}: {i.message}" for i in warnings],
        "parse_errors": [f"{i.path}: {i.message}" for i in parse_errors],
        "parse_warnings": [f"{i.path}: {i.message}" for i in parse_warnings],
        "app_name": spec.app_name,
        "entity_count": len(spec.entities),
        "workflow_count": len(spec.workflows),
    }


def validate_doql(source: str) -> dict[str, Any]:
    """Validate DOQL LESS/CSS text (e.g. nlp2doql output)."""
    try:
        import doql

        spec = doql.parse_css_text(source, format="less")
        issues = doql.validate(spec, env_vars={})
        return _result_from_spec(spec, issues)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def validate_doql_file(path: str | Path) -> dict[str, Any]:
    """Validate a DOQL file the same way as `doql validate`."""
    try:
        import doql

        file_path = Path(path).resolve()
        spec = doql.parse_file(file_path)
        env_vars = doql.parse_env(file_path.parent / ".env")
        issues = doql.validate(spec, env_vars, project_root=file_path.parent)
        return _result_from_spec(spec, issues)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}
