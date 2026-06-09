"""Read-only query handlers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsl2doql.result import DslResult


def _read_content(path: str) -> str:
    return Path(path).expanduser().read_text(encoding="utf-8")


def handle_query(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2doql.query import query_uri

    uri = cmd.get("target", "")
    file_param = cmd.get("file") or default_file
    fmt = (cmd.get("format") or "json").lower()
    result = query_uri(uri, file=file_param, fmt=fmt)
    return DslResult(
        ok=result.ok,
        command=line,
        action="query",
        output=result.rendered or json.dumps(result.data, ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_validate(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from nlp2doql.validate import validate_doql_file

    path = cmd.get("path") or default_file or "app.doql.less"
    result = validate_doql_file(path)
    return DslResult(
        ok=bool(result.get("ok")),
        command=line,
        action="validate",
        output=json.dumps(result, ensure_ascii=False, indent=2),
        data=result,
        error=None if result.get("ok") else str(result.get("errors") or result.get("error")),
    )


def handle_resolve(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2doql.nlp2uri import nlp2uri

    prompt = cmd.get("text", "")
    hits = nlp2uri(prompt, file=cmd.get("file") or default_file)
    payload = [hit.to_dict() for hit in hits]
    return DslResult(
        ok=bool(hits),
        command=line,
        action="resolve",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data={"hits": payload},
        error=None if hits else "no URI matches",
    )
