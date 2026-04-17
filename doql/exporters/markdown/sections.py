"""Markdown section renderers — one per DoqlSpec model type."""
from __future__ import annotations

from ...parsers.models import Entity, Interface, Workflow, Document, Report


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
