"""LSP document symbols provider — outline view."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lsprotocol import types as lsp
    from pygls.lsp.server import LanguageServer

try:
    from lsprotocol import types as lsp
except ImportError:  # pragma: no cover
    pass

from . import server
from .utils import _parse_doc, _find_line_col


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
