"""LSP go-to-definition provider — ENTITY refs."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lsprotocol import types as lsp
    from pygls.lsp.server import LanguageServer

try:
    from lsprotocol import types as lsp
except ImportError:  # pragma: no cover
    pass

from . import server
from .utils import _word_at


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
