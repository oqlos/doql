"""Entity and data-source CSS block mappers."""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import DoqlSpec, Entity, EntityField
    from ..css_utils import CssBlock, ParsedSelector


def _map_entity(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Entity definition."""
    name = sel.attributes.get('name', '')
    if not name:
        return

    # Check if entity already exists (for computed blocks etc.)
    existing = next((e for e in spec.entities if e.name == name), None)
    if existing is None:
        from ..models import Entity
        entity = Entity(name=name)
        spec.entities.append(entity)
    else:
        entity = existing

    # Parse field declarations
    for key, val in block.declarations.items():
        if key in ('audit', 'index'):
            if key == 'audit':
                entity.audit = val
            elif key == 'index':
                from ..css_utils import _parse_list
                entity.indexes = _parse_list(val)
            continue

        _add_entity_field(entity, key, val)


def _parse_type_flags(type_str: str) -> "tuple[EntityField, str]":
    """Parse type flags (!, unique, computed, auto) from type string.

    Returns tuple of (EntityField with flags set, cleaned type string).
    """
    from ..models import EntityField
    ef = EntityField(name="", type=type_str)
    current = type_str

    flags = [
        ('!', 'required'),
        ('unique', 'unique'),
        ('computed', 'computed'),
        ('auto', 'auto'),
    ]
    for flag, attr in flags:
        if flag in current:
            setattr(ef, attr, True)
            current = current.replace(flag, '').strip()

    return ef, current


def _add_entity_field(entity: "Entity", name: str, type_str: str) -> None:
    """Parse and add a single field to an entity."""
    ef, current_type = _parse_type_flags(type_str)
    ef.name = name
    ef.type, ef.ref, ef.default = _parse_type_modifiers(current_type)
    if ef.type:
        entity.fields.append(ef)


def _parse_type_modifiers(current_type: str) -> "tuple[str, str | None, str | None]":
    """Parse ref and default modifiers from type string.

    Returns tuple of (cleaned type, ref value or None, default value or None).
    """
    ref: str | None = None
    default: str | None = None

    ref_match = re.search(r'(\w+)\s+ref', current_type)
    if ref_match:
        ref = ref_match.group(1)
        current_type = current_type.replace('ref', '').replace(ref, '').strip()
        if not current_type:
            current_type = ref

    default_match = re.search(r'default\s*=\s*"?([^"\s;]+)"?', current_type)
    if default_match:
        default = default_match.group(1)
        current_type = re.sub(r'default\s*=\s*"?[^"\s;]+"?', '', current_type).strip()

    return current_type.strip().rstrip(';'), ref, default


def _map_data_source(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to DataSource definition."""
    from ..models import DataSource
    name = sel.attributes.get('name', '')
    ds = DataSource(
        name=name,
        source=block.declarations.get('source', 'json'),
        file=block.declarations.get('file'),
        url=block.declarations.get('url'),
        auth=block.declarations.get('auth'),
        token=block.declarations.get('token'),
        cache=block.declarations.get('cache'),
        read_only=block.declarations.get('read_only', '').lower() == 'true',
        env_overrides=block.declarations.get('env_overrides', '').lower() == 'true',
    )
    spec.data_sources.append(ds)
