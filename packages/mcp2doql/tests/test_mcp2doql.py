from pathlib import Path
from doql.parsers.models import DoqlSpec
from mcp2doql.scanner import scan_python_mcp
from mcp2doql.cli import main as cli_main

def test_scan_mcp_mock_project(tmp_path: Path) -> None:
    # Create pyproject.toml with scripts
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text(
        """
        [project]
        name = "test-project"
        dependencies = ["fastmcp"]
        [project.scripts]
        my-mcp = "my_mcp.server:main"
        """,
        encoding="utf-8"
    )

    # Create dummy Python file with FastMCP and @mcp.tool()
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    py_file = src_dir / "my_mcp.py"
    py_file.write_text(
        """
        from mcp import FastMCP
        mcp = FastMCP("my-mcp")
        @mcp.tool()
        def get_temperature() -> float:
            return 21.5
        """,
        encoding="utf-8"
    )

    spec = DoqlSpec()
    scan_python_mcp(tmp_path, spec)

    assert len(spec.interfaces) == 1
    iface = spec.interfaces[0]
    assert iface.name == "mcp"
    assert iface.type == "mcp"
    assert iface.framework == "stdio"
    assert len(iface.pages) == 1
    assert iface.pages[0].name == "my-mcp"
    assert iface.pages[0].entry == "my_mcp.server:main"
    assert "tools" in iface.config
    assert "get_temperature" in iface.config["tools"]

def test_cli_mock_project(tmp_path: Path) -> None:
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text(
        """
        [project]
        name = "test-project"
        [project.scripts]
        my-mcp = "my_mcp.server:main"
        """,
        encoding="utf-8"
    )
    code = cli_main([str(tmp_path)])
    assert code == 0
