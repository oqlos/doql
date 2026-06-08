"""DOQL control DSL — execute commands against doql:// URIs and manifests."""

from __future__ import annotations

import json
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DslResult:
    ok: bool
    command: str
    action: str = ""
    output: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "command": self.command,
            "action": self.action,
            "output": self.output,
            "data": self.data,
            "error": self.error,
        }


def _split_command(line: str) -> list[str]:
    line = line.strip()
    if not line or line.startswith("#"):
        return []
    try:
        return shlex.split(line, posix=True)
    except ValueError:
        return line.split()


def _read_content(path: str) -> str:
    return Path(path).expanduser().read_text(encoding="utf-8")


def execute_dsl_line(line: str, *, default_file: str | None = None) -> DslResult:
    tokens = _split_command(line)
    if not tokens:
        return DslResult(ok=True, command=line, action="noop")

    cmd = tokens[0].upper()
    rest = tokens[1:]

    try:
        if cmd == "QUERY":
            return _cmd_query(line, rest, default_file=default_file)
        if cmd == "MATERIALIZE":
            return _cmd_materialize(line, rest, default_file=default_file)
        if cmd == "VALIDATE":
            return _cmd_validate(line, rest)
        if cmd == "GENERATE":
            return _cmd_generate(line, rest)
        if cmd == "RESOLVE":
            return _cmd_resolve(line, rest, default_file=default_file)
        if cmd in {"PATCH", "UPDATE", "REPLACE"}:
            return _cmd_patch(line, rest, default_file=default_file)
        if cmd == "APPEND":
            return _cmd_append(line, rest, default_file=default_file)
        if cmd == "APPLY":
            return _cmd_apply(line, rest, default_file=default_file)
        if cmd == "CONVERT":
            return _cmd_convert(line, rest)
        if cmd == "ADOPT":
            return _cmd_adopt(line, rest)
        return DslResult(ok=False, command=line, action=cmd.lower(), error=f"unknown command: {cmd}")
    except Exception as exc:
        return DslResult(ok=False, command=line, action=cmd.lower(), error=str(exc))


def execute_dsl(text: str, *, default_file: str | None = None) -> list[DslResult]:
    results: list[DslResult] = []
    for line in text.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        results.append(execute_dsl_line(line, default_file=default_file))
    return results


def _pick_flag(rest: list[str], flag: str) -> str | None:
    if flag in rest:
        idx = rest.index(flag)
        if idx + 1 < len(rest):
            return rest[idx + 1]
    return None


