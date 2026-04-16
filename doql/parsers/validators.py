"""Validation logic for parsed DoqlSpec."""
from __future__ import annotations

import pathlib
from typing import Optional

from .models import DoqlSpec, ValidationIssue


def validate(
    spec: DoqlSpec,
    env_vars: dict[str, str],
    project_root: Optional[pathlib.Path] = None
) -> list[ValidationIssue]:
    """Validate a parsed DoqlSpec against env vars and internal consistency."""
    issues: list[ValidationIssue] = []

    # APP name required
    if not spec.app_name or spec.app_name == "Untitled":
        issues.append(ValidationIssue("APP", "APP name is required", "error"))

    # Check env.* references
    for ref in spec.env_refs:
        if ref not in env_vars:
            issues.append(ValidationIssue(
                f"env.{ref}",
                f"Referenced env var '{ref}' not found in .env",
                "warning",
            ))

    # Check DATA source files exist (if project_root given)
    if project_root:
        for ds in spec.data_sources:
            if ds.file and ds.source in ("json", "sqlite", "csv", "excel"):
                fpath = project_root / ds.file
                if not fpath.exists():
                    issues.append(ValidationIssue(
                        f"DATA {ds.name}",
                        f"File not found: {ds.file}",
                        "error",
                    ))

    # Check DOCUMENT templates exist
    if project_root:
        for doc in spec.documents:
            if doc.template:
                tpath = project_root / doc.template
                if not tpath.exists():
                    issues.append(ValidationIssue(
                        f"DOCUMENT {doc.name}",
                        f"Template not found: {doc.template}",
                        "warning",
                    ))

    # Check TEMPLATE files exist
    if project_root:
        for tmpl in spec.templates:
            if tmpl.file:
                tpath = project_root / tmpl.file
                if not tpath.exists():
                    issues.append(ValidationIssue(
                        f"TEMPLATE {tmpl.name}",
                        f"File not found: {tmpl.file}",
                        "warning",
                    ))

    # Cross-reference: DOCUMENT partials must reference known TEMPLATEs
    template_names = {t.name for t in spec.templates}
    for doc in spec.documents:
        for partial in doc.partials:
            if partial not in template_names:
                issues.append(ValidationIssue(
                    f"DOCUMENT {doc.name}",
                    f"Partial '{partial}' not found in TEMPLATEs",
                    "warning",
                ))

    # Cross-reference: ENTITY ref fields must reference known entities
    entity_names = {e.name for e in spec.entities}
    for ent in spec.entities:
        for f in ent.fields:
            if f.ref and f.ref not in entity_names:
                issues.append(ValidationIssue(
                    f"ENTITY {ent.name}.{f.name}",
                    f"References unknown entity '{f.ref}'",
                    "error",
                ))

    # Warn on interfaces with no pages
    for iface in spec.interfaces:
        if not iface.pages and iface.name not in ("api",):
            issues.append(ValidationIssue(
                f"INTERFACE {iface.name}",
                "No pages defined (will generate empty shell)",
                "warning",
            ))

    return issues
