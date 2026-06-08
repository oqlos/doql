"""doql:// URI builders and parsing."""

from __future__ import annotations

from urllib.parse import quote, unquote, urlparse

DOQL_SCHEME = "doql"
_FILE_SOURCE = "file"
_BLOCK_SOURCE = "block"
_GENERATE_SOURCE = "generate"


def _encode(value: str) -> str:
    return quote(value, safe="")


def _decode(value: str) -> str:
    return unquote(value or "")


def uri_for_file(path: str, *, dest: str | None = None) -> str:
    uri = f"{DOQL_SCHEME}://{_FILE_SOURCE}/{_encode(path)}"
    if dest:
        uri += f"?dest={_encode(dest)}"
    return uri


def uri_for_block(
    *parts: str,
    file: str | None = None,
    dest: str | None = None,
    fmt: str | None = None,
) -> str:
    encoded = "/".join(_encode(p) for p in parts if p)
    uri = f"{DOQL_SCHEME}://{_BLOCK_SOURCE}/{encoded}"
    params: list[str] = []
    if file:
        params.append(f"file={_encode(file)}")
    if dest:
        params.append(f"dest={_encode(dest)}")
    if fmt:
        params.append(f"format={_encode(fmt)}")
    if params:
        uri += "?" + "&".join(params)
    return uri


def uri_for_generate(prompt: str, *, dest: str | None = None) -> str:
    uri = f"{DOQL_SCHEME}://{_GENERATE_SOURCE}?prompt={_encode(prompt)}"
    if dest:
        uri += f"&dest={_encode(dest)}"
    return uri


def is_doql_uri(uri: str) -> bool:
    return urlparse(uri).scheme.lower() == DOQL_SCHEME


def parse_doql_uri(uri: str) -> dict[str, str | list[str]]:
    if not is_doql_uri(uri):
        raise ValueError(f"not a doql uri: {uri}")
    parsed = urlparse(uri)
    source = _decode(parsed.netloc)
    parts = [_decode(p) for p in parsed.path.split("/") if p]
    params: dict[str, str] = {}
    if parsed.query:
        for chunk in parsed.query.split("&"):
            if "=" in chunk:
                key, value = chunk.split("=", 1)
                params[key] = _decode(value)
    return {
        "source": source,
        "parts": parts,
        "params": params,
        "dest": params.get("dest", ""),
        "file": params.get("file", ""),
        "format": params.get("format", "json"),
        "prompt": params.get("prompt", ""),
        "action": params.get("action", "query"),
    }


def build_doql_uri_index() -> dict[str, dict[str, str]]:
    """Known doql:// URI templates for discovery layers."""
    return {
        uri_for_block("app"): {
            "kind": "block",
            "description": "Read app{} metadata from app.doql.less",
        },
        uri_for_block("entity", "Contact"): {
            "kind": "block",
            "description": "Read entity[name=Contact] block",
        },
        uri_for_block("workflow", "install"): {
            "kind": "block",
            "description": "Read workflow[name=install] block",
        },
        uri_for_block("interface", "cli", "page", "doql"): {
            "kind": "block",
            "description": "Read interface[type=cli] page[name=doql]",
        },
        uri_for_generate("CRM with contacts"): {
            "kind": "generate",
            "description": "Generate DOQL via nlp2doql from NL prompt",
        },
    }
