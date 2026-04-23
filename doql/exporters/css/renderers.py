"""CSS block renderers — one function per DoqlSpec model type."""
from __future__ import annotations

from ...parsers.models import (
    DoqlSpec, Entity, DataSource, Template, Document,
    Report, Database, ApiClient, Webhook, Interface,
    Integration, Workflow, Role, Deploy, Environment,
)
from .helpers import _indent, _prop, _field_line


def _render_app(spec: DoqlSpec) -> list[str]:
    lines = ["app {\n"]
    props = []
    props.append(_prop("name", spec.app_name))
    props.append(_prop("version", spec.version))
    if spec.description:
        props.append(_prop("description", spec.description))
    if spec.license:
        props.append(_prop("license", spec.license, quote_str=False))
    if spec.authors:
        props.append(_prop("authors", ", ".join(spec.authors)))
    if spec.keywords:
        props.append(_prop("keywords", ", ".join(spec.keywords)))
    if spec.homepage:
        props.append(_prop("homepage", spec.homepage))
    if spec.repository:
        props.append(_prop("repository", spec.repository))
    if spec.domain:
        props.append(_prop("domain", spec.domain, quote_str=False))
    if spec.languages:
        props.append(_prop("languages", ", ".join(spec.languages), quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_dependencies(spec: DoqlSpec) -> list[str]:
    if not spec.dependencies:
        return []
    lines = ["dependencies {\n"]
    props = []
    for key, value in spec.dependencies.items():
        props.append(_prop(key, value))
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


def _build_interface_props(iface: Interface) -> list[str]:
    """Build property lines for interface block."""
    props = []
    if iface.type != iface.name:
        props.append(_prop("type", iface.type, quote_str=False))
    if iface.framework:
        props.append(_prop("framework", iface.framework, quote_str=False))
    if iface.pwa:
        props.append(_prop("pwa", True))
    if iface.auth:
        if isinstance(iface.auth, dict):
            for k, v in iface.auth.items():
                props.append(_prop(f"auth-{k}", v, quote_str=False))
        else:
            props.append(_prop("auth-method", iface.auth, quote_str=False))
    if iface.hardware:
        for k, v in iface.hardware.items():
            props.append(_prop(f"hardware-{k}", v, quote_str=False))
    if iface.target:
        props.append(_prop("target", iface.target))
    return props


def _build_page_props(p) -> list[str]:
    """Build property lines for page block."""
    pprops = []
    if p.layout:
        pprops.append(_prop("layout", p.layout))
    if getattr(p, 'from_entity', None):
        pprops.append(_prop("from", p.from_entity))
    if p.path:
        pprops.append(_prop("path", p.path))
    if p.public:
        pprops.append(_prop("public", True))
    if p.features:
        pprops.append(_prop("features", ", ".join(p.features), quote_str=False))
    return pprops


def _render_interface(iface: Interface) -> list[str]:
    """Render Interface as CSS block with nested page blocks."""
    selector = f'interface[type="{iface.name}"]'
    lines = [f'{selector} {{\n']
    lines.append(_indent(_build_interface_props(iface)))
    lines.append("}\n")

    for p in iface.pages:
        lines.append(f'{selector} page[name="{p.name}"] {{\n')
        lines.append(_indent(_build_page_props(p)))
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
        # Only add target as separate word if it's not a key in params
        # (e.g., 'cmd' target with cmd=... param should only show cmd=value)
        if s.target and s.target not in s.params:
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
    props = [_prop("target", deploy.target, quote_str=False)]
    if deploy.rootless:
        props.append(_prop("rootless", True))
    for k, v in deploy.config.items():
        if k in ("target", "rootless"):
            continue
        props.append(_prop(k, v, quote_str=False))
    for k, v in deploy.directives.items():
        props.append(f"@{k}: {v};")
    lines.append(_indent(props))
    lines.append("}\n")
    return lines


def _render_environment(env: Environment) -> list[str]:
    lines = [f'environment[name="{env.name}"] {{\n']
    props = [_prop("runtime", env.runtime, quote_str=False)]
    if env.env_file:
        props.append(_prop("env_file", env.env_file))
    if env.ssh_host:
        props.append(_prop("ssh_host", env.ssh_host, quote_str=False))
    if env.replicas > 1:
        props.append(_prop("replicas", env.replicas))
    for k, v in env.config.items():
        props.append(_prop(k, v, quote_str=False))
    lines.append(_indent(props))
    lines.append("}\n")
    return lines
