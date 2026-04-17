"""CSS-like parser for .doql.css, .doql.less, and .doql.sass formats.

Tokenises CSS-like DOQL into (selector, declarations) blocks and maps
them to the same DoqlSpec model used by the classic .doql parser.

Supports:
  - .doql.css  — flat CSS with attribute selectors
  - .doql.less — CSS + @var variables and nesting
  - .doql.sass — whitespace-based (indent-driven), $var, @mixin/@include
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from typing import Optional

from .models import (
    DoqlSpec,
    DoqlParseError,
    ValidationIssue,
    Entity,
    EntityField,
    DataSource,
    Template,
    Document,
    Report,
    Database,
    ApiClient,
    Webhook,
    Interface,
    Page,
    Integration,
    Workflow,
    WorkflowStep,
    Role,
    Deploy,
)
from .extractors import collect_env_refs


# ---------------------------------------------------------------------------
# Tokeniser / block splitter for CSS-like and SASS formats
# ---------------------------------------------------------------------------

@dataclass
class CssBlock:
    """Single CSS-like rule: selector + key-value declarations."""
    selector: str
    declarations: dict[str, str] = field(default_factory=dict)
    children: list["CssBlock"] = field(default_factory=list)
    line: int = 0


def _strip_comments(text: str) -> str:
    """Remove /* ... */ and // line comments."""
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'//[^\n]*', '', text)
    return text


def _resolve_less_vars(text: str) -> str:
    """Expand @variable declarations in .doql.less text."""
    variables: dict[str, str] = {}
    lines = []
    for line in text.splitlines():
        m = re.match(r'^@([\w-]+)\s*:\s*(.+?)\s*;?\s*$', line)
        if m:
            variables[m.group(1)] = m.group(2)
        else:
            lines.append(line)
    result = '\n'.join(lines)
    # Expand variable references (up to 5 passes for nested refs)
    for _ in range(5):
        prev = result
        for name, val in variables.items():
            result = result.replace(f'@{name}', val)
        if result == prev:
            break
    return result


def _resolve_sass_vars(text: str) -> str:
    """Expand $variable declarations in .doql.sass text."""
    variables: dict[str, str] = {}
    lines = []
    for line in text.splitlines():
        m = re.match(r'^\$([\w-]+)\s*:\s*(.+?)\s*$', line)
        if m:
            variables[m.group(1)] = m.group(2)
        else:
            lines.append(line)
    result = '\n'.join(lines)
    for _ in range(5):
        prev = result
        for name, val in variables.items():
            result = result.replace(f'${name}', val)
        if result == prev:
            break
    return result


def _sass_to_css(text: str) -> str:
    """Convert indent-based SASS to brace-delimited CSS for unified parsing.

    This is a minimal conversion — enough for DOQL semantics.
    Strips @mixin definitions and expands @include as comments.
    """
    text = _resolve_sass_vars(text)

    # Collect mixins
    mixins: dict[str, list[str]] = {}
    lines = text.splitlines()
    out_lines: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^@mixin\s+([\w-]+)(?:\(.*?\))?\s*$', line)
        if m:
            # Collect mixin body
            mixin_name = m.group(1)
            body_lines: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith('  ') or lines[i].strip() == ''):
                body_lines.append(lines[i])
                i += 1
            mixins[mixin_name] = body_lines
            continue
        out_lines.append(line)
        i += 1

    # Expand @include
    expanded: list[str] = []
    for line in out_lines:
        m = re.match(r'^(\s*)@include\s+([\w-]+)(?:\(.*?\))?\s*$', line)
        if m:
            indent = m.group(1)
            name = m.group(2)
            if name in mixins:
                for ml in mixins[name]:
                    expanded.append(indent + ml.lstrip())
            else:
                expanded.append(f'{indent}/* @include {name} (unresolved) */')
        else:
            expanded.append(line)

    # Convert indent-based blocks to CSS braces
    result_lines: list[str] = []
    indent_stack: list[int] = []

    for line in expanded:
        stripped = line.rstrip()
        if not stripped:
            continue

        current_indent = len(line) - len(line.lstrip())

        # Close blocks that have ended
        while indent_stack and current_indent <= indent_stack[-1]:
            indent_stack.pop()
            result_lines.append('  ' * len(indent_stack) + '}')

        # Check if this looks like a selector (no colon for value, or multi-word selector)
        is_selector = False
        if ':' not in stripped:
            is_selector = True
        elif re.match(r'^[\w\[\]="\.\-\*\s]+$', stripped.split(':')[0].strip()):
            parts = stripped.split(':', 1)
            # If the part after colon is complex/absent, it's still a property
            if parts[1].strip() and not re.match(r'^[\w\[\]="\.\-\*\s{]+$', parts[1].strip()):
                is_selector = False
            else:
                # It's a property: value pair
                is_selector = False

        # Properties that look like selectors
        if stripped.rstrip().endswith(';'):
            is_selector = False

        # Lines with list syntax - features list items
        if stripped.lstrip().startswith('- '):
            is_selector = False

        # Detect selectors: lines without colon or with [] attributes
        if not is_selector and ('[' in stripped and ']' in stripped) and ':' not in stripped.split(']')[-1]:
            is_selector = True

        if is_selector and not stripped.endswith(';'):
            result_lines.append('  ' * len(indent_stack) + stripped.lstrip() + ' {')
            indent_stack.append(current_indent)
        else:
            prop_line = stripped.lstrip()
            if not prop_line.endswith(';'):
                prop_line += ';'
            result_lines.append('  ' * len(indent_stack) + prop_line)

    # Close remaining open blocks
    while indent_stack:
        indent_stack.pop()
        result_lines.append('  ' * len(indent_stack) + '}')

    return '\n'.join(result_lines)


