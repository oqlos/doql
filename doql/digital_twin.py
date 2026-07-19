"""Domain-independent enforcement helper for DOQL self digital-twin views."""
from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
import re
from typing import Any, Callable

from .parsers.models import DigitalTwinView


class DigitalTwinAccessError(PermissionError):
    """Raised when a self projection cannot be authorized safely."""


_SENSITIVE_FRAGMENTS = ("password", "secret", "token", "credential", "private_key")
_SAFE_FIELD_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
_SAFE_REDACTION_PATH = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*(?:\.[A-Za-z_][A-Za-z0-9_-]*)*")
_MAX_DEPTH = 16
_MAX_NODES = 10_000


def _sensitive(path: str) -> bool:
    leaf = path.rsplit(".", 1)[-1].lower()
    return any(fragment in leaf for fragment in _SENSITIVE_FRAGMENTS)


def _safe_value(
    value: Any,
    *,
    path: str,
    blocked: set[str],
    redacted: list[str],
    seen: set[int],
    budget: list[int],
    depth: int = 0,
) -> Any:
    if depth > _MAX_DEPTH:
        raise DigitalTwinAccessError("digital_twin_projection_depth_exceeded")
    budget[0] += 1
    if budget[0] > _MAX_NODES:
        raise DigitalTwinAccessError("digital_twin_projection_size_exceeded")
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not isfinite(value):
            raise DigitalTwinAccessError("digital_twin_projection_non_finite_number")
        return value
    if isinstance(value, (Mapping, list, tuple)):
        identity = id(value)
        if identity in seen:
            raise DigitalTwinAccessError("digital_twin_projection_cycle")
        seen.add(identity)
        try:
            if isinstance(value, Mapping):
                result: dict[str, Any] = {}
                for key, child in value.items():
                    if not isinstance(key, str):
                        raise DigitalTwinAccessError("digital_twin_projection_key_invalid")
                    child_path = f"{path}.{key}" if path else key
                    if child_path in blocked or _sensitive(child_path):
                        redacted.append(child_path)
                        continue
                    result[key] = _safe_value(
                        child,
                        path=child_path,
                        blocked=blocked,
                        redacted=redacted,
                        seen=seen,
                        budget=budget,
                        depth=depth + 1,
                    )
                return result
            return [
                _safe_value(
                    child,
                    path=path,
                    blocked=blocked,
                    redacted=redacted,
                    seen=seen,
                    budget=budget,
                    depth=depth + 1,
                )
                for child in value
            ]
        finally:
            seen.remove(identity)
    raise DigitalTwinAccessError("digital_twin_projection_value_invalid")


def project_self_view(
    view: DigitalTwinView,
    *,
    authenticated_subject: str,
    actor_roles: list[str],
    record: Mapping[str, Any],
    aql_authorized: bool = False,
    audit_sink: Callable[[Mapping[str, Any]], None] | None = None,
) -> dict[str, Any]:
    """Return an allowlisted projection only for the authenticated subject.

    The subject always comes from verified runtime identity, never request
    payload. ``aql+subject`` requires an explicit positive AQL decision and
    valid views require an audit sink. The sink receives metadata only, never
    projected values.
    """
    if view.subject != "self" or not view.read_only or not view.audit:
        raise DigitalTwinAccessError("digital_twin_view_not_self_read_only_audited")
    if (
        not view.fields
        or len(view.fields) > 200
        or len(view.redact) > 200
        or len(view.fields) != len(set(view.fields))
        or not _SAFE_FIELD_NAME.fullmatch(view.subject_field)
        or any(not _SAFE_FIELD_NAME.fullmatch(field) or _sensitive(field) for field in view.fields)
        or any(not _SAFE_REDACTION_PATH.fullmatch(field) for field in view.redact)
    ):
        raise DigitalTwinAccessError("digital_twin_field_allowlist_invalid")
    if view.authorization not in {"aql+subject", "subject"}:
        raise DigitalTwinAccessError("digital_twin_authorization_invalid")
    if view.authorization == "aql+subject" and aql_authorized is not True:
        raise DigitalTwinAccessError("digital_twin_aql_authorization_required")
    if audit_sink is None:
        raise DigitalTwinAccessError("digital_twin_audit_sink_required")
    if not authenticated_subject:
        raise DigitalTwinAccessError("digital_twin_authentication_required")
    allowed_roles = set(view.roles)
    if "*" not in allowed_roles and not allowed_roles.intersection(actor_roles):
        raise DigitalTwinAccessError("digital_twin_role_denied")
    if str(record.get(view.subject_field, "")) != authenticated_subject:
        raise DigitalTwinAccessError("digital_twin_subject_mismatch")
    blocked = set(view.redact)
    redacted: list[str] = []
    budget = [0]
    projection: dict[str, Any] = {}
    for name in view.fields:
        if name in blocked:
            redacted.append(name)
            continue
        projection[name] = _safe_value(
            record.get(name),
            path=name,
            blocked=blocked,
            redacted=redacted,
            seen=set(),
            budget=budget,
        )
    if audit_sink is not None:
        audit_sink({
            "schema": "doql.digital-twin.access/v1",
            "view": view.name,
            "subject": authenticated_subject,
            "authorization": view.authorization,
            "roles": sorted(set(actor_roles)),
            "projected_fields": sorted(projection),
            "redacted_paths": sorted(set(redacted)),
        })
    return projection
