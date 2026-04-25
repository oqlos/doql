"""Integration CSS block mapper."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DoqlSpec
    from ..css_utils import CssBlock, ParsedSelector


def _map_integration(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Integration definition."""
    from ..models import Integration
    name = sel.attributes.get('name', '')
    integration = Integration(
        name=name,
        type=block.declarations.get('type', ''),
    )
    # Copy all declarations as config
    integration.config = dict(block.declarations)
    spec.integrations.append(integration)
