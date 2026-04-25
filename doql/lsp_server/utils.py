"""Shared LSP server utilities."""
from __future__ import annotations

from lsprotocol import types as lsp

from .. import parser as doql_parser
from ..parsers.models import DoqlSpec


def _parse_doc(source: str) -> DoqlSpec | None:
    """Safely parse a document from its text content."""
    try:
        return doql_parser.parse_text(source)
    except Exception:
        return None


def _find_line_col(source: str, needle: str) -> tuple[int, int]:
    """Return 0-indexed (line, col) of the first occurrence of needle."""
    idx = source.find(needle)
    if idx < 0:
        return 0, 0
    prefix = source[:idx]
    line = prefix.count("\n")
    col = idx - (prefix.rfind("\n") + 1 if "\n" in prefix else 0)
    return line, col


def _word_at(source: str, position: lsp.Position) -> str:
    """Extract the word under the cursor."""
    lines = source.splitlines()
    if position.line >= len(lines):
        return ""
    line = lines[position.line]
    start = position.character
    end = position.character
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
        start -= 1
    while end < len(line) and (line[end].isalnum() or line[end] == "_"):
        end += 1
    return line[start:end]
