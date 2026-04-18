"""CSS format transformers.

Converts between CSS-like formats:
  - SASS → CSS (indent-based to brace-delimited)
  - LESS variable resolution
  - SASS variable resolution
"""
from __future__ import annotations

import re
from typing import Callable


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


def _extract_mixins(lines: list[str]) -> tuple[dict[str, list[str]], list[str]]:
    """Extract @mixin definitions and return (mixins, remaining_lines)."""
    mixins: dict[str, list[str]] = {}
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^@mixin\s+([\w-]+)(?:\(.*?\))?\s*$', line)
        if m:
            mixin_name = m.group(1)
            body_lines: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith('  ') or lines[i].strip() == ''):
                body_lines.append(lines[i])
                i += 1
            mixins[mixin_name] = body_lines
            continue
        out_lines.append(line)
        i += 1
    return mixins, out_lines


def _expand_includes(lines: list[str], mixins: dict[str, list[str]]) -> list[str]:
    """Expand @include directives using provided mixins."""
    expanded: list[str] = []
    for line in lines:
        m = re.match(r'^(\s*)@include\s+([\w-]+)(?:\(.*?\))?\s*$', line)
        if m:
            indent = m.group(1)
            name = m.group(2)
            if name in mixins:
                for ml in mixins[name]:
                    expanded.append(indent + ml.lstrip())
            else:
                expanded.append(f'{indent}/* @include {name} (unresolved) */')
        else:
            expanded.append(line)
    return expanded


def _is_selector_line(stripped: str) -> bool:
    """Determine if a line is a CSS selector or a property."""
    # Lines ending with ; are properties
    if stripped.rstrip().endswith(';'):
        return False

    # Lines with list syntax are properties
    if stripped.lstrip().startswith('- '):
        return False

    # Detect selectors: lines without colon or with [] attributes
    if ':' not in stripped:
        return True

    # Check if part after [] is a property
    if '[' in stripped and ']' in stripped:
        after_bracket = stripped.split(']')[-1].strip()
        if ':' not in after_bracket:
            return True

    # Complex selector detection
    parts = stripped.split(':', 1)
    if len(parts) < 2:
        return True

    after_colon = parts[1].strip()
    # If after colon looks like a selector pattern, it's a selector
    if after_colon and not re.match(r'^[\w\[\]="\.\-\*\s{]+$', after_colon):
        return False

    return False


def _convert_indent_to_braces(lines: list[str]) -> list[str]:
    """Convert indent-based SASS blocks to brace-delimited CSS."""
    result_lines: list[str] = []
    indent_stack: list[int] = []

    for line in lines:
        stripped = line.rstrip()
        if not stripped:
            continue

        current_indent = len(line) - len(line.lstrip())

        # Close blocks that have ended
        while indent_stack and current_indent <= indent_stack[-1]:
            indent_stack.pop()
            result_lines.append('  ' * len(indent_stack) + '}')

        is_selector = _is_selector_line(stripped)

        if is_selector and not stripped.endswith(';'):
            result_lines.append('  ' * len(indent_stack) + stripped.lstrip() + ' {')
            indent_stack.append(current_indent)
        else:
            prop_line = stripped.lstrip()
            if not prop_line.endswith(';'):
                prop_line += ';'
            result_lines.append('  ' * len(indent_stack) + prop_line)

    # Close remaining open blocks
    while indent_stack:
        indent_stack.pop()
        result_lines.append('  ' * len(indent_stack) + '}')

    return result_lines


def _sass_to_css(text: str) -> str:
    """Convert indent-based SASS to brace-delimited CSS for unified parsing.

    This is a minimal conversion — enough for DOQL semantics.
    Strips @mixin definitions and expands @include as comments.
    """
    text = _resolve_sass_vars(text)

    # Collect mixins and expand includes
    lines = text.splitlines()
    mixins, remaining = _extract_mixins(lines)
    expanded = _expand_includes(remaining, mixins)

    # Convert indent-based blocks to CSS braces
    result_lines = _convert_indent_to_braces(expanded)
    return '\n'.join(result_lines)
