"""doql parsers — reads .doql files into a typed specification model.

This package provides a modular, registry-based parser for the doql
Language Specification v0.2. The registry pattern reduces cyclomatic
complexity from 49 (original if/elif chain) to ~5 (dispatch table).

Example:
    from doql.parsers import parse_file, validate
    spec = parse_file(pathlib.Path("app.doql"))
    issues = validate(spec, env_vars={"DATABASE_URL": "sqlite:///app.db"})
"""
from __future__ import annotations

import pathlib

from .models import (
    DoqlSpec,
    DoqlParseError,
    ValidationIssue,
    Entity,
    EntityField,
    DataSource,
    Template,
    Document,
    Report,
    Database,
    ApiClient,
    Webhook,
    Page,
    Interface,
    Integration,
    Workflow,
    WorkflowStep,
    Role,
    Deploy,
)
from .extractors import collect_env_refs
from .blocks import split_blocks, apply_block
from .validators import validate
from .css_parser import parse_css_file, parse_css_text
from .css_utils import CssBlock, ParsedSelector

# File extensions that use the CSS-like parser
_CSS_EXTENSIONS = {'.doql.css', '.doql.less', '.doql.sass'}


def _is_css_format(path: pathlib.Path) -> bool:
    """Check if a path uses one of the CSS-like DOQL formats."""
    name = path.name.lower()
    return any(name.endswith(ext) for ext in _CSS_EXTENSIONS)


def detect_doql_file(root: pathlib.Path) -> pathlib.Path:
    """Auto-detect the DOQL spec file in a project directory.

    Searches for (in priority order):
      1. app.doql.less
      2. app.doql.sass
      3. app.doql.css
      4. app.doql (classic)
    """
    for ext in ['app.doql.less', 'app.doql.sass', 'app.doql.css', 'app.doql']:
        candidate = root / ext
        if candidate.exists():
            return candidate
    return root / 'app.doql'  # fallback


def parse_file(path: pathlib.Path) -> DoqlSpec:
    """Parse a .doql / .doql.css / .doql.less / .doql.sass file into a DoqlSpec."""
    if not path.exists():
        raise DoqlParseError(f"File not found: {path}")
    if _is_css_format(path):
        return parse_css_file(path)
    return parse_text(path.read_text(encoding="utf-8"))


def parse_text(text: str) -> DoqlSpec:
    """Parse .doql source text into a DoqlSpec (in-memory, no disk I/O).

    Uses error recovery: malformed blocks are skipped and recorded in
    ``spec.parse_errors`` rather than raising.
    """
    spec = DoqlSpec()
    spec.env_refs = collect_env_refs(text)

    for keyword, header, body, start_line in split_blocks(text):
        try:
            apply_block(spec, keyword, header, body)
        except Exception as e:
            spec.parse_errors.append(ValidationIssue(
                path=f"{keyword}",
                message=f"Failed to parse {keyword} block: {e}",
                severity="error",
                line=start_line,
            ))
    return spec


def parse_env(path: pathlib.Path) -> dict[str, str]:
    """Parse a .env file into a dict. Missing file → empty dict."""
    if not path.exists():
        return {}

    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


__all__ = [
    # Main functions
    "parse_file",
    "parse_text",
    "parse_env",
    "validate",
    # Models
    "DoqlSpec",
    "DoqlParseError",
    "ValidationIssue",
    "Entity",
    "EntityField",
    "DataSource",
    "Template",
    "Document",
    "Report",
    "Database",
    "ApiClient",
    "Webhook",
    "Page",
    "Interface",
    "Integration",
    "Workflow",
    "WorkflowStep",
    "Role",
    "Deploy",
    # Internal utilities (for advanced use)
    "split_blocks",
    "apply_block",
    "collect_env_refs",
    # CSS-like parser
    "parse_css_file",
    "parse_css_text",
    "detect_doql_file",
    # CSS utilities
    "CssBlock",
    "ParsedSelector",
]
