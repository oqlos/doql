"""Block splitting and application logic for .doql parsing."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from .registry import get_handler

if TYPE_CHECKING:
    from .models import DoqlSpec, ValidationIssue


# Top-level keywords that start a new block (column 0, no indent)
_BLOCK_RE = re.compile(
    r'^(APP|VERSION|DOMAIN|AUTHOR|LANGUAGES|DEFAULT_LANGUAGE'
    r'|ENTITY|DATA|TEMPLATE|DOCUMENT|REPORT|DATABASE'
    r'|API_CLIENT|WEBHOOK|INTERFACE|INTEGRATION'
    r'|WORKFLOW|ROLES|ROLE|SCENARIOS|TESTS|DEPLOY)\b',
    re.MULTILINE,
)


def split_blocks(text: str) -> list[tuple[str, str, str, int]]:
    """Split .doql text into (keyword, rest_of_header, body, start_line) blocks."""
    matches = list(_BLOCK_RE.finditer(text))
    blocks: list[tuple[str, str, str, int]] = []
    for i, m in enumerate(matches):
        keyword = m.group(1)
        line_end = text.find("\n", m.start())
        if line_end == -1:
            line_end = len(text)
        header = text[m.end():line_end].strip()
        body_start = line_end + 1
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end]
        start_line = text[:m.start()].count("\n")
        blocks.append((keyword, header, body, start_line))
    return blocks


def apply_block(spec: DoqlSpec, keyword: str, header: str, body: str) -> None:
    """Apply a single parsed block to *spec* using the registry dispatch.

    This replaces the massive if/elif chain (CC=49) with a clean registry
    pattern that has CC≈3: one dispatch lookup and one call.
    """
    handler = get_handler(keyword)
    if handler is None:
        raise ValueError(f"Unknown keyword: {keyword}")
    handler(spec, header, body)
