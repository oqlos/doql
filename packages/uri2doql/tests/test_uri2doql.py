import json
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import yaml

from uri2doql import (
    uri_for_block,
    uri_for_file,
    uri_for_generate,
    is_doql_uri,
    query_uri,
    materialize_uri,
    resolve_prompt_to_doql_uri,
)
from uri2doql.cli import main as cli_main


def test_uri_builders() -> None:
    assert uri_for_file("app.doql.less") == "doql://file/app.doql.less"
    assert uri_for_block("app") == "doql://block/app"
    assert uri_for_block("entity", "Contact") == "doql://block/entity/Contact"
    assert uri_for_generate("CRM") == "doql://generate?prompt=CRM"
    assert is_doql_uri("doql://block/app") is True
    assert is_doql_uri("http://example.com") is False


def test_query_and_materialize_file(tmp_path: Path) -> None:
    # Prepare dummy app.doql.less file
    doc_path = tmp_path / "app.doql.less"
    doc_path.write_text(
        """
        app {
          name: "Test App";
        }
        entity[name="Contact"] {
          first_name: string;
        }
        workflow[name="install"] {
          trigger: manual;
        }
        """,
        encoding="utf-8",
    )

    # We need to resolve the file name in uri2doql.files.resolve_doql_file.
    # We will mock resolve_doql_file to return our dummy path.
    with patch("uri2doql.query.resolve_doql_file", return_value=doc_path), \
         patch("uri2doql.materialize.resolve_doql_file", return_value=doc_path):

        # Query app block
        res = query_uri("doql://block/app", file=str(doc_path))
        assert res.ok is True
        assert res.data["name"] == "Test App"

        # Query entity block
        res = query_uri("doql://block/entity/Contact", file=str(doc_path))
        assert res.ok is True
        assert "Contact" in res.rendered

        # Materialize entity block to a separate file
        out_path = tmp_path / "contact.less"
        mat = materialize_uri("doql://block/entity/Contact", dest=str(out_path))
        assert mat.ok is True
        assert out_path.is_file()
        assert "Contact" in out_path.read_text(encoding="utf-8")


def test_resolve_prompt_e2e_toon() -> None:
    # Parse our TestTOON file
    toon_path = Path(__file__).parent / "uri2doql.testql.toon.yaml"
    assert toon_path.is_file()

    # Simple parser for the PROMPTS table in the TestTOON
    lines = toon_path.read_text(encoding="utf-8").splitlines()
    rows = []
    in_prompts = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("PROMPTS"):
            in_prompts = True
            continue
        if in_prompts:
            if line.endswith(":") or (("{" in line or "}" in line) and not ("\"" in line or "'" in line)):
                # header or another block
                in_prompts = False
                continue
            # split by comma
            parts = [p.strip().strip('"').strip("'") for p in line.split(",")]
            if len(parts) >= 4:
                rows.append({"id": parts[0], "nl": parts[2], "expect_uri": parts[3]})

    assert len(rows) > 0

    # Execute and assert each prompt resolution
    for r in rows:
        hits = resolve_prompt_to_doql_uri(r["nl"])
        assert len(hits) > 0, f"Failed to resolve: {r['nl']}"
        # The best match (highest confidence) should be the first one
        best_hit = hits[0]
        assert best_hit.uri == r["expect_uri"], f"Prompt '{r['nl']}' resolved to {best_hit.uri}, expected {r['expect_uri']}"


def test_cli_query(tmp_path: Path) -> None:
    doc_path = tmp_path / "app.doql.less"
    doc_path.write_text("app { name: \"Test\"; }", encoding="utf-8")
    with patch("uri2doql.query.resolve_doql_file", return_value=doc_path):
        code = cli_main(["query", "--uri", "doql://block/app", "--file", str(doc_path)])
        assert code == 0


def test_cli_resolve() -> None:
    with patch("sys.stdout") as mock_stdout:
        code = cli_main(["resolve", "read app metadata"])
        assert code == 0
