"""CSS tokenizer — character-by-character brace-matching parser.

Splits CSS-like DOQL text into flat CssBlock nodes. Handles nested
blocks via recursive descent.
"""
from __future__ import annotations

import re

from .css_utils import CssBlock, _strip_comments, _strip_quotes


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


def _consume_pending(decls: dict, pending_key: str, pending_value: str) -> tuple[str | None, str]:
    """Flush a completed multi-line declaration into *decls*. Returns (None, '')."""
    decls[pending_key] = _strip_quotes(pending_value.rstrip(';').strip())
    return None, ""


def _process_decl_line(
    stripped: str, pending_key: str | None, pending_value: str, decls: dict
) -> tuple[str | None, str]:
    """Process one stripped declaration line; return updated (pending_key, pending_value)."""
    m = re.match(r'^(@?[\w\-]+)\s*:\s*(.+)$', stripped)
    if m and pending_key is None:
        key, val = m.group(1), m.group(2).rstrip(';').strip()
        if stripped.rstrip().endswith(';'):
            decls[key] = _strip_quotes(val)
        else:
            pending_key = key
            pending_value = val
    elif pending_key is not None:
        pending_value += "\n" + stripped

    if pending_key is not None and pending_value.rstrip().endswith(';'):
        pending_key, pending_value = _consume_pending(decls, pending_key, pending_value)
    return pending_key, pending_value


def _parse_declarations(body: str) -> dict[str, str]:
    """Extract property: value pairs from a CSS block body (top-level only).

    Handles multi-line declarations where value continues on next line
    until terminated with semicolon.
    """
    decls: dict[str, str] = {}
    depth = 0
    pending_key: str | None = None
    pending_value: str = ""

    for line in body.splitlines():
        depth += line.count('{') - line.count('}')
        if depth != 0:
            if pending_key is not None:
                pending_value += "\n" + line
            continue

        stripped = line.strip()
        if not stripped or stripped.startswith('/*') or stripped in ('{', '}'):
            continue

        pending_key, pending_value = _process_decl_line(
            stripped, pending_key, pending_value, decls
        )

    if pending_key is not None:
        decls[pending_key] = _strip_quotes(pending_value.strip())

    return decls
