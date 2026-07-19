"""Validation logic for parsed DoqlSpec."""
from __future__ import annotations

import pathlib
import re
from typing import Any, Optional

from .models import DoqlSpec, ValidationIssue


def _validate_app_name(spec: DoqlSpec) -> list[ValidationIssue]:
    """Validate APP name is set."""
    issues: list[ValidationIssue] = []
    if not spec.app_name or spec.app_name == "Untitled":
        issues.append(ValidationIssue("APP", "APP name is required", "error"))
    return issues


def _validate_env_refs(spec: DoqlSpec, env_vars: dict[str, str]) -> list[ValidationIssue]:
    """Validate env.* references exist in env vars."""
    issues: list[ValidationIssue] = []
    for ref in spec.env_refs:
        if ref in env_vars:
            continue
        # Treat trailing-underscore refs as wildcard prefixes (e.g. SMTP_ from env.SMTP_*)
        if ref.endswith("_") and any(k.startswith(ref) for k in env_vars):
            continue
        issues.append(ValidationIssue(
            f"env.{ref}",
            f"Referenced env var '{ref}' not found in .env",
            "warning",
        ))
    return issues


def _validate_data_source_files(spec: DoqlSpec, project_root: pathlib.Path) -> list[ValidationIssue]:
    """Validate DATA source files exist."""
    issues: list[ValidationIssue] = []
    for ds in spec.data_sources:
        if ds.file and ds.source in ("json", "sqlite", "csv", "excel"):
            # Absolute paths are deployment targets — warn instead of error
            if pathlib.PurePosixPath(ds.file).is_absolute():
                issues.append(ValidationIssue(
                    f"DATA {ds.name}",
                    f"Absolute path (skipped local check): {ds.file}",
                    "warning",
                ))
                continue
            fpath = project_root / ds.file
            if not fpath.exists():
                issues.append(ValidationIssue(
                    f"DATA {ds.name}",
                    f"File not found: {ds.file}",
                    "error",
                ))
    return issues


def _validate_file_refs(
    items: list[Any],
    project_root: pathlib.Path,
    item_type: str,
    name_attr: str,
    file_attr: str,
    error_msg: str,
) -> list[ValidationIssue]:
    """Generic file reference validator.
    
    Args:
        items: List of objects to validate
        project_root: Root path for resolving relative paths
        item_type: Type label for error messages (e.g., "DOCUMENT", "TEMPLATE")
        name_attr: Attribute name for item name
        file_attr: Attribute name for file path
        error_msg: Error message template (e.g., "Template not found: {file}")
    """
    issues: list[ValidationIssue] = []
    for item in items:
        file_path = getattr(item, file_attr, None)
        if file_path:
            fpath = project_root / file_path
            if not fpath.exists():
                name = getattr(item, name_attr, "unknown")
                issues.append(ValidationIssue(
                    f"{item_type} {name}",
                    error_msg.format(file=file_path),
                    "warning",
                ))
    return issues


def _validate_document_templates(spec: DoqlSpec, project_root: pathlib.Path) -> list[ValidationIssue]:
    """Validate DOCUMENT template files exist."""
    return _validate_file_refs(
        spec.documents, project_root, "DOCUMENT", "name", "template",
        "Template not found: {file}"
    )


def _validate_template_files(spec: DoqlSpec, project_root: pathlib.Path) -> list[ValidationIssue]:
    """Validate TEMPLATE files exist."""
    return _validate_file_refs(
        spec.templates, project_root, "TEMPLATE", "name", "file",
        "File not found: {file}"
    )


def _validate_document_partials(spec: DoqlSpec) -> list[ValidationIssue]:
    """Cross-reference: DOCUMENT partials must reference known TEMPLATEs."""
    issues: list[ValidationIssue] = []
    template_names = {t.name for t in spec.templates}
    for doc in spec.documents:
        for partial in doc.partials:
            if partial not in template_names:
                issues.append(ValidationIssue(
                    f"DOCUMENT {doc.name}",
                    f"Partial '{partial}' not found in TEMPLATEs",
                    "warning",
                ))
    return issues


def _validate_entity_refs(spec: DoqlSpec) -> list[ValidationIssue]:
    """Cross-reference: ENTITY ref fields must reference known entities."""
    issues: list[ValidationIssue] = []
    entity_names = {e.name for e in spec.entities}
    for ent in spec.entities:
        for f in ent.fields:
            if f.ref and f.ref not in entity_names:
                issues.append(ValidationIssue(
                    f"ENTITY {ent.name}.{f.name}",
                    f"References unknown entity '{f.ref}'",
                    "error",
                ))
    return issues


