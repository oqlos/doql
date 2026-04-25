"""SASS @mixin extraction and @include expansion."""
from __future__ import annotations

import re


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
