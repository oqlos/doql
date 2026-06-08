"""Query addressed blocks from DoqlSpec."""

from __future__ import annotations

import io
import json
from dataclasses import asdict, dataclass, field, is_dataclass
from typing import Any

import doql
import yaml

from uri2doql.files import resolve_doql_file
from uri2doql.uri import parse_doql_uri


@dataclass
class QueryResult:
    ok: bool
    uri: str
    selector: str
    file: str
    data: Any = None
    rendered: str = ""
    format: str = "json"
    error: str | None = None
    keys: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "uri": self.uri,
            "selector": self.selector,
            "file": self.file,
            "data": self.data,
            "rendered": self.rendered,
            "format": self.format,
            "keys": self.keys,
            "error": self.error,
        }


def _to_plain(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {k: _to_plain(v) for k, v in asdict(value).items()}
    if isinstance(value, list):
        return [_to_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_plain(v) for k, v in value.items()}
    return value


def _render_partial(spec: doql.DoqlSpec, parts: list[str]) -> str:
    from doql.exporters.css.renderers import (
        _render_app,
        _render_deploy,
        _render_entity,
        _render_environment,
        _render_interface,
        _render_workflow,
    )

    if not parts or parts[0] == "app":
        return "".join(_render_app(spec))
    if parts[0] == "deploy":
        return "".join(_render_deploy(spec.deploy))
    if parts[0] == "entity" and len(parts) >= 2:
        entity = next((e for e in spec.entities if e.name == parts[1]), None)
        if entity is None:
            raise ValueError(f"entity not found: {parts[1]}")
        return "".join(_render_entity(entity))
    if parts[0] == "workflow" and len(parts) >= 2:
        workflow = next((w for w in spec.workflows if w.name == parts[1]), None)
        if workflow is None:
            raise ValueError(f"workflow not found: {parts[1]}")
        return "".join(_render_workflow(workflow))
    if parts[0] == "environment" and len(parts) >= 2:
        env = next((e for e in spec.environments if e.name == parts[1]), None)
        if env is None:
            raise ValueError(f"environment not found: {parts[1]}")
        return "".join(_render_environment(env))
    if parts[0] == "interface" and len(parts) >= 2:
        iface = next((i for i in spec.interfaces if i.type == parts[1] or i.name == parts[1]), None)
        if iface is None:
            raise ValueError(f"interface not found: {parts[1]}")
        if len(parts) >= 4 and parts[2] == "page":
            page = next((p for p in iface.pages if p.name == parts[3]), None)
            if page is None:
                raise ValueError(f"page not found: {parts[3]}")
            lines = [
                f'interface[type="{iface.type}"] page[name="{page.name}"] {{\n',
            ]
            if page.layout:
                lines.append(f"  layout: {page.layout};\n")
            if page.path:
                lines.append(f"  path: {page.path};\n")
            if page.entry:
                lines.append(f"  entry: {page.entry};\n")
            lines.append("}\n")
            return "".join(lines)
        return "".join(_render_interface(iface))
    raise ValueError(f"unsupported block path: {'/'.join(parts)}")


def _extract_data(spec: doql.DoqlSpec, parts: list[str]) -> Any:
    if not parts or parts[0] == "app":
        return {
            "name": spec.app_name,
            "version": spec.version,
            "description": spec.description,
            "domain": spec.domain,
            "languages": spec.languages,
            "dependencies": spec.dependencies,
        }
    if parts[0] == "deploy":
        return _to_plain(spec.deploy)
    if parts[0] == "entity" and len(parts) >= 2:
        entity = next((e for e in spec.entities if e.name == parts[1]), None)
        if entity is None:
            raise ValueError(f"entity not found: {parts[1]}")
        return _to_plain(entity)
    if parts[0] == "workflow" and len(parts) >= 2:
        workflow = next((w for w in spec.workflows if w.name == parts[1]), None)
        if workflow is None:
            raise ValueError(f"workflow not found: {parts[1]}")
        return _to_plain(workflow)
    if parts[0] == "environment" and len(parts) >= 2:
        env = next((e for e in spec.environments if e.name == parts[1]), None)
        if env is None:
            raise ValueError(f"environment not found: {parts[1]}")
        return _to_plain(env)
    if parts[0] == "interface" and len(parts) >= 2:
        iface = next((i for i in spec.interfaces if i.type == parts[1] or i.name == parts[1]), None)
        if iface is None:
            raise ValueError(f"interface not found: {parts[1]}")
        if len(parts) >= 4 and parts[2] == "page":
            page = next((p for p in iface.pages if p.name == parts[3]), None)
            if page is None:
                raise ValueError(f"page not found: {parts[3]}")
            return _to_plain(page)
        return _to_plain(iface)
    raise ValueError(f"unsupported block path: {'/'.join(parts)}")


def _selector_from_parts(parts: list[str]) -> str:
    if not parts or parts[0] == "app":
        return "app"
    if parts[0] == "deploy":
        return "deploy"
    if parts[0] == "entity" and len(parts) >= 2:
        return f'entity[name="{parts[1]}"]'
    if parts[0] == "workflow" and len(parts) >= 2:
        return f'workflow[name="{parts[1]}"]'
    if parts[0] == "environment" and len(parts) >= 2:
        return f'environment[name="{parts[1]}"]'
    if parts[0] == "interface" and len(parts) >= 2:
        if len(parts) >= 4 and parts[2] == "page":
            return f'interface[type="{parts[1]}"] page[name="{parts[3]}"]'
        return f'interface[type="{parts[1]}"]'
    return "/".join(parts)


def query_uri(uri: str, *, file: str | None = None, fmt: str | None = None) -> QueryResult:
    parsed = parse_doql_uri(uri)
    source = str(parsed["source"])
    parts = list(parsed["parts"])  # type: ignore[arg-type]
    params = parsed["params"]
    assert isinstance(params, dict)
    file_param = file or str(parsed.get("file") or "")
    output_fmt = (fmt or str(parsed.get("format") or "json")).lower()

    try:
        if source == "file":
            path = resolve_doql_file(parts[0] if parts else file_param or None)
            spec = doql.parse_file(path)
            data = _to_plain(spec)
            buffer = io.StringIO()
            from doql.exporters.css import export_less

            export_less(spec, buffer)
            rendered = buffer.getvalue()
            keys = sorted(data.keys()) if isinstance(data, dict) else []
            return QueryResult(
                ok=True,
                uri=uri,
                selector=str(path),
                file=str(path),
                data=data,
                rendered=rendered,
                format=output_fmt,
                keys=keys,
            )

        if source == "generate":
            prompt = str(parsed.get("prompt") or "")
            if not prompt:
                raise ValueError("doql://generate requires ?prompt=...")
            try:
                from nlp2doql.pipeline import generate_spec
            except ImportError as exc:
                raise RuntimeError("nlp2doql required; pip install 'uri2doql[nlp]'") from exc
            generated = generate_spec(prompt, validate=True)
            if not generated.ok:
                raise RuntimeError(generated.error or "generation failed")
            return QueryResult(
                ok=True,
                uri=uri,
                selector="generate",
                file="",
                data={"prompt": prompt, "planner": generated.plan.planner},
                rendered=generated.doql,
                format="less",
                keys=["prompt", "planner"],
            )

        if source != "block":
            raise ValueError(f"unsupported doql source: {source}")

        path = resolve_doql_file(file_param or None)
        spec = doql.parse_file(path)
        data = _extract_data(spec, parts)
        rendered = _render_partial(spec, parts)
        selector = _selector_from_parts(parts)
        keys = sorted(data.keys()) if isinstance(data, dict) else []
        result = QueryResult(
            ok=True,
            uri=uri,
            selector=selector,
            file=str(path),
            data=data,
            rendered=rendered,
            format=output_fmt,
            keys=keys,
        )
        if output_fmt == "yaml":
            result.rendered = yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
        elif output_fmt == "json":
            result.rendered = json.dumps(data, ensure_ascii=False, indent=2)
        elif output_fmt == "less":
            result.rendered = rendered
        return result
    except Exception as exc:
        return QueryResult(
            ok=False,
            uri=uri,
            selector=_selector_from_parts(parts),
            file=file_param,
            format=output_fmt,
            error=str(exc),
        )
