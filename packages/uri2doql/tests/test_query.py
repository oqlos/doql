"""Tests for uri2doql addressing."""

from pathlib import Path

from uri2doql.materialize import materialize_uri
from uri2doql.query import query_uri
from uri2doql.resolve import resolve_prompt_to_doql_uri
from uri2doql.uri import uri_for_block, uri_for_file


DOQL_ROOT = Path(__file__).resolve().parents[3]
APP_DOQL = DOQL_ROOT / "app.doql.less"


def test_query_app_block():
    uri = uri_for_block("app", file=str(APP_DOQL))
    result = query_uri(uri, file=str(APP_DOQL))
    assert result.ok
    assert result.data["name"] == "doql"
    assert result.data["version"]  # version tracks app.doql.less release


def test_query_workflow_install():
    uri = uri_for_block("workflow", "install", file=str(APP_DOQL))
    result = query_uri(uri, file=str(APP_DOQL), fmt="json")
    assert result.ok
    assert result.data["name"] == "install"
    assert result.data["trigger"] == "manual"


def test_materialize_workflow_fragment(tmp_path):
    uri = uri_for_block("workflow", "test", file=str(APP_DOQL), dest=str(tmp_path / "wf.less"))
    result = materialize_uri(uri, dest=str(tmp_path / "wf.less"))
    assert result.ok
    out = tmp_path / "wf.less"
    assert out.is_file()
    assert 'workflow[name="test"]' in out.read_text(encoding="utf-8")


def test_resolve_prompt():
    hits = resolve_prompt_to_doql_uri("show app manifest from app.doql", file=str(APP_DOQL))
    assert hits
    assert any("block/app" in hit.uri or "block/app?" in hit.uri for hit in hits)


def test_uri_for_file():
    uri = uri_for_file(str(APP_DOQL))
    result = query_uri(uri)
    assert result.ok
    assert "app {" in result.rendered
