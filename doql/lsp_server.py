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
import pathlib
import re
import sys
from typing import Optional

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

from . import __version__
from . import parser as doql_parser


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


# ─────────────────────────────────────────────────────────
# Server
# ─────────────────────────────────────────────────────────

server = LanguageServer(SERVER_NAME, __version__)


def _parse_doc(source: str) -> Optional[doql_parser.DoqlSpec]:
    """Safely parse a document from its text content."""
    try:
        return doql_parser.parse_text(source)
    except Exception:
        return None


def _find_line_col(source: str, needle: str) -> tuple[int, int]:
    """Return 0-indexed (line, col) of the first occurrence of needle."""
    idx = source.find(needle)
    if idx < 0:
        return 0, 0
    prefix = source[:idx]
    line = prefix.count("\n")
    col = idx - (prefix.rfind("\n") + 1 if "\n" in prefix else 0)
    return line, col


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


def _word_at(source: str, position: lsp.Position) -> str:
    """Extract the word under the cursor."""
    lines = source.splitlines()
    if position.line >= len(lines):
        return ""
    line = lines[position.line]
    start = position.character
    end = position.character
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
        start -= 1
    while end < len(line) and (line[end].isalnum() or line[end] == "_"):
        end += 1
    return line[start:end]


# ─────────────────────────────────────────────────────────
# Handlers
# ─────────────────────────────────────────────────────────

@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: lsp.DidOpenTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.publish_diagnostics(doc.uri, _diagnostics_for(doc.source, doc.uri))


@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: lsp.DidChangeTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.publish_diagnostics(doc.uri, _diagnostics_for(doc.source, doc.uri))


@server.feature(lsp.TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: lsp.DidSaveTextDocumentParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.publish_diagnostics(doc.uri, _diagnostics_for(doc.source, doc.uri))


@server.feature(
    lsp.TEXT_DOCUMENT_COMPLETION,
    lsp.CompletionOptions(trigger_characters=[" ", ":", "."]),
)
def completion(ls: LanguageServer, params: lsp.CompletionParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    spec = _parse_doc(doc.source)

    items: list[lsp.CompletionItem] = []

    # Keywords at start of line
    for kw in KEYWORDS:
        items.append(lsp.CompletionItem(
            label=kw,
            kind=lsp.CompletionItemKind.Keyword,
            detail="doql keyword",
        ))

    # Field attribute keywords
    for fk in FIELD_KEYWORDS:
        items.append(lsp.CompletionItem(
            label=fk,
            kind=lsp.CompletionItemKind.Property,
            detail="field attribute",
        ))

    # Entity names (for refs)
    if spec:
        for ent in spec.entities:
            items.append(lsp.CompletionItem(
                label=ent.name,
                kind=lsp.CompletionItemKind.Class,
                detail=f"entity ({len(ent.fields)} fields)",
            ))

    return lsp.CompletionList(is_incomplete=False, items=items)


@server.feature(lsp.TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params: lsp.HoverParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = _word_at(doc.source, params.position)
    if not word:
        return None

    spec = _parse_doc(doc.source)
    if not spec:
        return None

    # Entity hover
    for ent in spec.entities:
        if ent.name == word:
            fields = "\n".join(f"- `{f.name}`: {f.type}" + (" (unique)" if f.unique else "") for f in ent.fields)
            return lsp.Hover(
                contents=lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=f"**ENTITY `{ent.name}`**\n\n{len(ent.fields)} fields:\n\n{fields}",
                )
            )
        for f in ent.fields:
            if f.name == word:
                details = [f"**{ent.name}.{f.name}**", f"type: `{f.type}`"]
                if f.ref:
                    details.append(f"ref: `{f.ref}`")
                if f.unique:
                    details.append("unique")
                if f.required:
                    details.append("required")
                if f.computed:
                    details.append(f"computed: `{f.computed}`")
                return lsp.Hover(
                    contents=lsp.MarkupContent(
                        kind=lsp.MarkupKind.Markdown,
                        value="\n\n".join(details),
                    )
                )

    # Keyword hover
    if word in KEYWORDS:
        return lsp.Hover(
            contents=lsp.MarkupContent(
                kind=lsp.MarkupKind.Markdown,
                value=f"**doql keyword `{word}`**\n\nSee [doql SPEC](https://github.com/tom-sapletta-com/doql).",
            )
        )

    return None


@server.feature(lsp.TEXT_DOCUMENT_DEFINITION)
def definition(ls: LanguageServer, params: lsp.DefinitionParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = _word_at(doc.source, params.position)
    if not word:
        return None

    # Find "ENTITY <word>:" in source
    pattern = re.compile(rf'^ENTITY\s+{re.escape(word)}\s*:', re.MULTILINE)
    m = pattern.search(doc.source)
    if not m:
        return None

    # Compute line number
    line = doc.source[: m.start()].count("\n")
    col = m.group(0).find(word)
    return lsp.Location(
        uri=doc.uri,
        range=lsp.Range(
            start=lsp.Position(line=line, character=col),
            end=lsp.Position(line=line, character=col + len(word)),
        ),
    )


@server.feature(lsp.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbols(ls: LanguageServer, params: lsp.DocumentSymbolParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    spec = _parse_doc(doc.source)
    if not spec:
        return []

    symbols: list[lsp.DocumentSymbol] = []

    def _mkrange(needle: str) -> lsp.Range:
        line, col = _find_line_col(doc.source, needle)
        return lsp.Range(
            start=lsp.Position(line=line, character=col),
            end=lsp.Position(line=line, character=col + len(needle)),
        )

    for ent in spec.entities:
        needle = f"ENTITY {ent.name}"
        r = _mkrange(needle)
        symbols.append(lsp.DocumentSymbol(
            name=ent.name,
            kind=lsp.SymbolKind.Class,
            range=r, selection_range=r,
            detail=f"{len(ent.fields)} fields",
            children=[
                lsp.DocumentSymbol(
                    name=f.name,
                    kind=lsp.SymbolKind.Field,
                    range=r, selection_range=r,
                    detail=f.type,
                )
                for f in ent.fields
            ],
        ))

    for iface in spec.interfaces:
        needle = f"INTERFACE {iface.name}"
        r = _mkrange(needle)
        symbols.append(lsp.DocumentSymbol(
            name=iface.name,
            kind=lsp.SymbolKind.Interface,
            range=r, selection_range=r,
            detail=f"type: {iface.type}",
        ))

    for wf in spec.workflows:
        needle = f"WORKFLOW {wf.name}"
        r = _mkrange(needle)
        symbols.append(lsp.DocumentSymbol(
            name=wf.name,
            kind=lsp.SymbolKind.Function,
            range=r, selection_range=r,
            detail=wf.trigger or wf.schedule or "",
        ))

    return symbols


# ─────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────

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
