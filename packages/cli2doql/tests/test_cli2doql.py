from pathlib import Path
from doql.parsers.models import DoqlSpec
from cli2doql.scanner import scan_python_cli
from cli2doql.cli import main as cli_main

def test_scan_cli_mock_project(tmp_path: Path) -> None:
    # Create pyproject.toml with scripts
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text(
        """
        [project]
        name = "test-project"
        dependencies = ["click"]
        [project.scripts]
        my-cli = "my_cli.main:main"
        """,
        encoding="utf-8"
    )

    spec = DoqlSpec()
    scan_python_cli(tmp_path, spec)

    assert len(spec.interfaces) == 1
    iface = spec.interfaces[0]
    assert iface.name == "cli"
    assert iface.type == "cli"
    assert iface.framework == "click"
    assert len(iface.pages) == 1
    assert iface.pages[0].name == "my-cli"
    assert iface.pages[0].entry == "my_cli.main:main"

def test_cli_mock_project(tmp_path: Path) -> None:
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text(
        """
        [project]
        name = "test-project"
        [project.scripts]
        my-cli = "my_cli.main:main"
        """,
        encoding="utf-8"
    )
    code = cli_main([str(tmp_path)])
    assert code == 0
