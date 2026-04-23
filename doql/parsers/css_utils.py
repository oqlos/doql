"""Shared CSS parsing utilities.

This module provides common data structures and helper functions
used across CSS-like parsers.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class CssBlock:
    """Single CSS-like rule: selector + key-value declarations."""
    selector: str
    declarations: dict[str, str] = field(default_factory=dict)
    children: list["CssBlock"] = field(default_factory=list)
    line: int = 0


@dataclass
class ParsedSelector:
    """Decomposed CSS selector."""
    type: str = ""            # e.g. "app", "entity", "interface", "deploy"
    attributes: dict[str, str] = field(default_factory=dict)
    chain: list[str] = field(default_factory=list)  # full selector parts


def _strip_comments(text: str) -> str:
    """Remove /* ... */ and // line comments.

    Uses a lookbehind so ``/*`` preceded by a non-whitespace character
    (e.g. ``scenarios/*.oql``) is NOT treated as a comment opener.
    """
    text = re.sub(r'(?<![^\s])/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'(?<![^\s])//[^\n]*', '', text)
    return text


def _strip_quotes(val: str) -> str:
    """Strip surrounding quotes from a value (removes ALL outer quote pairs)."""
    result = val
    while len(result) >= 2 and result[0] in ('"', "'") and result[-1] == result[0]:
        result = result[1:-1]
    return result


def _parse_list(val: str) -> list[str]:
    """Parse '[a, b, c]' or 'a, b, c' into a list."""
    val = val.strip().strip('[]')
    return [v.strip().strip('"\'') for v in val.split(',') if v.strip()]


def _parse_selector(selector: str) -> ParsedSelector:
    """Parse a CSS-like selector into structured form.

    Examples:
        "app" → type="app"
        'entity[name="Node"]' → type="entity", attributes={"name": "Node"}
    """
    parts = selector.strip().split()
    result = ParsedSelector(chain=parts)

    if parts:
        first = parts[0]
        base_match = re.match(r'^([\w\-]+)', first)
        if base_match:
            result.type = base_match.group(1).lower()
        # Collect attributes from ALL parts (e.g. project[name="x" path="y"])
        for part in parts:
            for m in re.finditer(r'\[(\w+)=["\']?([^"\'\]]+)["\']?\]', part):
                result.attributes[m.group(1)] = m.group(2)

    return result
