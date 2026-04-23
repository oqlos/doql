"""CSS tokenizer — character-by-character brace-matching parser.

Splits CSS-like DOQL text into flat CssBlock nodes. Handles nested
blocks via recursive descent.
"""
from __future__ import annotations

import re

from .css_utils import CssBlock, _strip_quotes

# Pre-compiled regex for declaration parsing
_DECL_RE = re.compile(r'^([@\w\-]+)\s*:\s*(.+)$')


def _make_css_block(selector: str, body: str, line_num: int) -> CssBlock:
    """Build a CssBlock from selector + raw body text."""
    return CssBlock(
        selector=selector,
        declarations=_parse_declarations(body),
        children=_tokenise_css(body) if '{' in body else [],
        line=line_num,
    )


def _tokenise_css(text: str) -> list[CssBlock]:
    """Parse CSS-like text into flat CssBlock list.

    Optimized: uses index-based brace matching for O(n) performance.
    """
    blocks: list[CssBlock] = []

    pos = 0
    line_num = 0

    while pos < len(text):
        # Find next opening brace at depth 0
        brace_pos = text.find('{', pos)
        if brace_pos == -1:
            break

        # Extract selector (text between last closing brace or start and this brace)
        selector = text[pos:brace_pos].strip()
        if not selector:
            pos = brace_pos + 1
            continue

        # Find matching closing brace using depth counting
        depth = 1
        body_start = brace_pos + 1
        scan_pos = body_start

        while scan_pos < len(text) and depth > 0:
            if text[scan_pos] == '{':
                depth += 1
            elif text[scan_pos] == '}':
                depth -= 1
            scan_pos += 1

        if depth == 0:
            body = text[body_start:scan_pos - 1]
            block = _make_css_block(selector, body, text[:brace_pos].count('\n'))
            blocks.append(block)
            pos = scan_pos
        else:
            # Unclosed block, skip
            break

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
        if not stripped or stripped[:2] in ('/*', '//') or stripped in ('{', '}'):
            continue

        # Handle multiple declarations on one line: split by semicolon first
        statements = [s.strip() for s in stripped.split(';') if s.strip()]

        for stmt in statements:
            m = _DECL_RE.match(stmt)
            if m:
                key, val = m.group(1), m.group(2).strip()
                decls[key] = _strip_quotes(val)

    return decls
