import json
from pathlib import Path

import pytest

from mcp2doql.server import DoqlMCPServer


def test_mcp_server_registers_tools() -> None:
    pytest.importorskip("mcp")
    server = DoqlMCPServer(name="test-doql")
    assert server.app is not None
    assert server.app.name == "test-doql"
