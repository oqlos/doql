"""LSP completion provider."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lsprotocol import types as lsp
    from pygls.lsp.server import LanguageServer

try:
    from lsprotocol import types as lsp
except ImportError:  # pragma: no cover
    pass

from . import server, KEYWORDS, FIELD_KEYWORDS
from .utils import _parse_doc


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