def _validate_interfaces(spec: DoqlSpec) -> list[ValidationIssue]:
    """Warn on interfaces with no pages."""
    issues: list[ValidationIssue] = []
    for iface in spec.interfaces:
        if not iface.pages and iface.name not in ("api",):
            issues.append(ValidationIssue(
                f"INTERFACE {iface.name}",
                "No pages defined (will generate empty shell)",
                "warning",
            ))
    return issues


def _validate_digital_twins(spec: DoqlSpec) -> list[ValidationIssue]:
    """Digital-twin views must be self-bound, read-only and field-allowlisted."""
    issues: list[ValidationIssue] = []
    forbidden = ("password", "secret", "token", "credential", "private_key")
    for twin in spec.digital_twins:
        path = f"DIGITAL_TWIN {twin.name}"
        if not twin.source:
            issues.append(ValidationIssue(path, "source is required", "error"))
        if twin.subject != "self":
            issues.append(ValidationIssue(path, "Only subject=self is safe in v1", "error"))
        if twin.authorization not in {"aql+subject", "subject"}:
            issues.append(ValidationIssue(path, "authorization must be aql+subject or subject", "error"))
        if not twin.read_only:
            issues.append(ValidationIssue(path, "Digital twin self view must be read-only", "error"))
        if not twin.audit:
            issues.append(ValidationIssue(path, "Digital twin access must be audited", "error"))
        if not twin.fields:
            issues.append(ValidationIssue(path, "Explicit fields allowlist is required", "error"))
        if len(twin.fields) > 200 or len(twin.redact) > 200:
            issues.append(ValidationIssue(path, "Digital twin field lists cannot exceed 200 entries", "error"))
        if len(twin.fields) != len(set(twin.fields)):
            issues.append(ValidationIssue(path, "Digital twin fields must be unique", "error"))
        if len(twin.redact) != len(set(twin.redact)):
            issues.append(ValidationIssue(path, "Digital twin redaction paths must be unique", "error"))
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", twin.subject_field):
            issues.append(ValidationIssue(path, "subject-field must be a safe field name", "error"))
        if not twin.route.startswith("/") or ".." in twin.route:
            issues.append(ValidationIssue(path, "route must be an absolute safe path", "error"))
        for field in twin.fields:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", field):
                issues.append(ValidationIssue(path, f"Invalid field name '{field}'", "error"))
            if any(fragment in field.lower() for fragment in forbidden):
                issues.append(ValidationIssue(path, f"Sensitive field '{field}' cannot be exposed", "error"))
        for field in twin.redact:
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*(?:\.[A-Za-z_][A-Za-z0-9_-]*)*", field):
                issues.append(ValidationIssue(path, f"Invalid redaction path '{field}'", "error"))
    return issues


def _validate_deploy_strategy(spec: DoqlSpec) -> list[ValidationIssue]:
    """Warn on deprecated deploy strategy names, suggest canonical ones.

    Mapping (old -> canonical per redeploy):
        docker-compose -> docker_full
        quadlet -> podman_quadlet
        kubernetes -> k3s
    """
    issues: list[ValidationIssue] = []
    if not spec.deploy or not spec.deploy.target:
        return issues

    target = spec.deploy.target
    deprecated_map = {
        "docker-compose": ("docker_full", "docker-compose"),
        "quadlet": ("podman_quadlet", "podman quadlet"),
        "kubernetes": ("k3s", "k3s"),
    }

    if target in deprecated_map:
        canonical, description = deprecated_map[target]
        issues.append(ValidationIssue(
            "DEPLOY.target",
            f"Deprecated strategy '{target}'. Use '{canonical}' (alias preserved for compatibility).",
            "warning",
        ))

    return issues


def validate(
    spec: DoqlSpec,
    env_vars: dict[str, str],
    project_root: Optional[pathlib.Path] = None
) -> list[ValidationIssue]:
    """Validate a parsed DoqlSpec against env vars and internal consistency."""
    issues: list[ValidationIssue] = []

    issues.extend(_validate_app_name(spec))
    issues.extend(_validate_env_refs(spec, env_vars))
    issues.extend(_validate_document_partials(spec))
    issues.extend(_validate_entity_refs(spec))
    issues.extend(_validate_interfaces(spec))
    issues.extend(_validate_digital_twins(spec))
    issues.extend(_validate_deploy_strategy(spec))

    if project_root:
        issues.extend(_validate_data_source_files(spec, project_root))
        issues.extend(_validate_document_templates(spec, project_root))
        issues.extend(_validate_template_files(spec, project_root))

    return issues
