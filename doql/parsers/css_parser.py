"""CSS-like parser for .doql.css, .doql.less, and .doql.sass formats.

This module provides a thin facade over the css parsing submodules:
  - css_utils: Common data structures and utilities
  - css_transformers: Format conversion (SASS/LESS → CSS)
  - css_mappers: CSS blocks → DoqlSpec mapping

Tokenises CSS-like DOQL into (selector, declarations) blocks and maps
them to the same DoqlSpec model used by the classic .doql parser.

Supports:
  - .doql.css  — flat CSS with attribute selectors
  - .doql.less — CSS + @var variables and nesting
  - .doql.sass — whitespace-based (indent-driven), $var, @mixin/@include
"""
from __future__ import annotations

import pathlib

from .models import DoqlSpec, DoqlParseError
from .extractors import collect_env_refs
from .css_utils import CssBlock, ParsedSelector, _strip_comments, _strip_quotes, _parse_list
from .css_transformers import _resolve_less_vars, _sass_to_css
from .css_tokenizer import _tokenise_css, _parse_declarations
from .css_mappers import (
    _map_entity, _map_data_source, _map_template, _map_document,
    _map_report, _map_interface, _map_integration, _map_workflow,
    _map_role, _map_deploy, _map_database,
)

# Re-export for backward compatibility
__all__ = [
    'CssBlock', 'ParsedSelector',
    'parse_css_file', 'parse_css_text',
]


def _parse_selector(selector: str) -> ParsedSelector:
    """Parse a CSS-like selector into structured form.

    Examples:
        "app" → type="app"
        'entity[name="Node"]' → type="entity", attributes={"name": "Node"}
    """
    import re
    parts = selector.strip().split()
    result = ParsedSelector(chain=parts)

    if parts:
        first = parts[0]
        base_match = re.match(r'^([\w\-]+)', first)
        if base_match:
            result.type = base_match.group(1).lower()
        for m in re.finditer(r'\[(\w+)=["\']?([^"\'\]]+)["\']?\]', first):
            result.attributes[m.group(1)] = m.group(2)

    return result


def _map_to_spec(blocks: list[CssBlock]) -> DoqlSpec:
    """Map a list of CssBlock nodes to a DoqlSpec."""
    from .models import ValidationIssue
    spec = DoqlSpec()

    for block in blocks:
        sel = _parse_selector(block.selector)
        try:
            _apply_css_block(spec, sel, block)
        except Exception as e:
            spec.parse_errors.append(ValidationIssue(
                path=block.selector,
                message=f"Failed to map CSS block: {e}",
                severity="error",
                line=block.line,
            ))

    return spec


def _apply_css_block(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    """Route a single CSS block to the appropriate spec builder. CC: ~12"""
    t = sel.type

    route_map = {
        'entity': _map_entity,
        'data': _map_data_source,
        'template': _map_template,
        'document': _map_document,
        'report': _map_report,
        'integration': _map_integration,
        'workflow': _map_workflow,
        'role': _map_role,
        'deploy': _map_deploy,
        'database': _map_database,
    }

    if t == 'app':
        spec.app_name = _strip_quotes(block.declarations.get('name', spec.app_name))
        spec.version = _strip_quotes(block.declarations.get('version', spec.version))
        spec.domain = _strip_quotes(block.declarations.get('domain', spec.domain or ''))
        lang = block.declarations.get('languages')
        if lang:
            spec.languages = _parse_list(lang)
    elif t in ('interface',):
        _map_interface(spec, sel, block)
    elif t in route_map:
        route_map[t](spec, sel, block)
    elif t in ('scenarios', 'api-client'):
        pass  # Informational blocks — no DoqlSpec mapping yet


def parse_css_file(path: pathlib.Path) -> DoqlSpec:
    """Parse a .doql.css / .doql.less / .doql.sass file into DoqlSpec."""
    if not path.exists():
        raise DoqlParseError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")
    return parse_css_text(text, format=_detect_format(path))


def parse_css_text(text: str, format: str = "css") -> DoqlSpec:
    """Parse CSS-like DOQL source text into a DoqlSpec."""
    text = _strip_comments(text)

    if format == "less":
        text = _resolve_less_vars(text)
    elif format == "sass":
        text = _sass_to_css(text)

    blocks = _tokenise_css(text)
    spec = _map_to_spec(blocks)
    spec.env_refs = collect_env_refs(text)
    return spec


def _detect_format(path: pathlib.Path) -> str:
    """Detect format from file extension."""
    name = path.name.lower()
    if name.endswith('.doql.sass'):
        return 'sass'
    if name.endswith('.doql.less'):
        return 'less'
    return 'css'
