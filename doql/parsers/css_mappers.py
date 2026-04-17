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


def _add_entity_field(entity: "Entity", name: str, type_str: str) -> None:
    """Parse and add a single field to an entity."""
    from .models import EntityField
    ef = EntityField(name=name, type=type_str)

    # Parse type flags
    current_type = type_str

    if '!' in current_type:
        ef.required = True
        current_type = current_type.replace('!', '').strip()

    if 'unique' in current_type:
        ef.unique = True
        current_type = current_type.replace('unique', '').strip()

    if 'computed' in current_type:
        ef.computed = True
        current_type = current_type.replace('computed', '').strip()

    if 'auto' in current_type:
        ef.auto = True
        current_type = current_type.replace('auto', '').strip()

    # Parse ref
    ref_match = re.search(r'(\w+)\s+ref', current_type)
    if ref_match:
        ef.ref = ref_match.group(1)
        current_type = current_type.replace('ref', '').replace(ref_match.group(1), '').strip()
        if not current_type:
            current_type = ref_match.group(1)

    # Parse default
    default_match = re.search(r'default\s*=\s*"?([^"\s;]+)"?', current_type)
    if default_match:
        ef.default = default_match.group(1)
        current_type = re.sub(r'default\s*=\s*"?[^"\s;]+"?', '', current_type).strip()

    ef.type = current_type.strip().rstrip(';')
    if ef.type:
        entity.fields.append(ef)


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


def _map_template(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Template definition."""
    from .models import Template
    name = sel.attributes.get('name', '')
    tpl = Template(
        name=name,
        type=block.declarations.get('type', 'html'),
        file=block.declarations.get('file', ''),
    )
    vars_str = block.declarations.get('vars')
    if vars_str:
        from .css_utils import _parse_list
        tpl.variables = _parse_list(vars_str)
    spec.templates.append(tpl)


def _map_document(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Document definition."""
    from .models import Document
    name = sel.attributes.get('name', '')
    doc = Document(
        name=name,
        type=block.declarations.get('type', 'pdf'),
        template=block.declarations.get('template', ''),
    )
    partials = block.declarations.get('partials')
    if partials:
        from .css_utils import _parse_list
        doc.partials = _parse_list(partials)
    spec.documents.append(doc)


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


def _map_interface(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Interface definition.

    Handles both top-level ``interface[type="api"] { … }`` blocks and
    compound selectors like ``interface[type="web"] page[name="dash"] { … }``.
    """
    from .models import Interface, Page
    from .css_utils import _parse_selector
    itype = sel.attributes.get('type') or sel.attributes.get('name', '')
    if not itype:
        return

    # Find or create interface (lookup by name = selector attribute value)
    existing = next((i for i in spec.interfaces if i.name == itype), None)
    if existing is None:
        iface = Interface(name=itype, type=itype)
        spec.interfaces.append(iface)
    else:
        iface = existing

    # Compound selector → route the sub-element
    # Strip CSS child combinator '>' from chain before inspection
    chain = [p for p in sel.chain[1:] if p != '>']
    if chain:
        sub = _parse_selector(chain[0])
        if sub.type == 'page':
            _add_interface_page(iface, sub, block)
        # endpoint, feature, widget, menu, sync, card – informational
        return

    # Top-level interface block → apply / back-fill properties
    declared_type = block.declarations.get('type')
    if declared_type:
        iface.type = declared_type
    for key in ('framework', 'theme', 'auth'):
        val = block.declarations.get(key)
        if val and not getattr(iface, key, None):
            setattr(iface, key, val)
    if block.declarations.get('pwa', '').lower() == 'true':
        iface.pwa = True

    # Nested children (rare – if tokenizer ever nests them)
    for child in block.children:
        child_sel = _parse_selector(child.selector)
        if child_sel.type == 'page':
            _add_interface_page(iface, child_sel, child)


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


def _map_workflow(spec: "DoqlSpec", sel: "ParsedSelector", block: "CssBlock") -> None:
    """Map CSS block to Workflow definition."""
    from .css_utils import _parse_selector
    from .models import Workflow, WorkflowStep
    name = sel.attributes.get('name', '')
    # Check if workflow already exists (steps are separate blocks)
    existing = next((w for w in spec.workflows if w.name == name), None)
    if existing is None:
        wf = Workflow(
            name=name,
            trigger=block.declarations.get('trigger', ''),
        )
        spec.workflows.append(wf)
    else:
        wf = existing

    # Parse child steps
    for child in block.children:
        child_sel = _parse_selector(child.selector)
        if child_sel.type == 'step':
            step = WorkflowStep(
                action=child.declarations.get('action', ''),
                target=child.declarations.get('target'),
                params=dict(child.declarations),
            )
            wf.steps.append(step)


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
