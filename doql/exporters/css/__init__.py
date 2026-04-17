"""Export DoqlSpec → CSS / LESS / SASS format (.doql.css/.doql.less/.doql.sass).

Re-exports the public API from submodules for backward compatibility.
"""
from __future__ import annotations

import pathlib
from typing import IO

from ...parsers.models import DoqlSpec
from .renderers import (
    _render_app, _render_entity, _render_data_source, _render_template,
    _render_document, _render_report, _render_database, _render_api_client,
    _render_webhook, _render_interface, _render_integration, _render_workflow,
    _render_role, _render_deploy, _render_environment,
)
from .format_convert import _css_to_less, _css_to_sass
from .helpers import _indent, _prop, _field_line


# ── Layer aggregators ──────────────────────────────────────────

def _render_data_layer(spec: DoqlSpec) -> list[list[str]]:
    """Render data-related components (entities, data sources, templates)."""
    sections: list[list[str]] = []
    for e in spec.entities:
        sections.append(_render_entity(e))
    for ds in spec.data_sources:
        sections.append(_render_data_source(ds))
    for t in spec.templates:
        sections.append(_render_template(t))
    return sections


def _render_documentation_layer(spec: DoqlSpec) -> list[list[str]]:
    """Render documentation components (documents, reports)."""
    sections: list[list[str]] = []
    for d in spec.documents:
        sections.append(_render_document(d))
    for r in spec.reports:
        sections.append(_render_report(r))
    return sections


def _render_infrastructure_layer(spec: DoqlSpec) -> list[list[str]]:
    """Render infrastructure components (databases, API clients, webhooks)."""
    sections: list[list[str]] = []
    for db in spec.databases:
        sections.append(_render_database(db))
    for ac in spec.api_clients:
        sections.append(_render_api_client(ac))
    for wh in spec.webhooks:
        sections.append(_render_webhook(wh))
    return sections


def _render_integration_layer(spec: DoqlSpec) -> list[list[str]]:
    """Render integration components (interfaces, integrations, workflows, roles)."""
    sections: list[list[str]] = []
    for iface in spec.interfaces:
        sections.append(_render_interface(iface))
    for integ in spec.integrations:
        sections.append(_render_integration(integ))
    for w in spec.workflows:
        sections.append(_render_workflow(w))
    for role in spec.roles:
        sections.append(_render_role(role))
    return sections


def _render_css(spec: DoqlSpec) -> str:
    """Render DoqlSpec as CSS-like .doql.css text."""
    sections: list[list[str]] = []
    sections.append(_render_app(spec))
    sections.extend(_render_data_layer(spec))
    sections.extend(_render_documentation_layer(spec))
    sections.extend(_render_infrastructure_layer(spec))
    sections.extend(_render_integration_layer(spec))
    if spec.deploy and spec.deploy.target:
        sections.append(_render_deploy(spec.deploy))
    for env in spec.environments:
        sections.append(_render_environment(env))
    return "\n".join("".join(s) for s in sections)


# ── Public export API ──────────────────────────────────────────

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
