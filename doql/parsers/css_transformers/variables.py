"""CSS variable resolution (LESS @vars, SASS $vars)."""
from __future__ import annotations

import re


def _resolve_vars(text: str, prefix: str) -> str:
    """Expand variable declarations in CSS-like text.

    Args:
        text: Input text with variable declarations
        prefix: Variable prefix character ('@' for LESS, '$' for SASS)
    """
    variables: dict[str, str] = {}
    lines = []
    # Match pattern depends on prefix (LESS uses ; terminator, SASS doesn't)
    pattern = rf'^\{prefix}([\w-]+)\s*:\s*(.+?)\s*;?\s*$'

    for line in text.splitlines():
        m = re.match(pattern, line)
        if m:
            variables[m.group(1)] = m.group(2)
        else:
            lines.append(line)

    result = '\n'.join(lines)
    # Expand variable references (up to 5 passes for nested refs)
    for _ in range(5):
        prev = result
        for name, val in variables.items():
            result = result.replace(f'{prefix}{name}', val)
        if result == prev:
            break
    return result


# Backward-compatible aliases
def _resolve_less_vars(text: str) -> str:
    """Expand @variable declarations in .doql.less text."""
    return _resolve_vars(text, "@")


def _resolve_sass_vars(text: str) -> str:
    """Expand $variable declarations in .doql.sass text."""
    return _resolve_vars(text, "$")
