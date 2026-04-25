"""LSP hover provider — entity and field info."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lsprotocol import types as lsp
    from pygls.lsp.server import LanguageServer

try:
    from lsprotocol import types as lsp
except ImportError:  # pragma: no cover
    pass

from . import server, KEYWORDS
from .utils import _parse_doc, _word_at


def _hover_field(ent, f) -> lsp.Hover:
    """Return hover info for a field."""
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


def _hover_entity(spec, word) -> lsp.Hover | None:
    """Return hover info if *word* matches an entity name or field."""
    for ent in spec.entities:
        if ent.name == word:
            fields = "\n".join(
                f"- `{f.name}`: {f.type}" + (" (unique)" if f.unique else "")
                for f in ent.fields
            )
            return lsp.Hover(
                contents=lsp.MarkupContent(
                    kind=lsp.MarkupKind.Markdown,
                    value=f"**ENTITY `{ent.name}`**\n\n{len(ent.fields)} fields:\n\n{fields}",
                )
            )
        for f in ent.fields:
            if f.name == word:
                return _hover_field(ent, f)
    return None


@server.feature(lsp.TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params: lsp.HoverParams):
    doc = ls.workspace.get_text_document(params.text_document.uri)
    word = _word_at(doc.source, params.position)
    if not word:
        return None

    spec = _parse_doc(doc.source)
    if not spec:
        return None

    result = _hover_entity(spec, word)
    if result:
        return result

    if word in KEYWORDS:
        return lsp.Hover(
            contents=lsp.MarkupContent(
                kind=lsp.MarkupKind.Markdown,
                value=f"**doql keyword `{word}`**\n\nSee [doql SPEC](https://github.com/tom-sapletta-com/doql).",
            )
        )

    return None
