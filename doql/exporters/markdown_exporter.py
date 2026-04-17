"""Export DoqlSpec → Markdown documentation."""
from __future__ import annotations

import pathlib
from typing import IO

from ..parsers.models import DoqlSpec, Entity, Interface, Workflow, Document, Report


def _h(level: int, text: str) -> str:
    return f"{'#' * level} {text}\n\n"


def _field_type_str(f) -> str:
    """Build human-readable field type string."""
    parts = [f.type]
    if f.required:
        parts.append("required")
    if f.unique:
        parts.append("unique")
    if f.auto:
        parts.append("auto")
    if f.computed:
        parts.append("computed")
    if f.ref:
        parts.append(f"→ {f.ref}")
    if f.default is not None:
        parts.append(f"default={f.default}")
    return ", ".join(parts)


def _entity_section(e: Entity) -> str:
    lines = [_h(3, f"Entity: {e.name}")]
    if e.audit:
        lines.append(f"**Audit:** {e.audit}\n\n")
    if e.fields:
        lines.append("| Field | Type |\n|-------|------|\n")
        for f in e.fields:
            lines.append(f"| `{f.name}` | {_field_type_str(f)} |\n")
        lines.append("\n")
    if e.indexes:
        lines.append(f"**Indexes:** {', '.join(e.indexes)}\n\n")
    return "".join(lines)


def _interface_section(iface: Interface) -> str:
    lines = [_h(3, f"Interface: {iface.name}")]
    lines.append(f"- **Type:** {iface.type}\n")
    if iface.framework:
        lines.append(f"- **Framework:** {iface.framework}\n")
    if iface.pwa:
        lines.append("- **PWA:** yes\n")
    if iface.auth:
        lines.append(f"- **Auth:** {iface.auth}\n")
    lines.append("\n")
    if iface.pages:
        lines.append("**Pages:**\n\n")
        for p in iface.pages:
            desc = f"`{p.name}`"
            if p.layout:
                desc += f" (layout: {p.layout})"
            if p.path:
                desc += f" — `{p.path}`"
            lines.append(f"- {desc}\n")
        lines.append("\n")
    return "".join(lines)


def _workflow_section(w: Workflow) -> str:
    lines = [_h(3, f"Workflow: {w.name}")]
    if w.trigger:
        lines.append(f"- **Trigger:** {w.trigger}\n")
    if w.schedule:
        lines.append(f"- **Schedule:** {w.schedule}\n")
    if w.condition:
        lines.append(f"- **Condition:** {w.condition}\n")
    lines.append("\n")
    if w.steps:
        lines.append("**Steps:**\n\n")
        for i, s in enumerate(w.steps, 1):
            desc = f"{i}. `{s.action}`"
            if s.target:
                desc += f" → {s.target}"
            if s.params:
                desc += f" ({', '.join(f'{k}={v}' for k, v in s.params.items())})"
            lines.append(f"{desc}\n")
        lines.append("\n")
    return "".join(lines)


def _document_section(d: Document) -> str:
    lines = [_h(3, f"Document: {d.name}")]
    lines.append(f"- **Type:** {d.type}\n")
    if d.template:
        lines.append(f"- **Template:** {d.template}\n")
    if d.output:
        lines.append(f"- **Output:** {d.output}\n")
    lines.append("\n")
    return "".join(lines)


def _report_section(r: Report) -> str:
    lines = [_h(3, f"Report: {r.name}")]
    lines.append(f"- **Output:** {r.output}\n")
    if r.schedule:
        lines.append(f"- **Schedule:** {r.schedule}\n")
    if r.template:
        lines.append(f"- **Template:** {r.template}\n")
    lines.append("\n")
    return "".join(lines)


def export_markdown(spec: DoqlSpec, out: IO[str]) -> None:
    """Write DoqlSpec as Markdown documentation to the given stream."""
    out.write(_h(1, spec.app_name))
    out.write(f"**Version:** {spec.version}\n\n")
    if spec.domain:
        out.write(f"**Domain:** {spec.domain}\n\n")
    if spec.languages:
        out.write(f"**Languages:** {', '.join(spec.languages)}\n\n")

    # Data sources
    if spec.data_sources:
        out.write(_h(2, "Data Sources"))
        for ds in spec.data_sources:
            out.write(f"- **{ds.name}** — {ds.source}")
            if ds.file:
                out.write(f" (`{ds.file}`)")
            if ds.url:
                out.write(f" (`{ds.url}`)")
            out.write("\n")
        out.write("\n")

    # Entities
    if spec.entities:
        out.write(_h(2, "Entities"))
        for e in spec.entities:
            out.write(_entity_section(e))

    # Interfaces
    if spec.interfaces:
        out.write(_h(2, "Interfaces"))
        for iface in spec.interfaces:
            out.write(_interface_section(iface))

    # Documents
    if spec.documents:
        out.write(_h(2, "Documents"))
        for d in spec.documents:
            out.write(_document_section(d))

    # Reports
    if spec.reports:
        out.write(_h(2, "Reports"))
        for r in spec.reports:
            out.write(_report_section(r))

    # Workflows
    if spec.workflows:
        out.write(_h(2, "Workflows"))
        for w in spec.workflows:
            out.write(_workflow_section(w))

    # Roles
    if spec.roles:
        out.write(_h(2, "Roles"))
        for role in spec.roles:
            out.write(f"### {role.name}\n\n")
            if role.permissions:
                for p in role.permissions:
                    out.write(f"- {p}\n")
                out.write("\n")

    # Integrations
    if spec.integrations:
        out.write(_h(2, "Integrations"))
        for integ in spec.integrations:
            out.write(f"- **{integ.name}** ({integ.type})\n")
        out.write("\n")

    # Deploy
    if spec.deploy and spec.deploy.target:
        out.write(_h(2, "Deployment"))
        out.write(f"- **Target:** {spec.deploy.target}\n")
        if spec.deploy.rootless:
            out.write("- **Rootless:** yes\n")
        out.write("\n")


def export_markdown_file(spec: DoqlSpec, path: pathlib.Path) -> None:
    """Write DoqlSpec as Markdown to a file."""
    with open(path, "w", encoding="utf-8") as f:
        export_markdown(spec, f)
