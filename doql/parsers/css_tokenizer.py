"""CSS tokenizer — character-by-character brace-matching parser.

Splits CSS-like DOQL text into flat CssBlock nodes. Handles nested
blocks via recursive descent.
"""
from __future__ import annotations

import re

from .css_utils import CssBlock, _strip_comments


def _tokenise_css(text: str) -> list[CssBlock]:
    """Parse CSS-like text into flat CssBlock list."""
    blocks: list[CssBlock] = []
    text = _strip_comments(text)

    depth = 0
    current_selector = ''
    current_body = ''
    line_num = 0

    i = 0
    while i < len(text):
        ch = text[i]

        if ch == '{':
            if depth == 0:
                # Find selector start: go backwards from i
                sel_start = i - 1
                while sel_start >= 0 and text[sel_start] not in ('}', ';'):
                    sel_start -= 1
                current_selector = text[sel_start + 1:i].strip()
                current_body = ''
                line_num = text[:i].count('\n')
            depth += 1
            if depth > 1:
                current_body += ch
            i += 1
            continue

        if ch == '}':
            depth -= 1
            if depth == 0:
                block = CssBlock(
                    selector=current_selector,
                    declarations=_parse_declarations(current_body),
                    children=_tokenise_css(current_body) if '{' in current_body else [],
                    line=line_num,
                )
                blocks.append(block)
                current_selector = ''
                current_body = ''
            elif depth > 0:
                current_body += ch
            i += 1
            continue

        if depth > 0:
            current_body += ch
        i += 1

    return blocks


def _parse_declarations(body: str) -> dict[str, str]:
    """Extract property: value pairs from a CSS block body (top-level only)."""
    decls: dict[str, str] = {}
    depth = 0
    for line in body.splitlines():
        depth += line.count('{') - line.count('}')
        if depth != 0:
            continue
        line = line.strip()
        if not line or line.startswith('/*') or '{' in line or '}' in line:
            continue
        m = re.match(r'^(@?[\w\-]+)\s*:\s*(.+?)\s*;?\s*$', line)
        if m:
            decls[m.group(1)] = m.group(2).rstrip(';').strip()
    return decls
