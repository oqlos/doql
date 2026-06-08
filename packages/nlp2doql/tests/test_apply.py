from pathlib import Path
from unittest.mock import patch

from nlp2doql.apply import apply_nl


def test_apply_validate_intent(tmp_path: Path) -> None:
    doc = tmp_path / "app.doql.less"
    doc.write_text('app { name: "Demo"; version: 1.0.0; }\n', encoding="utf-8")
    result = apply_nl(f"validate {doc}", file=str(doc))
    assert result.action == "validate"
    assert result.ok is True


def test_apply_query_intent(tmp_path: Path) -> None:
    doc = tmp_path / "app.doql.less"
    doc.write_text('app { name: "Demo"; version: 1.0.0; }\n', encoding="utf-8")
    with patch("uri2doql.query.resolve_doql_file", return_value=doc):
        result = apply_nl("show app metadata", file=str(doc))
    assert result.action == "query"
    assert result.ok is True
