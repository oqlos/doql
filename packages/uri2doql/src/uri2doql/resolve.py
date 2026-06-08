"""NL hints → doql:// URI (for nlp2uri resolve layer)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from uri2doql.uri import uri_for_block, uri_for_file, uri_for_generate


@dataclass(frozen=True)
class ResolvedDoqlUri:
    uri: str
    confidence: float
    match_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "uri": self.uri,
            "confidence": self.confidence,
            "match_reason": self.match_reason,
        }


def resolve_prompt_to_doql_uri(
    prompt: str,
    *,
    file: str | None = None,
    dest: str | None = None,
) -> list[ResolvedDoqlUri]:
    normalized = re.sub(r"\s+", " ", prompt.lower().strip())
    if not normalized:
        return []

    hits: list[ResolvedDoqlUri] = []

    if any(h in normalized for h in ("generate", "wygeneruj", "stwórz", "create", "build app")):
        hits.append(
            ResolvedDoqlUri(
                uri=uri_for_generate(prompt, dest=dest),
                confidence=0.85,
                match_reason="nlp2doql:generate",
            ),
        )

    if any(h in normalized for h in ("app", "manifest", "projekt", "project")):
        uri = uri_for_block("app", file=file) if file else "doql://block/app"
        hits.append(
            ResolvedDoqlUri(uri=uri, confidence=0.78, match_reason="block:app"),
        )

    entity_hints = {
        "contact": "Contact",
        "kontakt": "Contact",
        "workflow": "install",
        "install": "install",
        "test": "test",
        "cli": "cli",
    }
    for hint, name in entity_hints.items():
        if hint in normalized:
            if hint in {"workflow", "install", "test"}:
                uri = uri_for_block("workflow", name, file=file) if file else f"doql://block/workflow/{name}"
            elif hint == "cli":
                uri = (
                    uri_for_block("interface", "cli", "page", "doql", file=file)
                    if file
                    else "doql://block/interface/cli/page/doql"
                )
            else:
                uri = uri_for_block("entity", name, file=file) if file else f"doql://block/entity/{name}"
            hits.append(
                ResolvedDoqlUri(
                    uri=uri,
                    confidence=0.72,
                    match_reason=f"block:{name.lower()}",
                ),
            )

    if any(h in normalized for h in (".doql", "doql file", "plik doql", "app.doql")):
        path = file or "app.doql.less"
        hits.append(
            ResolvedDoqlUri(
                uri=uri_for_file(path, dest=dest),
                confidence=0.8,
                match_reason="file:doql_manifest",
            ),
        )

    seen: set[str] = set()
    unique: list[ResolvedDoqlUri] = []
    for hit in sorted(hits, key=lambda h: h.confidence, reverse=True):
        if hit.uri in seen:
            continue
        seen.add(hit.uri)
        unique.append(hit)
    return unique
