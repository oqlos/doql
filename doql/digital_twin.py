"""Domain-independent enforcement helper for DOQL self digital-twin views."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .parsers.models import DigitalTwinView


class DigitalTwinAccessError(PermissionError):
    """Raised when a self projection cannot be authorized safely."""


def project_self_view(
    view: DigitalTwinView,
    *,
    authenticated_subject: str,
    actor_roles: list[str],
    record: Mapping[str, Any],
) -> dict[str, Any]:
    """Return an allowlisted projection only for the authenticated subject.

    The subject always comes from verified runtime identity, never request
    payload. AQL authorization must be evaluated by the caller when the view
    declares ``aql+subject``.
    """
    if view.subject != "self" or not view.read_only:
        raise DigitalTwinAccessError("digital_twin_view_not_self_read_only")
    if not authenticated_subject:
        raise DigitalTwinAccessError("digital_twin_authentication_required")
    allowed_roles = set(view.roles)
    if "*" not in allowed_roles and not allowed_roles.intersection(actor_roles):
        raise DigitalTwinAccessError("digital_twin_role_denied")
    if str(record.get(view.subject_field, "")) != authenticated_subject:
        raise DigitalTwinAccessError("digital_twin_subject_mismatch")
    blocked = set(view.redact)
    return {name: record.get(name) for name in view.fields if name not in blocked}
