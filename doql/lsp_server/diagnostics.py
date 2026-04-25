"""LSP diagnostics — parse errors + validation issues."""
from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lsprotocol import types as lsp
    from pygls.lsp.server import LanguageServer

from .. import parser as doql_parser
from . import server, SERVER_NAME
from .utils import _parse_doc

try:
    from lsprotocol import types as lsp
except ImportError:  # pragma: no cover
    pass


def _diagnostics_for(source: str, uri: str) -> list[lsp.Diagnostic]:
    """Parse, validate and return LSP diagnostics."""
    diagnostics: list[lsp.Diagnostic] = []
    spec = _parse_doc(source)
    if spec is None:
        diagnostics.append(
            lsp.Diagnostic(
                range=lsp.Range(
                    start=lsp.Position(line=0, character=0),
                    end=lsp.Position(line=0, character=1),
                ),
                message="Failed to parse .doql file",
                severity=lsp.DiagnosticSeverity.Error,
                source=SERVER_NAME,
            )
        )
        return diagnostics

    # Read env from project .env if present
    project_root = pathlib.Path(uri.replace("file://", "")).parent if uri.startswith("file://") else pathlib.Path(".")
    env_file = project_root / ".env"
    env_vars = doql_parser.parse_env(env_file) if env_file.exists() else {}

    # Collect parse errors (from error recovery) + validation issues
    all_issues = list(spec.parse_errors) + list(
        doql_parser.validate(spec, env_vars, project_root=project_root)
    )
    for issue in all_issues:
        token = issue.path.split(".")[-1] if issue.path else ""
        # Prefer explicit line/column from the issue when the parser provided them
        if getattr(issue, "line", 0):
            line, col = issue.line, getattr(issue, "column", 0)
        else:
            from .utils import _find_line_col
            line, col = _find_line_col(source, token) if token else (0, 0)
        severity = (
            lsp.DiagnosticSeverity.Error if issue.severity == "error"
            else lsp.DiagnosticSeverity.Warning
        )
        diagnostics.append(
            lsp.Diagnostic(
                range=lsp.Range(
                    start=lsp.Position(line=line, character=col),
                    end=lsp.Position(line=line, character=col + max(len(token), 1)),
                ),
                message=f"{issue.path}: {issue.message}" if issue.path else issue.message,
                severity=severity,
                source=SERVER_NAME,
            )
        )
    return diagnostics


def _on_text_document_event(ls: LanguageServer, uri: str) -> None:
    """Unified handler for text document open/change/save events."""
    doc = ls.workspace.get_text_document(uri)
    ls.publish_diagnostics(doc.uri, _diagnostics_for(doc.source, doc.uri))


@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: lsp.DidOpenTextDocumentParams):
    _on_text_document_event(ls, params.text_document.uri)


@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: lsp.DidChangeTextDocumentParams):
    _on_text_document_event(ls, params.text_document.uri)


@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: lsp.DidSaveTextDocumentParams):
    _on_text_document_event(ls, params.text_document.uri)
