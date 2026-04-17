"""Export DoqlSpec → Markdown documentation.

Re-exports the public API from submodules.
"""
from __future__ import annotations

import pathlib
from typing import IO

from ...parsers.models import DoqlSpec
from .sections import (
    _h, _field_type_str, _entity_section, _interface_section,
    _workflow_section, _document_section, _report_section,
)
from .writers import (
    _write_header, _write_data_sources, _write_entities,
    _write_interfaces, _write_documents, _write_reports,
    _write_workflows, _write_roles, _write_integrations,
    _write_deployment,
)


def export_markdown(spec: DoqlSpec, out: IO[str]) -> None:
    """Write DoqlSpec as Markdown documentation to the given stream."""
    _write_header(spec, out)
    _write_data_sources(spec, out)
    _write_entities(spec, out)
    _write_interfaces(spec, out)
    _write_documents(spec, out)
    _write_reports(spec, out)
    _write_workflows(spec, out)
    _write_roles(spec, out)
    _write_integrations(spec, out)
    _write_deployment(spec, out)


def export_markdown_file(spec: DoqlSpec, path: pathlib.Path) -> None:
    """Write DoqlSpec as Markdown to a file."""
    with open(path, "w", encoding="utf-8") as f:
        export_markdown(spec, f)
