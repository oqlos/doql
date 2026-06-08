"""NL → doql:// URI resolution (nlp2uri layer)."""

from __future__ import annotations

from uri2doql.resolve import ResolvedDoqlUri, resolve_prompt_to_doql_uri


def nlp2uri(
    prompt: str,
    *,
    file: str | None = None,
    dest: str | None = None,
) -> list[ResolvedDoqlUri]:
    """Map natural language to ranked doql:// URIs."""
    return resolve_prompt_to_doql_uri(prompt, file=file, dest=dest)


def best_uri(
    prompt: str,
    *,
    file: str | None = None,
    dest: str | None = None,
) -> ResolvedDoqlUri | None:
    hits = nlp2uri(prompt, file=file, dest=dest)
    return hits[0] if hits else None
