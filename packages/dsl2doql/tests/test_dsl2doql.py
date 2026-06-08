from pathlib import Path

from dsl2doql.cli import main as cli_main
from dsl2doql.engine import execute_dsl_line
from doql.importers.oql_converter import convert_dsl_to_doql


def test_convert_via_dsl_engine(tmp_path: Path) -> None:
    oql = tmp_path / "test.oql"
    oql.write_text("SET NAME 'My test'\nSET pompa_1 1\n", encoding="utf-8")
    out = tmp_path / "workflow.less"
    result = execute_dsl_line(f"CONVERT {oql} OUT {out}")
    assert result.ok is True
    assert out.is_file()
    assert 'workflow[name="my_test"]' in out.read_text(encoding="utf-8")


def test_convert_oql_importer() -> None:
    doql = convert_dsl_to_doql("SET NAME 'My test'\nSET pompa_1 1\n")
    assert 'workflow[name="my_test"]' in doql


def test_cli_convert(tmp_path: Path) -> None:
    oql = tmp_path / "test.oql"
    oql.write_text("SET NAME 'My test'\n", encoding="utf-8")
    out = tmp_path / "workflow.less"
    code = cli_main(["-c", f"CONVERT {oql} OUT {out}"])
    assert code == 0
    assert out.is_file()
