"""Naming convention utilities for doql."""
from __future__ import annotations

import re


def snake(name: str) -> str:
    """Convert CamelCase to snake_case (also handles spaces).

    Examples:
        >>> snake("CamelCase")
        'camel_case'
        >>> snake("SimpleXML")
        'simple_xml'
        >>> snake("already_snake")
        'already_snake'
        >>> snake("My App Name")
        'my_app_name'
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    return s2.replace(" ", "_")


def kebab(name: str) -> str:
    """Convert CamelCase or snake_case to kebab-case.

    Examples:
        >>> kebab("CamelCase")
        'camel-case'
        >>> kebab("snake_case")
        'snake-case'
        >>> kebab("already-kebab")
        'already-kebab'
    """
    # First convert to snake, then replace underscores with hyphens
    return snake(name).replace("_", "-")