def _tokenise_css(text: str) -> list[CssBlock]:
    """Parse CSS-like text into flat CssBlock list."""
    blocks: list[CssBlock] = []
    text = _strip_comments(text)

    depth = 0
    current_selector = ''
    current_body = ''
    selector_stack: list[str] = []
    line_num = 0

    i = 0
    while i < len(text):
        ch = text[i]

        if ch == '{':
            if depth == 0:
                current_selector = text[:i].rsplit('}', 1)[-1].strip() if blocks else text[:i].strip()
                # Find selector start: go backwards from i
                sel_start = i - 1
                while sel_start >= 0 and text[sel_start] != '}' and text[sel_start] != ';':
                    sel_start -= 1
                current_selector = text[sel_start + 1:i].strip()
                current_body = ''
                line_num = text[:i].count('\n')
            depth += 1
            if depth > 1:
                current_body += ch
            i += 1
            continue

        if ch == '}':
            depth -= 1
            if depth == 0:
                block = CssBlock(
                    selector=current_selector,
                    declarations=_parse_declarations(current_body),
                    children=_tokenise_css(current_body) if '{' in current_body else [],
                    line=line_num,
                )
                blocks.append(block)
                current_selector = ''
                current_body = ''
            elif depth > 0:
                current_body += ch
            i += 1
            continue

        if depth > 0:
            current_body += ch
        i += 1

    return blocks


def _parse_declarations(body: str) -> dict[str, str]:
    """Extract property: value pairs from a CSS block body (top-level only)."""
    decls: dict[str, str] = {}
    depth = 0
    for line in body.splitlines():
        # Track nesting
        depth += line.count('{') - line.count('}')
        if depth != 0:
            continue
        line = line.strip()
        if not line or line.startswith('/*') or '{' in line or '}' in line:
            continue
        m = re.match(r'^([\w\-]+)\s*:\s*(.+?)\s*;?\s*$', line)
        if m:
            decls[m.group(1)] = m.group(2).rstrip(';').strip()
    return decls


# ---------------------------------------------------------------------------
# Selector parsing
# ---------------------------------------------------------------------------

@dataclass
class ParsedSelector:
    """Decomposed CSS selector."""
    type: str = ""            # e.g. "app", "entity", "interface", "deploy"
    attributes: dict[str, str] = field(default_factory=dict)
    chain: list[str] = field(default_factory=list)  # full selector parts


