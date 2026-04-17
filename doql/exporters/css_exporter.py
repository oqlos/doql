"""Export DoqlSpec → CSS / LESS / SASS format (.doql.css/.doql.less/.doql.sass)."""
from __future__ import annotations

import pathlib
from typing import IO

from ..parsers.models import (
    DoqlSpec, Entity, EntityField, DataSource, Template, Document,
    Report, Database, ApiClient, Webhook, Interface, Page,
    Integration, Workflow, WorkflowStep, Role, Deploy,
)


def _indent(lines: list[str], level: int = 1) -> str:
    prefix = "  " * level
    return "\n".join(f"{prefix}{line}" for line in lines) + "\n"


def _prop(key: str, value, quote_str: bool = True) -> str:
    """Format a CSS property line."""
    if isinstance(value, bool):
        return f"{key}: {'true' if value else 'false'};"
    if isinstance(value, (int, float)):
        return f"{key}: {value};"
    s = str(value)
    if quote_str and not s.startswith("env.") and not s.startswith("$") and not s.startswith("@"):
        return f'{key}: "{s}";'
    return f"{key}: {s};"


# ── Entity fields ──────────────────────────────────────────────

def _field_line(f: EntityField) -> str:
    """Render an entity field as a CSS property."""
    parts = [f.type]
    if f.required:
        parts[0] += "!"
    if f.unique:
        parts.append("unique")
    if f.auto:
        parts.append("auto")
    if f.computed:
        parts.append("computed")
    if f.ref:
        parts.append(f"ref={f.ref}")
    if f.default is not None:
        parts.append(f"default={f.default}")
    return f"{f.name}: {' '.join(parts)};"


# ── Block renderers ────────────────────────────────────────────

