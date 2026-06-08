from cli2doql.cli import main as cli_main


def test_cli_exec_query(monkeypatch) -> None:
    called = {}

    def fake_execute(line, *, default_file=None):
        from dsl2doql.engine import DslResult

        called["line"] = line
        return DslResult(ok=True, command=line, action="query", output='{"name":"demo"}')

    monkeypatch.setattr("cli2doql.cli.execute_dsl_line", fake_execute)
    code = cli_main(["exec", "QUERY doql://block/app"])
    assert code == 0
    assert "QUERY" in called["line"]
