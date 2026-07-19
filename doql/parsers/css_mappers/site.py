"""DOQL site topology mapper."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DoqlSpec
    from ..css_utils import CssBlock, ParsedSelector


def _map_site(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    from ..models import Site
    from ..css_utils import _strip_quotes

    domain = _strip_quotes(sel.attributes.get("domain", "")).strip().lower().rstrip(".")
    if not domain:
        raise ValueError("site domain is required")
    source = _strip_quotes(block.declarations.get("source", "")) or None
    remote_path = _strip_quotes(block.declarations.get("remote_path", "")) or None
    is_main = _strip_quotes(block.declarations.get("is_main", "")).lower() == "true"
    spec.sites.append(Site(domain=domain, source=source, remote_path=remote_path, is_main=is_main))
