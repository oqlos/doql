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
            # Inside nested block - if we have pending declaration, accumulate
            if pending_key is not None:
                pending_value += "\n" + line
            continue
            
        stripped = line.strip()
        if not stripped or stripped.startswith('/*'):
            continue
            
        # Skip lines that are just braces (block terminators)
        if stripped in ('{', '}'):
            continue
            
        # Check if this looks like a new declaration (has property: value pattern)
        # A new declaration starts at top level and has 'key: value' pattern
        m = re.match(r'^(@?[\w\-]+)\s*:\s*(.+)$', stripped)
        
        if m and pending_key is None:
            key, val = m.group(1), m.group(2).rstrip(';').strip()
            if stripped.rstrip().endswith(';'):
                # Complete declaration on single line
                decls[key] = _strip_quotes(val)
            else:
                # Multi-line declaration starts
                pending_key = key
                pending_value = val
        elif pending_key is not None:
            # Continue accumulating multi-line value
            pending_value += "\n" + stripped
            
        # Check if pending declaration is now complete (ends with ;)
        if pending_key is not None and pending_value.rstrip().endswith(';'):
            decls[pending_key] = _strip_quotes(pending_value.rstrip(';').strip())
            pending_key = None
            pending_value = ""
    
    # Handle any remaining pending declaration (incomplete - no trailing ;)
    if pending_key is not None:
        decls[pending_key] = _strip_quotes(pending_value.strip())
        
    return decls
