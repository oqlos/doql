"""Selector / property line classification for indent-based CSS."""
from __future__ import annotations

import re


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
