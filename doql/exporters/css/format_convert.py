"""CSS ↔ LESS / SASS format conversion."""
from __future__ import annotations
import re


def _unquote_simple_value(full_prop: str, val: str) -> str:
    """Return the LESS property line, removing quotes for simple scalar values."""
    if ' ' in val or ',' in val or '(' in val or ')' in val:
        return f'{full_prop}: "{val}";'
    if val.startswith(('env.', '$', '@')):
        return f'{full_prop}: {val};'
    if val in ('true', 'false', 'null'):
        return f'{full_prop}: {val};'
    if val.replace('.', '', 1).replace('-', '', 1).isdigit():
        return f'{full_prop}: {val};'
    return f'{full_prop}: {val};'


def _css_to_less(css_text: str) -> str:
    """Convert CSS output to LESS format.

    LESS uses @variables and doesn't require quotes for simple string values.
    """
    header = "// LESS format — define @variables here as needed\n\n"

    def _sub(match):
        return _unquote_simple_value(match.group(1), match.group(2))

    lines = []
    for line in css_text.splitlines():
        if not lines and not line.strip():
            continue
        line = re.sub(r'^(\s*[\w\-@]+):\s*"([^"]+)"\s*;?$', _sub, line)
        lines.append(line)

    return header + '\n'.join(lines) + '\n'


def _css_to_sass(css_text: str) -> str:
    """Convert CSS syntax to SASS (indented, no braces/semicolons)."""
    lines = []
    for line in css_text.splitlines():
        stripped = line.rstrip()
        # Skip empty lines
        if not stripped:
            lines.append("")
            continue
        # Comments pass through
        if stripped.startswith("//") or stripped.startswith("/*"):
            lines.append(stripped)
            continue
        if stripped.endswith("*/"):
            lines.append(stripped)
            continue
        # Opening brace — just remove it
        if stripped.endswith("{"):
            lines.append(stripped[:-1].rstrip())
            continue
        # Closing brace — skip
        if stripped.strip() == "}":
            continue
        # Property — remove trailing semicolon
        if stripped.rstrip().endswith(";"):
            lines.append(stripped.rstrip()[:-1])
            continue
        lines.append(stripped)
    return "\n".join(lines) + "\n"
