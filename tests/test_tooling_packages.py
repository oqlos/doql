"""Tests that doql adopt scans MCP/CLI interfaces in-core."""

from __future__ import annotations

from pathlib import Path

from doql.adopt.scanner.interfaces.cli import scan_python_cli
from doql.adopt.scanner.interfaces.mcp import scan_python_mcp
from doql.parsers.models import DoqlSpec


def test_adopt_scans_mcp(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo"
[project.scripts]
demo-mcp = "demo_mcp.server:main"
""",
        encoding="utf-8",
    )
    src = tmp_path / "src"
    src.mkdir()
    (src / "demo_mcp.py").write_text(
        'from mcp.server.fastmcp import FastMCP\nmcp = FastMCP("demo")\n'
        "@mcp.tool()\ndef ping() -> str:\n    return 'ok'\n",
        encoding="utf-8",
    )
    spec = DoqlSpec()
    scan_python_mcp(tmp_path, spec)
    assert any(i.type == "mcp" for i in spec.interfaces)


def test_adopt_scans_cli(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").write_text(
        """
[project]
name = "demo"
dependencies = ["click"]
[project.scripts]
demo-cli = "demo_cli.main:main"
""",
        encoding="utf-8",
    )
    spec = DoqlSpec()
    scan_python_cli(tmp_path, spec)
    cli = next(i for i in spec.interfaces if i.type == "cli")
    assert cli.pages[0].name == "demo-cli"
