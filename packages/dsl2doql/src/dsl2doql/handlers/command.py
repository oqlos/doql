"""Write command handlers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dsl2doql.result import DslResult


def _read_content(path: str) -> str:
    return Path(path).expanduser().read_text(encoding="utf-8")


def handle_materialize(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2doql.materialize import materialize_uri

    uri = cmd.get("target", "")
    if default_file and "file=" not in uri:
        sep = "&" if "?" in uri else "?"
        uri = f"{uri}{sep}file={default_file}"
    result = materialize_uri(uri, dest=cmd.get("dest") or None)
    return DslResult(
        ok=result.ok,
        command=line,
        action="materialize",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_generate(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from nlp2doql.pipeline import generate_spec

    generated = generate_spec(cmd.get("text", ""), out_path=cmd.get("out"), validate=True)
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


def handle_patch(cmd: dict[str, Any], *, line: str, default_file: str | None, verb: str = "patch") -> DslResult:
    from uri2doql.patch import patch_uri

    with_path = cmd.get("with_path")
    if not with_path:
        raise ValueError(f"{verb.upper()} requires WITH <fragment-file>")
    content = _read_content(with_path)
    result = patch_uri(cmd.get("target", ""), content=content, file=cmd.get("file") or default_file)
    return DslResult(
        ok=result.ok,
        command=line,
        action=verb,
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_append(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2doql.patch import append_uri

    with_path = cmd.get("with_path")
    if not with_path:
        raise ValueError("APPEND requires WITH <fragment-file>")
    content = _read_content(with_path)
    target = cmd.get("target") or default_file or ""
    result = append_uri(target, content=content, file=cmd.get("file") or default_file or target)
    return DslResult(
        ok=result.ok,
        command=line,
        action="append",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_apply(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from uri2doql.patch import apply_uri

    with_path = cmd.get("with_path")
    content = _read_content(with_path) if with_path else None
    result = apply_uri(
        cmd.get("target", ""),
        dest=cmd.get("dest"),
        content=content,
        file=cmd.get("file") or default_file,
        mode=(cmd.get("mode") or "materialize").lower(),
    )
    return DslResult(
        ok=result.ok,
        command=line,
        action="apply",
        output=json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
        data=result.to_dict(),
        error=result.error,
    )


def handle_convert(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from doql.importers.oql_converter import convert_dsl_to_doql

    src = Path(cmd.get("source", "")).expanduser()
    doql = convert_dsl_to_doql(src.read_text(encoding="utf-8"), default_name=src.stem)
    out = cmd.get("out")
    if out:
        Path(out).write_text(doql, encoding="utf-8")
    return DslResult(
        ok=True,
        command=line,
        action="convert",
        output=doql,
        data={"source": str(src.resolve()), "output": out},
    )


def handle_adopt(cmd: dict[str, Any], *, line: str, default_file: str | None) -> DslResult:
    from doql.adopt.scanner import scan_project
    from doql.exporters.css import export_less

    root = Path(cmd.get("root", ".")).expanduser().resolve()
    out = cmd.get("out") or default_file or "app.doql.less"
    buffer_path = Path(out)
    with buffer_path.open("w", encoding="utf-8") as fh:
        export_less(scan_project(root), fh)
    return DslResult(
        ok=True,
        command=line,
        action="adopt",
        output=str(buffer_path.resolve()),
        data={"root": str(root), "output": str(buffer_path.resolve())},
    )


def handle_from_tokens(line: str, tokens: list[str], *, default_file: str | None) -> DslResult:
    """Legacy token dispatch for engine compatibility."""
    from dsl2doql.grammar import parse_line

    cmd = parse_line(line)
    if cmd is None:
        return DslResult(ok=True, command=line, action="noop")
    verb = cmd["verb"]
    try:
        if verb == "QUERY":
            return handle_query(cmd, line=line, default_file=default_file)
        if verb == "VALIDATE":
            return handle_validate(cmd, line=line, default_file=default_file)
        if verb == "RESOLVE":
            return handle_resolve(cmd, line=line, default_file=default_file)
        if verb == "MATERIALIZE":
            return handle_materialize(cmd, line=line, default_file=default_file)
        if verb == "GENERATE":
            return handle_generate(cmd, line=line, default_file=default_file)
        if verb in {"PATCH", "UPDATE", "REPLACE"}:
            return handle_patch(cmd, line=line, default_file=default_file, verb=verb.lower())
        if verb == "APPEND":
            return handle_append(cmd, line=line, default_file=default_file)
        if verb == "APPLY":
            return handle_apply(cmd, line=line, default_file=default_file)
        if verb == "CONVERT":
            return handle_convert(cmd, line=line, default_file=default_file)
        if verb == "ADOPT":
            return handle_adopt(cmd, line=line, default_file=default_file)
        return DslResult(ok=False, command=line, action=verb.lower(), error=f"unknown command: {verb}")
    except Exception as exc:
        return DslResult(ok=False, command=line, action=verb.lower(), error=str(exc))
