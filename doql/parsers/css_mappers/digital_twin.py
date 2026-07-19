"""CSS mapper for subject-bound digital-twin views."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DoqlSpec
    from ..css_utils import CssBlock, ParsedSelector


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() == "true"


def _map_digital_twin(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    from ..css_utils import _parse_list, _strip_quotes
    from ..models import DigitalTwinView

    get = block.declarations.get
    spec.digital_twins.append(DigitalTwinView(
        name=sel.attributes.get("name", ""),
        source=_strip_quotes(get("source", "")) or None,
        subject=_strip_quotes(get("subject", "self")),
        subject_field=_strip_quotes(get("subject-field", "principal")),
        route=_strip_quotes(get("route", "/me/digital-twin")),
        roles=_parse_list(get("roles", "[*]")) or ["*"],
        fields=_parse_list(get("fields", "[]")),
        redact=_parse_list(get("redact", "[]")),
        renderer=_strip_quotes(get("renderer", "profile")),
        authorization=_strip_quotes(get("authorization", "aql+subject")),
        read_only=_bool(get("read-only"), True),
        audit=_bool(get("audit"), True),
    ))
