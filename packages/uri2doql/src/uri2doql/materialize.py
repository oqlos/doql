"""Materialize doql:// URIs into files or partial specs."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from uri2doql.files import resolve_doql_file
from uri2doql.query import query_uri
from uri2doql.uri import parse_doql_uri


@dataclass
class MaterializeResult:
    ok: bool
    uri: str
    dest: str
    selector: str = ""
    keys: list[str] = field(default_factory=list)
    source: str = ""
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "dest": self.dest,
            "selector": self.selector,
            "keys": self.keys,
            "source": self.source,
            "error": self.error,
        }


def materialize_uri(uri: str, *, dest: str | None = None) -> MaterializeResult:
    parsed = parse_doql_uri(uri)
    source = str(parsed["source"])
    parts = list(parsed["parts"])  # type: ignore[arg-type]
    params = parsed["params"]
    assert isinstance(params, dict)
    target = dest or str(parsed.get("dest") or "")

    try:
        if source == "file":
            src = resolve_doql_file(parts[0] if parts else None)
            out = Path(target).expanduser().resolve() if target else src
            if target:
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, out)
            return MaterializeResult(
                ok=True,
                uri=uri,
                dest=str(out),
                selector=str(src),
                source=f"file:{src}",
            )

        if source == "generate":
            if not target:
                target = "app.doql.less"
            try:
                from nlp2doql.pipeline import generate_spec
            except ImportError as exc:
                raise RuntimeError("nlp2doql required; pip install 'uri2doql[nlp]'") from exc
            prompt = str(parsed.get("prompt") or "")
            generated = generate_spec(prompt, out_path=target, validate=True)
            if not generated.ok:
                raise RuntimeError(generated.error or "generation failed")
            return MaterializeResult(
                ok=True,
                uri=uri,
                dest=str(Path(target).resolve()),
                selector="generate",
                keys=["prompt"],
                source="nlp2doql",
            )

        if source == "block":
            if not target:
                raise ValueError("block materialize requires --dest or ?dest=")
            fmt = str(params.get("format") or "less")
            query = query_uri(uri, fmt=fmt)
            if not query.ok:
                raise RuntimeError(query.error or "query failed")
            out = Path(target).expanduser().resolve()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(query.rendered, encoding="utf-8")
            return MaterializeResult(
                ok=True,
                uri=uri,
                dest=str(out),
                selector=query.selector,
                keys=query.keys,
                source=f"block:{query.file}",
            )

        raise ValueError(f"unsupported doql source: {source}")
    except Exception as exc:
        fallback_dest = target or ""
        return MaterializeResult(
            ok=False,
            uri=uri,
            dest=fallback_dest,
            error=str(exc),
        )
