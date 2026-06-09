"""FastMCP server exposing DOQL control tools."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


def _require_fastmcp():
    try:
        from mcp.server.fastmcp import FastMCP
        return FastMCP
    except ImportError as exc:
        raise RuntimeError(
            "MCP support requires optional dependency 'mcp'. Install with: pip install mcp",
        ) from exc


@dataclass
class DoqlMCPServer:
    """Expose DOQL query/patch/validate/generate via MCP tools."""

    name: str = "doql"

    def __post_init__(self) -> None:
        FastMCP = _require_fastmcp()
        self.app = FastMCP(self.name)
        self._register_tools()

    def _register_tools(self) -> None:
        from dsl2doql import dispatch, execute_dsl, execute_dsl_line
        from dsl2doql.pb_codec import encode_result_protobuf
        from nlp2doql.apply import apply_nl
        from uri2doql.materialize import materialize_uri
        from uri2doql.nlp2uri import nlp2uri
        from uri2doql.patch import apply_uri, patch_uri, update_uri
        from uri2doql.query import query_uri

        @self.app.tool()
        def doql_query(uri: str, file: str = "", fmt: str = "json") -> dict[str, Any]:
            """Query a doql:// URI or block selector."""
            result = query_uri(uri, file=file or None, fmt=fmt)
            return result.to_dict()

        @self.app.tool()
        def doql_materialize(uri: str, dest: str = "") -> dict[str, Any]:
            """Materialize addressed DOQL content to a file."""
            result = materialize_uri(uri, dest=dest or None)
            return result.to_dict()

        @self.app.tool()
        def doql_validate(path: str) -> dict[str, Any]:
            """Validate a .doql.less/.doql.css manifest."""
            from nlp2doql.validate import validate_doql_file

            return validate_doql_file(path)

        @self.app.tool()
        def doql_run_dsl(script: str, default_file: str = "") -> list[dict[str, Any]]:
            """Execute DOQL control DSL commands (one per line)."""
            results = execute_dsl(script, default_file=default_file or None)
            return [r.to_dict() for r in results]

        @self.app.tool()
        def doql_run_command(command: str, default_file: str = "") -> dict[str, Any]:
            """Execute a single DOQL control DSL command."""
            result = execute_dsl_line(command, default_file=default_file or None)
            return result.to_dict()

        @self.app.tool()
        def doql_run_command_pb(envelope_bytes: bytes, default_file: str = "") -> bytes:
            """Execute protobuf DslEnvelope; returns DslResult protobuf."""
            result = dispatch(envelope_bytes, default_file=default_file or None)
            return encode_result_protobuf(result)

        @self.app.tool()
        def doql_to_dsl(prompt: str) -> str:
            """Convert NL hint to DSL line (no side effects)."""
            from nlp2doql.apply import _intent
            from dsl2doql.grammar import to_text

            intent = _intent(prompt)
            if intent == "validate":
                return to_text({"verb": "VALIDATE", "path": "app.doql.less"})
            if intent == "generate":
                return to_text({"verb": "GENERATE", "text": prompt})
            return to_text({"verb": "RESOLVE", "text": prompt})

        @self.app.tool()
        def doql_resolve(prompt: str, file: str = "") -> list[dict[str, Any]]:
            """Map natural language to doql:// URIs (nlp2uri)."""
            return [hit.to_dict() for hit in nlp2uri(prompt, file=file or None)]

        @self.app.tool()
        def doql_patch(uri: str, content: str, file: str = "") -> dict[str, Any]:
            """Replace a DOQL block referenced by URI."""
            result = patch_uri(uri, content=content, file=file or None)
            return result.to_dict()

        @self.app.tool()
        def doql_update(uri: str, content: str, file: str = "") -> dict[str, Any]:
            """Update a DOQL block referenced by URI."""
            result = update_uri(uri, content=content, file=file or None)
            return result.to_dict()

        @self.app.tool()
        def doql_apply(
            uri: str,
            mode: str = "materialize",
            dest: str = "",
            content: str = "",
            file: str = "",
        ) -> dict[str, Any]:
            """Apply URI action: materialize, patch, append, update."""
            result = apply_uri(
                uri,
                dest=dest or None,
                content=content or None,
                file=file or None,
                mode=mode,
            )
            return result.to_dict()

        @self.app.tool()
        def doql_apply_nl(prompt: str, file: str = "", content: str = "") -> dict[str, Any]:
            """Apply natural-language DOQL control (validate/query/patch/generate)."""
            result = apply_nl(prompt, file=file or None, content=content or None)
            return result.to_dict()

    def run(self) -> None:
        self.app.run()


def create_server(name: str = "doql") -> DoqlMCPServer:
    return DoqlMCPServer(name=name)


def run_server() -> None:
    create_server().run()


if __name__ == "__main__":
    run_server()
