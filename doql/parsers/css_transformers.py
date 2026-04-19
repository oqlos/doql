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


_DOQL_PROP_RE = re.compile(
    r'^(step-\d+|trigger|schedule|condition|env_file|runtime|target|framework|name|version|type)\s*:'
)


def _is_doql_property_decl(stripped: str) -> bool:
    """Return True if stripped looks like a DOQL property declaration."""
    return bool(_DOQL_PROP_RE.match(stripped.lstrip()))


def _is_selector_line(stripped: str) -> bool:
    """Determine if a line is a CSS selector or a property."""
    if stripped.rstrip().endswith(';'):
        return False
    if stripped.lstrip().startswith('- '):
        return False
    if _is_doql_property_decl(stripped):
        return False
    if ':' not in stripped:
        return True
    if '[' in stripped and ']' in stripped:
        after_bracket = stripped.split(']')[-1].strip()
        if ':' not in after_bracket:
            return True
    parts = stripped.split(':', 1)
    if len(parts) < 2:
        return True
    after_colon = parts[1].strip()
    if after_colon and not re.match(r'^[\w\[\]="\.\-\*\s{]+$', after_colon):
        return False
    return False


_DOQL_KNOWN_SELECTORS = {
    'app', 'deploy', 'database', 'entity', 'interface',
    'workflow', 'role', 'template', 'document', 'report',
    'integration', 'webhook', 'api-client', 'data-source',
}

_DOQL_PROPERTY_PREFIXES = re.compile(
    r'^(trigger|schedule|condition|env_file|runtime|target|framework|name|version|type)\s*:'
)


def _is_step_line(line: str) -> bool:
    return re.match(r'^step-\d+:', line.lstrip()) is not None


def _has_bracket_selector(stripped: str) -> bool:
    """Return True if stripped has an attribute-selector bracket pattern."""
    if '[' not in stripped or ']' not in stripped:
        return False
    after_bracket = stripped.split(']')[-1].strip()
    return ':' not in after_bracket and not after_bracket.startswith('{')


def _is_selector_starter(line: str) -> bool:
    """Return True if *line* looks like a DOQL selector (not a property)."""
    stripped = line.strip()
    if not stripped or stripped.endswith(':') or stripped.endswith(';'):
        return False
    if _is_step_line(line) or _DOQL_PROPERTY_PREFIXES.match(stripped):
        return False
    if ':' not in stripped:
        return bool(re.match(r'^[\w\-]+\[', stripped)) or stripped.split()[0] in _DOQL_KNOWN_SELECTORS
    return _has_bracket_selector(stripped)


def _find_step_block_end(lines: list[str], start_idx: int, start_indent: int) -> int:
    """Find end of a step-N item: next step/selector/brace at same/lower indent."""
    for j in range(start_idx + 1, len(lines)):
        line = lines[j].rstrip()
        if not line:
            continue
        indent = len(lines[j]) - len(lines[j].lstrip())
        stripped = line.lstrip()
        if _is_step_line(line):
            return j
        if indent <= start_indent and (_is_selector_starter(line) or stripped == '}'):
            return j
    return len(lines)


def _close_indent_blocks(
    result_lines: list[str], indent_stack: list[int], current_indent: int
) -> None:
    """Emit closing braces for all blocks whose indent exceeds *current_indent*."""
    while indent_stack and current_indent <= indent_stack[-1]:
        indent_stack.pop()
        result_lines.append('  ' * len(indent_stack) + '}')


def _convert_indent_to_braces(lines: list[str]) -> list[str]:
    """Convert indent-based SASS blocks to brace-delimited CSS."""
    result_lines: list[str] = []
    indent_stack: list[int] = []

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.rstrip()
        if not stripped:
            i += 1
            continue

        current_indent = len(line) - len(line.lstrip())
        _close_indent_blocks(result_lines, indent_stack, current_indent)

        if _is_step_line(line):
            block_end = _find_step_block_end(lines, i, current_indent)
            step_lines = [stripped.lstrip()] + [lines[j] for j in range(i + 1, block_end)]
            step_value = '\n'.join(step_lines).rstrip()
            if not step_value.endswith(';'):
                step_value += ';'
            result_lines.append('  ' * len(indent_stack) + step_value)
            i = block_end
            continue

        if _is_selector_starter(line):
            result_lines.append('  ' * len(indent_stack) + stripped.lstrip() + ' {')
            indent_stack.append(current_indent)
        else:
            prop_line = stripped.lstrip()
            if not prop_line.endswith(';'):
                prop_line += ';'
            result_lines.append('  ' * len(indent_stack) + prop_line)

        i += 1

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
