"""Markdown section writers — write spec sections to a stream."""
from __future__ import annotations

from typing import IO, Any, Callable

from ...parsers.models import DoqlSpec
from .sections import (
    _h, _entity_section, _interface_section, _workflow_section,
    _document_section, _report_section,
)


def _write_header(spec: DoqlSpec, out: IO[str]) -> None:
    """Write document header with app name, version, domain, and languages."""
    out.write(_h(1, spec.app_name))
    out.write(f"**Version:** {spec.version}\n\n")
    if spec.domain:
        out.write(f"**Domain:** {spec.domain}\n\n")
    if spec.languages:
        out.write(f"**Languages:** {', '.join(spec.languages)}\n\n")


def _write_data_sources(spec: DoqlSpec, out: IO[str]) -> None:
    """Write data sources section."""
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


def _write_section(
    spec: DoqlSpec,
    out: IO[str],
    attr_name: str,
    title: str,
    formatter: Callable[[Any], str],
) -> None:
    """Generic section writer — reduces duplication across entity/interface/document/report/workflow."""
    items = getattr(spec, attr_name, None)
    if items:
        out.write(_h(2, title))
        for item in items:
            out.write(formatter(item))


# Specific writers use the generic implementation
def _write_entities(spec: DoqlSpec, out: IO[str]) -> None:
    _write_section(spec, out, "entities", "Entities", _entity_section)


def _write_interfaces(spec: DoqlSpec, out: IO[str]) -> None:
    _write_section(spec, out, "interfaces", "Interfaces", _interface_section)


def _write_documents(spec: DoqlSpec, out: IO[str]) -> None:
    _write_section(spec, out, "documents", "Documents", _document_section)


def _write_reports(spec: DoqlSpec, out: IO[str]) -> None:
    _write_section(spec, out, "reports", "Reports", _report_section)


def _write_workflows(spec: DoqlSpec, out: IO[str]) -> None:
    _write_section(spec, out, "workflows", "Workflows", _workflow_section)


def _write_roles(spec: DoqlSpec, out: IO[str]) -> None:
    """Write roles section."""
    if spec.roles:
        out.write(_h(2, "Roles"))
        for role in spec.roles:
            out.write(f"### {role.name}\n\n")
            if role.permissions:
                for p in role.permissions:
                    out.write(f"- {p}\n")
                out.write("\n")


def _write_integrations(spec: DoqlSpec, out: IO[str]) -> None:
    """Write integrations section."""
    if spec.integrations:
        out.write(_h(2, "Integrations"))
        for integ in spec.integrations:
            out.write(f"- **{integ.name}** ({integ.type})\n")
        out.write("\n")


def _write_deployment(spec: DoqlSpec, out: IO[str]) -> None:
    """Write deployment section."""
    if spec.deploy and spec.deploy.target:
        out.write(_h(2, "Deployment"))
        out.write(f"- **Target:** {spec.deploy.target}\n")
        if spec.deploy.rootless:
            out.write("- **Rootless:** yes\n")
        out.write("\n")
