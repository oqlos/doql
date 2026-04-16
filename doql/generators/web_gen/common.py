"""Common utilities for web generator."""
from __future__ import annotations

import re


def _snake(name: str) -> str:
    """Convert CamelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _kebab(name: str) -> str:
    """Convert CamelCase to kebab-case."""
    return _snake(name).replace("_", "-")
