"""CSS block to DoqlSpec mappers.

Maps parsed CSS blocks to the DoqlSpec model structure.
Each mapper handles a specific selector type (entity, interface, etc.)
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import DoqlSpec, Entity, EntityField, Interface, Page
    from .css_utils import CssBlock, ParsedSelector


def _map_entity(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Entity definition."""
    name = sel.attributes.get('name', '')
    if not name:
        return

    # Check if entity already exists (for computed blocks etc.)
    existing = next((e for e in spec.entities if e.name == name), None)
    if existing is None:
        from .models import Entity
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
                from .css_utils import _parse_list
                entity.indexes = _parse_list(val)
            continue

        _add_entity_field(entity, key, val)


def _parse_type_flags(type_str: str) -> "tuple[EntityField, str]":
    """Parse type flags (!, unique, computed, auto) from type string.

    Returns tuple of (EntityField with flags set, cleaned type string).
    """
    from .models import EntityField
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
    from .models import DataSource
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


def _map_config_block(
    spec: "DoqlSpec",
    sel: "ParsedSelector", 
    block: "CssBlock",
    model_class: type,
    list_attr: str,
    defaults: dict[str, str],
    list_fields: dict[str, str],
) -> None:
    """Generic config block mapper for Template/Document/Report.
    
    Args:
        spec: DoqlSpec to append to
        sel: Parsed CSS selector
        block: CSS block with declarations
        model_class: Model class to instantiate (Template, Document, Report)
        list_attr: Attribute name on spec to append to (templates, documents, reports)
        defaults: Default values for model fields
        list_fields: Field names that should be parsed as lists (field_name -> parse_key)
    """
    name = sel.attributes.get('name', '')
    kwargs: dict[str, Any] = {'name': name}
    
    for field, default in defaults.items():
        kwargs[field] = block.declarations.get(field, default)
    
    for field, parse_key in list_fields.items():
        list_str = block.declarations.get(parse_key)
        if list_str:
            from .css_utils import _parse_list
            kwargs[field] = _parse_list(list_str)
    
    obj = model_class(**kwargs)
    getattr(spec, list_attr).append(obj)


def _map_template(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Template definition."""
    from .models import Template
    _map_config_block(
        spec, sel, block,
        model_class=Template,
        list_attr='templates',
        defaults={'type': 'html', 'file': ''},
        list_fields={'vars': 'vars'},
    )


def _map_document(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Document definition."""
    from .models import Document
    _map_config_block(
        spec, sel, block,
        model_class=Document,
        list_attr='documents',
        defaults={'type': 'pdf', 'template': ''},
        list_fields={'partials': 'partials'},
    )


def _map_report(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Report definition."""
    from .models import Report
    name = sel.attributes.get('name', '')
    report = Report(
        name=name,
        schedule=block.declarations.get('schedule', ''),
        template=block.declarations.get('template', ''),
        output=block.declarations.get('output', 'pdf'),
    )
    spec.reports.append(report)


def _find_or_create_interface(spec: "DoqlSpec", name: str) -> "Interface":
    """Find existing interface by name or create new one."""
    from .models import Interface
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
    from .css_utils import _parse_selector
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
    from .css_utils import _parse_selector
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
    from .models import Page
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


def _map_integration(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Integration definition."""
    from .models import Integration
    name = sel.attributes.get('name', '')
    integration = Integration(
        name=name,
        type=block.declarations.get('type', ''),
    )
    # Copy all declarations as config
    integration.config = dict(block.declarations)
    spec.integrations.append(integration)


def _parse_step_text(step_text: str) -> "WorkflowStep":
    """Parse a 'action [target|params...]' step text into a WorkflowStep."""
    from .models import WorkflowStep
    space_idx = step_text.find(' ')
    if space_idx == -1:
        return WorkflowStep(action=step_text, target=None, params={})
    action = step_text[:space_idx]
    rest = step_text[space_idx + 1:]
    target = None
    params: dict = {}
    if rest.startswith('cmd='):
        params['cmd'] = rest[4:].rstrip(';')
        target = 'cmd'
    else:
        for part in rest.split():
            if '=' in part:
                k, v = part.split('=', 1)
                params[k] = v.rstrip(';')
            elif target is None:
                target = part.rstrip(';')
    return WorkflowStep(action=action, target=target, params=params)


def _append_inline_steps(wf, block, strip_quotes_fn) -> None:
    """Append step-N inline declarations from *block* to *wf*."""
    for key, val in block.declarations.items():
        if key.startswith('step-'):
            wf.steps.append(_parse_step_text(strip_quotes_fn(val)))


def _append_child_steps(wf, block, parse_selector_fn, strip_quotes_fn) -> None:
    """Append steps from nested child blocks to *wf*."""
    from .models import WorkflowStep
    for child in block.children:
        child_sel = parse_selector_fn(child.selector)
        if child_sel.type == 'step':
            wf.steps.append(WorkflowStep(
                action=strip_quotes_fn(child.declarations.get('action', '')),
                target=strip_quotes_fn(child.declarations.get('target', '')),
                params={k: strip_quotes_fn(v) for k, v in child.declarations.items()},
            ))


def _map_workflow(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Workflow definition."""
    from .css_utils import _parse_selector, _strip_quotes
    from .models import Workflow
    name = sel.attributes.get('name', '')
    existing = next((w for w in spec.workflows if w.name == name), None)
    if existing is None:
        wf = Workflow(
            name=name,
            trigger=_strip_quotes(block.declarations.get('trigger', '')),
        )
        spec.workflows.append(wf)
    else:
        wf = existing
        if not wf.trigger and block.declarations.get('trigger'):
            wf.trigger = _strip_quotes(block.declarations.get('trigger', ''))

    _append_inline_steps(wf, block, _strip_quotes)
    _append_child_steps(wf, block, _parse_selector, _strip_quotes)


def _map_role(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Role definition."""
    from .css_utils import _parse_list
    from .models import Role
    name = sel.attributes.get('name', '')
    can_str = block.declarations.get('can', '')
    permissions = _parse_list(can_str) if can_str else []
    role = Role(
        name=name,
        permissions=permissions,
    )
    spec.roles.append(role)


def _map_deploy(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Deploy definition."""
    from .models import Deploy
    deploy = Deploy(
        target=block.declarations.get('target', ''),
    )
    for key, val in block.declarations.items():
        if key.startswith('@'):
            deploy.directives[key[1:]] = val
        else:
            deploy.config[key] = val
    spec.deploy = deploy


def _map_database(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Database definition."""
    from .models import Database
    name = sel.attributes.get('name', '')
    db = Database(
        name=name,
        type=block.declarations.get('type', ''),
        url=block.declarations.get('url', ''),
    )
    spec.databases.append(db)


def _map_environment(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Environment definition."""
    from .models import Environment
    name = sel.attributes.get('name', '')
    if not name:
        return
    env = Environment(
        name=name,
        runtime=block.declarations.get('runtime', 'docker-compose'),
    )
    env.env_file = block.declarations.get('env_file')
    env.ssh_host = block.declarations.get('ssh_host')
    replicas = block.declarations.get('replicas')
    if replicas and replicas.isdigit():
        env.replicas = int(replicas)
    # Store remaining declarations as config
    skip = {'runtime', 'env_file', 'ssh_host', 'replicas'}
    for k, v in block.declarations.items():
        if k not in skip:
            env.config[k] = v
    spec.environments.append(env)