def _cmd_query(line: str, rest: list[str], *, default_file: str | None) -> DslResult:
    from uri2doql.query import query_uri

    uri = rest[0]
    file_param = _pick_flag(rest, "FILE") or default_file
    fmt = (_pick_flag(rest, "FORMAT") or "json").lower()
    result = query_uri(uri, file=file_param, fmt=fmt)
    return DslResult(
        ok=result.ok,
        command=line,
        action="query",
        output=result.rendered or json.dumps(result.data, ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def _cmd_materialize(line: str, rest: list[str], *, default_file: str | None) -> DslResult:
    from uri2doql.materialize import materialize_uri

    uri = rest[0]
    dest = _pick_flag(rest, "TO") or _pick_flag(rest, "DEST") or ""
    if default_file and "file=" not in uri:
        sep = "&" if "?" in uri else "?"
        uri = f"{uri}{sep}file={default_file}"
    result = materialize_uri(uri, dest=dest or None)
    return DslResult(
        ok=result.ok,
        command=line,
        action="materialize",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def _cmd_validate(line: str, rest: list[str]) -> DslResult:
    from nlp2doql.validate import validate_doql_file

    path = rest[0]
    result = validate_doql_file(path)
    return DslResult(
        ok=bool(result.get("ok")),
        command=line,
        action="validate",
        output=json.dumps(result, ensure_ascii=False, indent=2),
        data=result,
        error=None if result.get("ok") else str(result.get("errors") or result.get("error")),
    )


def _cmd_generate(line: str, rest: list[str]) -> DslResult:
    from nlp2doql.pipeline import generate_spec

    prompt = rest[0]
    out = _pick_flag(rest, "OUT")
    generated = generate_spec(prompt, out_path=out, validate=True)
    return DslResult(
        ok=generated.ok,
        command=line,
        action="generate",
        output=generated.doql,
        data={
            "output_path": generated.output_path,
            "planner": generated.plan.planner,
            "validation": generated.validation,
        },
        error=generated.error,
    )


def _cmd_resolve(line: str, rest: list[str], *, default_file: str | None) -> DslResult:
    from uri2doql.nlp2uri import nlp2uri

    prompt = " ".join(rest)
    hits = nlp2uri(prompt, file=default_file)
    payload = [hit.to_dict() for hit in hits]
    return DslResult(
        ok=bool(hits),
        command=line,
        action="resolve",
        output=json.dumps(payload, ensure_ascii=False, indent=2),
        data={"hits": payload},
        error=None if hits else "no URI matches",
    )


def _cmd_patch(line: str, rest: list[str], *, default_file: str | None) -> DslResult:
    from uri2doql.patch import patch_uri

    uri = rest[0]
    with_path = _pick_flag(rest, "WITH")
    if not with_path:
        raise ValueError("PATCH requires WITH <fragment-file>")
    content = _read_content(with_path)
    result = patch_uri(uri, content=content, file=default_file)
    return DslResult(
        ok=result.ok,
        command=line,
        action="patch",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def _cmd_append(line: str, rest: list[str], *, default_file: str | None) -> DslResult:
    from uri2doql.patch import append_uri

    target = rest[0] if rest else (default_file or "")
    with_path = _pick_flag(rest, "WITH")
    if not with_path:
        raise ValueError("APPEND requires WITH <fragment-file>")
    content = _read_content(with_path)
    result = append_uri(target, content=content, file=default_file or target)
    return DslResult(
        ok=result.ok,
        command=line,
        action="append",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def _cmd_apply(line: str, rest: list[str], *, default_file: str | None) -> DslResult:
    from uri2doql.patch import apply_uri

    uri = rest[0]
    mode = (_pick_flag(rest, "MODE") or "materialize").lower()
    dest = _pick_flag(rest, "TO") or _pick_flag(rest, "DEST")
    with_path = _pick_flag(rest, "WITH")
    content = _read_content(with_path) if with_path else None
    result = apply_uri(uri, dest=dest, content=content, file=default_file, mode=mode)
    return DslResult(
        ok=result.ok,
        command=line,
        action="apply",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def _cmd_convert(line: str, rest: list[str]) -> DslResult:
    from doql.importers.oql_converter import convert_dsl_to_doql

    src = Path(rest[0]).expanduser()
    dsl_text = src.read_text(encoding="utf-8")
    doql = convert_dsl_to_doql(dsl_text, default_name=src.stem)
    out = _pick_flag(rest, "OUT")
    if out:
        Path(out).write_text(doql, encoding="utf-8")
    return DslResult(
        ok=True,
        command=line,
        action="convert",
        output=doql,
        data={"source": str(src.resolve()), "output": out},
    )


def _cmd_adopt(line: str, rest: list[str]) -> DslResult:
    from doql.adopt.scanner import scan_project
    from doql.exporters.css import export_less

    root = Path(rest[0] if rest else ".").expanduser().resolve()
    out = _pick_flag(rest, "OUT") or "app.doql.less"
    spec = scan_project(root)
    buffer_path = Path(out)
    with buffer_path.open("w", encoding="utf-8") as fh:
        export_less(spec, fh)
    return DslResult(
        ok=True,
        command=line,
        action="adopt",
        output=str(buffer_path.resolve()),
        data={"root": str(root), "output": str(buffer_path.resolve())},
    )
