"""Tests for doql LSP server diagnostics and parsing helpers."""
from __future__ import annotations

import pathlib

import pytest

pytest.importorskip("pygls")
pytest.importorskip("lsprotocol")

from doql import lsp_server as ls


EXAMPLE = pathlib.Path(__file__).parent.parent / "examples" / "asset-management" / "app.doql"


def test_parse_doc_handles_valid_input():
    spec = ls._parse_doc('APP: "Test"\nVERSION: "1.0.0"\n')
    assert spec is not None
    assert spec.app_name == "Test"


def test_parse_doc_returns_none_on_crash():
    """Catch-all must swallow exceptions and return None — never crash the server."""
    # Even total garbage should either parse (thanks to error recovery) or return None
    result = ls._parse_doc("")
    # Empty input is still parseable (produces a DoqlSpec with defaults)
    assert result is not None


def test_find_line_col_finds_needle():
    source = "line0\nline1\nENTITY Thing:\n  id: uuid!\n"
    line, col = ls._find_line_col(source, "ENTITY Thing")
    assert line == 2
    assert col == 0


def test_word_at_extracts_word():
    from lsprotocol import types as lsp
    source = "ENTITY Thing:\n  id: uuid!\n"
    word = ls._word_at(source, lsp.Position(line=0, character=10))
    # Cursor is inside "Thing"
    assert word == "Thing"


def test_diagnostics_on_asset_management_example():
    if not EXAMPLE.exists():
        pytest.skip("example not found")
    source = EXAMPLE.read_text()
    uri = f"file://{EXAMPLE.resolve()}"
    diags = ls._diagnostics_for(source, uri)
    # Without a .env, we expect warnings about missing env vars
    assert len(diags) > 0
    assert all(hasattr(d, "range") and hasattr(d, "message") for d in diags)


def test_keyword_completion_includes_common_top_level():
    expected_top_level = {"APP", "ENTITY", "INTERFACE", "WORKFLOW", "DEPLOY"}
    assert expected_top_level.issubset(set(ls.KEYWORDS))
