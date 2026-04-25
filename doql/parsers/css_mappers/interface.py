"""Interface and page CSS block mappers."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DoqlSpec, Interface, Page
    from ..css_utils import CssBlock, ParsedSelector


def _find_or_create_interface(spec: "DoqlSpec", name: str) -> "Interface":
    """Find existing interface by name or create new one."""
    from ..models import Interface
    existing = next((i for i in spec.interfaces if i.name == name), None)
    if existing is None:
        iface = Interface(name=name, type=name)
        spec.interfaces.append(iface)
        return iface
    return existing


def _handle_interface_chain(iface: "Interface", sel: "ParsedSelector", block: "CssBlock") -> bool:
    """Handle compound selector chains (e.g., interface page { }).
    
    Returns True if chain was handled (sub-element routed).
    """
    from ..css_utils import _parse_selector
    chain = [p for p in sel.chain[1:] if p != '>']
    if not chain:
        return False
    sub = _parse_selector(chain[0])
    if sub.type == 'page':
        _add_interface_page(iface, sub, block)
    # endpoint, feature, widget, menu, sync, card – informational (no-op)
    return True


def _apply_interface_properties(iface: "Interface", block: "CssBlock") -> None:
    """Apply top-level interface block declarations."""
    declared_type = block.declarations.get('type')
    if declared_type:
        iface.type = declared_type
    for key in ('framework', 'theme', 'auth'):
        val = block.declarations.get(key)
        if val and not getattr(iface, key, None):
            setattr(iface, key, val)
    if block.declarations.get('pwa', '').lower() == 'true':
        iface.pwa = True


def _apply_nested_interface_children(iface: "Interface", block: "CssBlock") -> None:
    """Apply nested children (rare – if tokenizer ever nests them)."""
    from ..css_utils import _parse_selector
    for child in block.children:
        child_sel = _parse_selector(child.selector)
        if child_sel.type == 'page':
            _add_interface_page(iface, child_sel, child)


def _map_interface(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Interface definition.

    Handles both top-level ``interface[type="api"] { … }`` blocks and
    compound selectors like ``interface[type="web"] page[name="dash"] { … }``.
    """
    itype = sel.attributes.get('type') or sel.attributes.get('name', '')
    if not itype:
        return

    iface = _find_or_create_interface(spec, itype)

    if _handle_interface_chain(iface, sel, block):
        return

    _apply_interface_properties(iface, block)
    _apply_nested_interface_children(iface, block)


def _add_interface_page(
    iface: "Interface", sel: "ParsedSelector", block: "CssBlock"
) -> None:
    """Create or update a Page on *iface*."""
    from ..models import Page
    page_name = sel.attributes.get('name', '')
    if not page_name:
        return
    existing = next((p for p in iface.pages if p.name == page_name), None)
    if existing is None:
        page = Page(name=page_name)
        iface.pages.append(page)
    else:
        page = existing
    if 'layout' in block.declarations:
        page.layout = block.declarations['layout']
    if 'from' in block.declarations:
        page.from_entity = block.declarations['from']