def _parse_selector(selector: str) -> ParsedSelector:
    """Parse a CSS-like selector into structured form.

    Examples:
        "app" → type="app"
        'entity[name="Node"]' → type="entity", attributes={"name": "Node"}
        'interface[type="web"] page[name="home"]' → type="interface", ...
    """
    parts = selector.strip().split()
    result = ParsedSelector(chain=parts)

    if parts:
        first = parts[0]
        # Extract base type (before first [)
        base_match = re.match(r'^([\w\-]+)', first)
        if base_match:
            result.type = base_match.group(1).lower()

        # Extract all attributes from first part
        for m in re.finditer(r'\[(\w+)=["\']?([^"\'\]]+)["\']?\]', first):
            result.attributes[m.group(1)] = m.group(2)

    return result


# ---------------------------------------------------------------------------
# CSS blocks → DoqlSpec mapping
# ---------------------------------------------------------------------------

def _map_to_spec(blocks: list[CssBlock]) -> DoqlSpec:
    """Map a list of CssBlock nodes to a DoqlSpec."""
    spec = DoqlSpec()

    for block in blocks:
        sel = _parse_selector(block.selector)
        try:
            _apply_css_block(spec, sel, block)
        except Exception as e:
            spec.parse_errors.append(ValidationIssue(
                path=block.selector,
                message=f"Failed to map CSS block: {e}",
                severity="error",
                line=block.line,
            ))

    return spec


def _strip_quotes(val: str) -> str:
    """Strip surrounding quotes from a value."""
    if len(val) >= 2 and val[0] in ('"', "'") and val[-1] == val[0]:
        return val[1:-1]
    return val


