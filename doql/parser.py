"""doql parser — reads .doql files into a typed specification model.

DEPRECATED: This module is kept for backward compatibility.
Please use `doql.parsers` instead for new code.

The parser has been refactored into a modular package:
  - doql.parsers.models      — Data classes (DoqlSpec, Entity, etc.)
  - doql.parsers.extractors  — Field extraction utilities
  - doql.parsers.registry    — Block handler registry (replaces if/elif chain)
  - doql.parsers.blocks      — Block splitting and application
  - doql.parsers.validators  — Validation logic

This reduces cyclomatic complexity from 49 (original _apply_block)
to ~5 (registry dispatch pattern).
"""
from __future__ import annotations

# Re-export everything from the new parsers package for backward compatibility
from .parsers import (  # noqa: F401
    # Functions
    parse_file,
    parse_text,
    parse_env,
    validate,
    # CSS-like parser
    parse_css_file,
    parse_css_text,
    detect_doql_file,
    # Models
    DoqlSpec,
    DoqlParseError,
    ValidationIssue,
    Entity,
    EntityField,
    DataSource,
    Template,
    Document,
    Report,
    Database,
    ApiClient,
    Webhook,
    Page,
    Interface,
    Integration,
    Workflow,
    WorkflowStep,
    Role,
    Deploy,
    # Internal utilities
    split_blocks,
    apply_block,
    collect_env_refs,
)

# For compatibility with code that imported internal functions
from .parsers.extractors import (  # noqa: F401
    extract_val as _extract_val,
    extract_list as _extract_list,
    extract_yaml_list as _extract_yaml_list,
    extract_pages as _extract_pages,
    extract_entity_fields as _extract_entity_fields,
    collect_env_refs as _collect_env_refs,
)

__all__ = [
    "ApiClient",
    "DataSource",
    "Database",
    "Deploy",
    "Document",
    "DoqlParseError",
    "DoqlSpec",
    "Entity",
    "EntityField",
    "Integration",
    "Interface",
    "Page",
    "Report",
    "Role",
    "Template",
    "ValidationIssue",
    "Webhook",
    "Workflow",
    "WorkflowStep",
    "apply_block",
    "collect_env_refs",
    "detect_doql_file",
    "parse_css_file",
    "parse_css_text",
    "parse_env",
    "parse_file",
    "parse_text",
    "split_blocks",
    "validate",
]

# Provide legacy aliases with underscore prefixes
_split_blocks = split_blocks
_apply_block = apply_block
