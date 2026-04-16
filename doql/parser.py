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
from .parsers.blocks import split_blocks as _split_blocks
from .parsers.extractors import (
    extract_val as _extract_val,
    extract_list as _extract_list,
    extract_yaml_list as _extract_yaml_list,
    extract_pages as _extract_pages,
    extract_entity_fields as _extract_entity_fields,
    collect_env_refs as _collect_env_refs,
)

# Provide legacy aliases with underscore prefixes
_split_blocks = split_blocks
_apply_block = apply_block
_extract_val = _extract_val
_extract_list = _extract_list
_extract_yaml_list = _extract_yaml_list
_extract_pages = _extract_pages
_extract_entity_fields = _extract_entity_fields
_collect_env_refs = _collect_env_refs