def _render_app(spec: DoqlSpec) -> list[str]:
    lines = ["app {\n"]
    props = []
    props.append(_prop("name", spec.app_name))
    props.append(_prop("version", spec.version))
    if spec.domain:
        props.append(_prop("domain", spec.domain, quote_str=False))
    if spec.languages:
        props.append(_prop("languages", ", ".join(spec.languages), quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_entity(e: Entity) -> list[str]:
    lines = [f'entity[name="{e.name}"] {{\n']
    props = []
    for f in e.fields:
        props.append(_field_line(f))
    if e.audit:
        props.append(_prop("audit", e.audit))
    if e.indexes:
        props.append(_prop("indexes", ", ".join(e.indexes), quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_data_source(ds: DataSource) -> list[str]:
    lines = [f'data[name="{ds.name}"] {{\n']
    props = []
    props.append(_prop("source", ds.source))
    if ds.file:
        props.append(_prop("file", ds.file))
    if ds.url:
        props.append(_prop("url", ds.url))
    if ds.schema:
        props.append(_prop("schema", ds.schema))
    if ds.auth:
        props.append(_prop("auth", ds.auth))
    if ds.token:
        props.append(_prop("token", ds.token, quote_str=False))
    if ds.cache:
        props.append(_prop("cache", ds.cache))
    if ds.read_only:
        props.append(_prop("read-only", True))
    if ds.env_overrides:
        props.append(_prop("env-overrides", True))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_template(t: Template) -> list[str]:
    lines = [f'template[name="{t.name}"] {{\n']
    props = [_prop("type", t.type)]
    if t.file:
        props.append(_prop("file", t.file))
    if t.engine != "jinja2":
        props.append(_prop("engine", t.engine))
    if t.vars:
        props.append(_prop("vars", ", ".join(t.vars), quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_document(d: Document) -> list[str]:
    lines = [f'document[name="{d.name}"] {{\n']
    props = [_prop("type", d.type)]
    if d.template:
        props.append(_prop("template", d.template))
    if d.output:
        props.append(_prop("output", d.output))
    for k, v in d.data.items():
        props.append(_prop(f"data-{k}", v, quote_str=False))
    for k, v in d.styling.items():
        props.append(_prop(f"styling-{k}", v))
    for k, v in d.metadata.items():
        props.append(_prop(f"metadata-{k}", v))
    for k, v in d.signature.items():
        props.append(_prop(f"signature-{k}", v, quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_report(r: Report) -> list[str]:
    lines = [f'report[name="{r.name}"] {{\n']
    props = [_prop("output", r.output)]
    if r.schedule:
        props.append(_prop("schedule", r.schedule))
    if r.template:
        props.append(_prop("template", r.template))
    if r.retention:
        props.append(_prop("retention", r.retention))
    for k, v in r.query.items():
        props.append(_prop(f"query-{k}", v, quote_str=False))
    for k, v in r.recipients.items():
        props.append(_prop(f"recipients-{k}", v))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_database(db: Database) -> list[str]:
    lines = [f'database[name="{db.name}"] {{\n']
    props = [_prop("type", db.type)]
    if db.url:
        props.append(_prop("url", db.url, quote_str=False))
    if db.file:
        props.append(_prop("file", db.file))
    if db.read_only:
        props.append(_prop("read-only", True))
    if db.backup:
        props.append(_prop("backup", db.backup))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_api_client(ac: ApiClient) -> list[str]:
    lines = [f'api-client[name="{ac.name}"] {{\n']
    props = []
    if ac.base_url:
        props.append(_prop("base-url", ac.base_url, quote_str=False))
    if ac.auth:
        props.append(_prop("auth", ac.auth))
    if ac.token:
        props.append(_prop("token", ac.token, quote_str=False))
    if ac.openapi:
        props.append(_prop("openapi", ac.openapi))
    if ac.retry:
        props.append(_prop("retry", ac.retry))
    if ac.timeout:
        props.append(_prop("timeout", ac.timeout))
    if ac.methods:
        props.append(_prop("methods", ", ".join(ac.methods), quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_webhook(wh: Webhook) -> list[str]:
    lines = [f'webhook[name="{wh.name}"] {{\n']
    props = []
    if wh.source:
        props.append(_prop("source", wh.source))
    if wh.event:
        props.append(_prop("event", wh.event))
    if wh.auth:
        props.append(_prop("auth", wh.auth))
    if wh.secret:
        props.append(_prop("secret", wh.secret, quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_interface(iface: Interface) -> list[str]:
    selector = f'interface[name="{iface.name}"]'
    lines = [f'{selector} {{\n']
    props = [_prop("type", iface.type)]
    if iface.framework:
        props.append(_prop("framework", iface.framework))
    if iface.pwa:
        props.append(_prop("pwa", True))
    if iface.auth:
        for k, v in iface.auth.items():
            props.append(_prop(f"auth-{k}", v, quote_str=False))
    if iface.hardware:
        for k, v in iface.hardware.items():
            props.append(_prop(f"hardware-{k}", v, quote_str=False))
    if iface.target:
        props.append(_prop("target", iface.target))
    lines.append(_indent(props))
    lines.append("}\n")
    # Pages as nested blocks
    for p in iface.pages:
        lines.append(f'{selector} > page[name="{p.name}"] {{\n')
        pprops = []
        if p.layout:
            pprops.append(_prop("layout", p.layout))
        if p.path:
            pprops.append(_prop("path", p.path))
        if p.public:
            pprops.append(_prop("public", True))
        if p.features:
            pprops.append(_prop("features", ", ".join(p.features), quote_str=False))
        lines.append(_indent(pprops))
        lines.append("}\n")
    return lines


def _render_integration(integ: Integration) -> list[str]:
    lines = [f'integration[name="{integ.name}"] {{\n']
    props = [_prop("type", integ.type)]
    for k, v in integ.config.items():
        props.append(_prop(k, v, quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_workflow(w: Workflow) -> list[str]:
    lines = [f'workflow[name="{w.name}"] {{\n']
    props = []
    if w.trigger:
        props.append(_prop("trigger", w.trigger))
    if w.schedule:
        props.append(_prop("schedule", w.schedule))
    if w.condition:
        props.append(_prop("condition", w.condition))
    for i, s in enumerate(w.steps, 1):
        val_parts = [s.action]
        if s.target:
            val_parts.append(s.target)
        if s.params:
            val_parts.extend(f"{k}={v}" for k, v in s.params.items())
        props.append(f"step-{i}: {' '.join(val_parts)};")
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_role(role: Role) -> list[str]:
    lines = [f'role[name="{role.name}"] {{\n']
    props = []
    for perm in role.permissions:
        props.append(f"permit: {perm};")
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_deploy(deploy: Deploy) -> list[str]:
    lines = ["deploy {\n"]
    props = [_prop("target", deploy.target)]
    if deploy.rootless:
        props.append(_prop("rootless", True))
    for k, v in deploy.config.items():
        props.append(_prop(k, v, quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


# ── LESS / SASS wrappers ──────────────────────────────────────

def _css_to_less(css_text: str) -> str:
    """Wrap CSS output with a LESS variable header comment."""
    header = "// LESS format — define @variables here as needed\n\n"
    return header + css_text


def _css_to_sass(css_text: str) -> str:
    """Convert CSS syntax to SASS (indented, no braces/semicolons)."""
    lines = []
    for line in css_text.splitlines():
        stripped = line.rstrip()
        # Skip empty lines
        if not stripped:
            lines.append("")
            continue
        # Comments pass through
        if stripped.startswith("//") or stripped.startswith("/*"):
            lines.append(stripped)
            continue
        if stripped.endswith("*/"):
            lines.append(stripped)
            continue
        # Opening brace — just remove it
        if stripped.endswith("{"):
            lines.append(stripped[:-1].rstrip())
            continue
        # Closing brace — skip
        if stripped.strip() == "}":
            continue
        # Property — remove trailing semicolon
        if stripped.rstrip().endswith(";"):
            lines.append(stripped.rstrip()[:-1])
            continue
        lines.append(stripped)
    return "\n".join(lines) + "\n"


# ── Main export functions ──────────────────────────────────────

def _render_css(spec: DoqlSpec) -> str:
    """Render DoqlSpec as CSS-like .doql.css text."""
    sections: list[list[str]] = []
    sections.append(_render_app(spec))
    for e in spec.entities:
        sections.append(_render_entity(e))
    for ds in spec.data_sources:
        sections.append(_render_data_source(ds))
    for t in spec.templates:
        sections.append(_render_template(t))
    for d in spec.documents:
        sections.append(_render_document(d))
    for r in spec.reports:
        sections.append(_render_report(r))
    for db in spec.databases:
        sections.append(_render_database(db))
    for ac in spec.api_clients:
        sections.append(_render_api_client(ac))
    for wh in spec.webhooks:
        sections.append(_render_webhook(wh))
    for iface in spec.interfaces:
        sections.append(_render_interface(iface))
    for integ in spec.integrations:
        sections.append(_render_integration(integ))
    for w in spec.workflows:
        sections.append(_render_workflow(w))
    for role in spec.roles:
        sections.append(_render_role(role))
    if spec.deploy and spec.deploy.target:
        sections.append(_render_deploy(spec.deploy))
    return "\n".join("".join(s) for s in sections)


def export_css(spec: DoqlSpec, out: IO[str]) -> None:
    """Write DoqlSpec as .doql.css format."""
    out.write(_render_css(spec))


def export_less(spec: DoqlSpec, out: IO[str]) -> None:
    """Write DoqlSpec as .doql.less format."""
    out.write(_css_to_less(_render_css(spec)))


def export_sass(spec: DoqlSpec, out: IO[str]) -> None:
    """Write DoqlSpec as .doql.sass format."""
    out.write(_css_to_sass(_render_css(spec)))


def export_css_file(spec: DoqlSpec, path: pathlib.Path, fmt: str = "css") -> None:
    """Write DoqlSpec to a CSS-like file. fmt is 'css', 'less', or 'sass'."""
    writer = {"css": export_css, "less": export_less, "sass": export_sass}[fmt]
    with open(path, "w", encoding="utf-8") as f:
        writer(spec, f)
