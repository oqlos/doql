"""Export DoqlSpec → Markdown documentation.

Backward-compatibility shim — delegates to doql.exporters.markdown subpackage.
"""
from doql.exporters.markdown import (  # noqa: F401
    _h, _field_type_str, _entity_section, _interface_section,
    _workflow_section, _document_section, _report_section,
    _write_header, _write_data_sources, _write_entities,
    _write_interfaces, _write_documents, _write_reports,
    _write_workflows, _write_roles, _write_integrations,
    _write_deployment, export_markdown, export_markdown_file,
)
