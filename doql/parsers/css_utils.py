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
    """Remove /* ... */ and // line comments."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'//[^\n]*', '', text)
    return text


def _strip_quotes(val: str) -> str:
    """Strip surrounding quotes from a value."""
    if len(val) >= 2 and val[0] in ('"', "'") and val[-1] == val[0]:
        return val[1:-1]
    return val


def _parse_list(val: str) -> list[str]:
    """Parse '[a, b, c]' or 'a, b, c' into a list."""
    val = val.strip().strip('[]')
    return [v.strip().strip('"\'') for v in val.split(',') if v.strip()]
