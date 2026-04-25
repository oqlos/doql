"""Language Server Protocol implementation for doql.

Provides IDE features for `.doql` files:
  - Diagnostics (from parser.validate)
  - Hover (entity/field info)
  - Go-to-definition (ENTITY refs)
  - Completions (keywords, entity names)
  - Document symbols (outline view)

Requires: pip install pygls>=1.3

Usage:
    python -m doql.lsp_server        # stdio (VS Code default)
    python -m doql.lsp_server --tcp  # TCP socket on :2087
"""
from __future__ import annotations

import argparse
import sys

try:
    try:
        from pygls.lsp.server import LanguageServer  # pygls >= 2.0
    except ImportError:
        from pygls.server import LanguageServer  # pygls 1.x
    from lsprotocol import types as lsp
except ImportError:  # pragma: no cover
    print(
        "❌ pygls not installed. Install with: pip install 'doql[lsp]' or 'pip install pygls>=1.3'",
        file=sys.stderr,
    )
    sys.exit(1)

from .. import __version__

SERVER_NAME = "doql-lsp"
KEYWORDS = [
    "APP", "VERSION", "DOMAIN", "AUTHOR", "LANGUAGES", "DEFAULT_LANGUAGE",
    "ENTITY", "DATA", "TEMPLATE", "DOCUMENT", "REPORT", "DATABASE",
    "API_CLIENT", "WEBHOOK", "INTERFACE", "INTEGRATION",
    "WORKFLOW", "ROLES", "ROLE", "SCENARIOS", "TESTS", "DEPLOY",
    "PAGE", "PERMISSIONS",
]

FIELD_KEYWORDS = [
    "type", "required", "unique", "default", "computed", "ref",
    "description", "example", "format", "min", "max", "enum",
]

server = LanguageServer(SERVER_NAME, __version__)

from .diagnostics import did_open, did_change, did_save  # noqa: E402, F401
from .completion import completion  # noqa: E402, F401
from .hover import hover  # noqa: E402, F401
from .definition import definition  # noqa: E402, F401
from .symbols import document_symbols  # noqa: E402, F401


def main():
    p = argparse.ArgumentParser(description="doql Language Server")
    p.add_argument("--tcp", action="store_true", help="Run as TCP server")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=2087)
    args = p.parse_args()

    if args.tcp:
        server.start_tcp(args.host, args.port)
    else:
        server.start_io()


if __name__ == "__main__":
    main()