def _apply_css_block(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    """Route a single CSS block to the appropriate spec builder."""
    t = sel.type

    if t == 'app':
        spec.app_name = _strip_quotes(block.declarations.get('name', spec.app_name))
        spec.version = _strip_quotes(block.declarations.get('version', spec.version))
        spec.domain = _strip_quotes(block.declarations.get('domain', spec.domain or ''))
        lang = block.declarations.get('languages')
        if lang:
            spec.languages = _parse_list(lang)

    elif t == 'entity':
        _map_entity(spec, sel, block)

    elif t == 'data':
        _map_data_source(spec, sel, block)

    elif t == 'template':
        _map_template(spec, sel, block)

    elif t == 'document':
        _map_document(spec, sel, block)

    elif t == 'report':
        _map_report(spec, sel, block)

    elif t in ('interface', ):
        _map_interface(spec, sel, block)

    elif t == 'integration':
        _map_integration(spec, sel, block)

    elif t == 'workflow':
        _map_workflow(spec, sel, block)

    elif t == 'role':
        _map_role(spec, sel, block)

    elif t == 'deploy':
        _map_deploy(spec, sel, block)

    elif t in ('scenarios', 'api-client'):
        pass  # Informational blocks — no DoqlSpec mapping yet

    elif t == 'database':
        _map_database(spec, sel, block)


# ---------------------------------------------------------------------------
# Individual mappers
# ---------------------------------------------------------------------------

def _parse_list(val: str) -> list[str]:
    """Parse '[a, b, c]' or 'a, b, c' into a list."""
    val = val.strip().strip('[]')
    return [v.strip().strip('"\'') for v in val.split(',') if v.strip()]


def _map_entity(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    name = sel.attributes.get('name', '')
    if not name:
        return

    # Check if entity already exists (for computed blocks etc.)
    existing = next((e for e in spec.entities if e.name == name), None)
    if existing is None:
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
                entity.indexes = _parse_list(val)
            continue

        ef = EntityField(name=key, type=val)
        # Parse type flags
        if '!' in val:
            ef.required = True
            ef.type = val.replace('!', '').strip()
        if 'unique' in val:
            ef.unique = True
            ef.type = ef.type.replace('unique', '').strip()
        if 'computed' in val:
            ef.computed = True
            ef.type = ef.type.replace('computed', '').strip()
        if 'auto' in val:
            ef.auto = True
            ef.type = ef.type.replace('auto', '').strip()
        ref_match = re.search(r'(\w+)\s+ref', val)
        if ref_match:
            ef.ref = ref_match.group(1)
            ef.type = ef.type.replace('ref', '').replace(ref_match.group(1), '').strip()
            if not ef.type:
                ef.type = ref_match.group(1)
        default_match = re.search(r'default\s*=\s*"?([^"\s;]+)"?', val)
        if default_match:
            ef.default = default_match.group(1)
            ef.type = re.sub(r'default\s*=\s*"?[^"\s;]+"?', '', ef.type).strip()

        ef.type = ef.type.strip().rstrip(';')
        if ef.type:
            entity.fields.append(ef)


def _map_data_source(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
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


def _map_template(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    name = sel.attributes.get('name', '')
    tpl = Template(
        name=name,
        type=block.declarations.get('type', 'html'),
        file=block.declarations.get('file', ''),
    )
    vars_str = block.declarations.get('vars')
    if vars_str:
        tpl.variables = _parse_list(vars_str)
    spec.templates.append(tpl)


def _map_document(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    name = sel.attributes.get('name', '')
    doc = Document(
        name=name,
        type=block.declarations.get('type', 'pdf'),
        template=block.declarations.get('template', ''),
    )
    partials = block.declarations.get('partials')
    if partials:
        doc.partials = _parse_list(partials)
    spec.documents.append(doc)


def _map_report(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    name = sel.attributes.get('name', '')
    report = Report(
        name=name,
        schedule=block.declarations.get('schedule', ''),
        template=block.declarations.get('template', ''),
        output=block.declarations.get('output', 'pdf'),
    )
    spec.reports.append(report)


def _map_interface(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    itype = sel.attributes.get('type', '')
    if not itype:
        return

    # Find or create interface
    existing = next((i for i in spec.interfaces if i.type == itype), None)
    if existing is None:
        iface = Interface(
            name=itype,
            type=block.declarations.get('type', itype),
        )
        # Copy declarations
        iface.framework = block.declarations.get('framework')
        iface.theme = block.declarations.get('theme')
        iface.auth = block.declarations.get('auth')
        spec.interfaces.append(iface)
    else:
        iface = existing

    # Check children for pages
    for child in block.children:
        child_sel = _parse_selector(child.selector)
        if child_sel.type == 'page':
            page_name = child_sel.attributes.get('name', '')
            page = Page(name=page_name)
            if 'layout' in child.declarations:
                page.layout = child.declarations['layout']
            if 'from' in child.declarations:
                page.from_entity = child.declarations['from']
            iface.pages.append(page)
        elif child_sel.type == 'endpoint':
            pass  # Endpoints are informational in current spec


def _map_integration(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    name = sel.attributes.get('name', '')
    integration = Integration(
        name=name,
        type=block.declarations.get('type', ''),
    )
    # Copy all declarations as config
    integration.config = dict(block.declarations)
    spec.integrations.append(integration)


def _map_workflow(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
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


def _map_role(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    name = sel.attributes.get('name', '')
    can_str = block.declarations.get('can', '')
    permissions = _parse_list(can_str) if can_str else []
    role = Role(
        name=name,
        permissions=permissions,
    )
    spec.roles.append(role)


def _map_deploy(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    deploy = Deploy(
        target=block.declarations.get('target', ''),
    )
    deploy.config = dict(block.declarations)
    spec.deploy = deploy


def _map_database(spec: DoqlSpec, sel: ParsedSelector, block: CssBlock) -> None:
    name = sel.attributes.get('name', '')
    db = Database(
        name=name,
        type=block.declarations.get('type', ''),
        url=block.declarations.get('url', ''),
    )
    spec.databases.append(db)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_css_file(path: pathlib.Path) -> DoqlSpec:
    """Parse a .doql.css / .doql.less / .doql.sass file into DoqlSpec."""
    if not path.exists():
        raise DoqlParseError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")
    return parse_css_text(text, format=_detect_format(path))


def parse_css_text(text: str, format: str = "css") -> DoqlSpec:
    """Parse CSS-like DOQL source text into a DoqlSpec.

    Args:
        text: Source text.
        format: One of "css", "less", "sass".
    """
    text = _strip_comments(text)

    if format == "less":
        text = _resolve_less_vars(text)
    elif format == "sass":
        text = _sass_to_css(text)

    blocks = _tokenise_css(text)
    spec = _map_to_spec(blocks)
    spec.env_refs = collect_env_refs(text)
    return spec


def _detect_format(path: pathlib.Path) -> str:
    """Detect format from file extension."""
    name = path.name.lower()
    if name.endswith('.doql.sass'):
        return 'sass'
    if name.endswith('.doql.less'):
        return 'less'
    return 'css'
