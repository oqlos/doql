"""doql parser — reads .doql files into a typed specification model.

Block-based parser for doql Language Specification v0.2.
Handles all section types: APP, VERSION, DATA, ENTITY, TEMPLATE, DOCUMENT,
REPORT, DATABASE, API_CLIENT, WEBHOOK, INTERFACE, WORKFLOW, ROLES,
SCENARIOS, TESTS, DEPLOY, INTEGRATION.

Full tree-sitter grammar planned for Faza 1 per ROADMAP.md.
"""
from __future__ import annotations

import pathlib
import re
from dataclasses import dataclass, field
from typing import Any, Optional


# ────────────────────────────────────────────────────────
# Errors
# ────────────────────────────────────────────────────────

class DoqlParseError(Exception):
    """Raised when a .doql file cannot be parsed."""


# ────────────────────────────────────────────────────────
# Data models (SPEC v0.2 — all section types)
# ────────────────────────────────────────────────────────

@dataclass
class ValidationIssue:
    path: str
    message: str
    severity: str = "error"  # "error" | "warning"


@dataclass
class EntityField:
    name: str
    type: str
    required: bool = False
    unique: bool = False
    computed: bool = False
    ref: Optional[str] = None
    default: Optional[str] = None
    auto: bool = False


@dataclass
class Entity:
    name: str
    fields: list[EntityField] = field(default_factory=list)
    audit: Optional[str] = None
    indexes: list[str] = field(default_factory=list)


@dataclass
class DataSource:
    name: str
    source: str = "json"
    file: Optional[str] = None
    url: Optional[str] = None
    schema: Optional[str] = None
    auth: Optional[str] = None
    token: Optional[str] = None
    cache: Optional[str] = None
    read_only: bool = False
    env_overrides: bool = False


@dataclass
class Template:
    name: str
    type: str = "html"
    file: Optional[str] = None
    content: Optional[str] = None
    vars: list[str] = field(default_factory=list)
    engine: str = "jinja2"


@dataclass
class Document:
    name: str
    type: str = "pdf"
    template: Optional[str] = None
    data: dict[str, Any] = field(default_factory=dict)
    output: Optional[str] = None
    styling: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    signature: dict[str, Any] = field(default_factory=dict)
    hooks: dict[str, Any] = field(default_factory=dict)
    partials: list[str] = field(default_factory=list)


@dataclass
class Report:
    name: str
    schedule: Optional[str] = None
    template: Optional[str] = None
    output: str = "pdf"
    query: dict[str, Any] = field(default_factory=dict)
    recipients: dict[str, Any] = field(default_factory=dict)
    retention: Optional[str] = None


@dataclass
class Database:
    name: str
    type: str = "sqlite"
    url: Optional[str] = None
    file: Optional[str] = None
    read_only: bool = False
    backup: Optional[str] = None


@dataclass
class ApiClient:
    name: str
    base_url: Optional[str] = None
    auth: Optional[str] = None
    token: Optional[str] = None
    openapi: Optional[str] = None
    retry: int = 0
    timeout: Optional[str] = None
    methods: list[str] = field(default_factory=list)


@dataclass
class Webhook:
    name: str
    source: Optional[str] = None
    event: Optional[str] = None
    auth: Optional[str] = None
    secret: Optional[str] = None


@dataclass
class Page:
    name: str
    layout: Optional[str] = None
    features: list[str] = field(default_factory=list)
    path: Optional[str] = None
    public: bool = False


@dataclass
class Interface:
    name: str
    type: str = "spa"
    pages: list[Page] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    target: Optional[str] = None
    auth: dict[str, Any] = field(default_factory=dict)
    hardware: dict[str, Any] = field(default_factory=dict)
    framework: Optional[str] = None
    pwa: bool = False


@dataclass
class Integration:
    name: str
    type: str = "email"
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    action: str
    target: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    name: str
    trigger: Optional[str] = None
    schedule: Optional[str] = None
    condition: Optional[str] = None
    steps: list[WorkflowStep] = field(default_factory=list)


@dataclass
class Role:
    name: str
    permissions: list[str] = field(default_factory=list)


@dataclass
class Deploy:
    target: str = "docker-compose"
    rootless: bool = False
    containers: list[dict[str, Any]] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class DoqlSpec:
    app_name: str = "Untitled"
    version: str = "0.1.0"
    domain: Optional[str] = None
    languages: list[str] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    data_sources: list[DataSource] = field(default_factory=list)
    templates: list[Template] = field(default_factory=list)
    documents: list[Document] = field(default_factory=list)
    reports: list[Report] = field(default_factory=list)
    databases: list[Database] = field(default_factory=list)
    api_clients: list[ApiClient] = field(default_factory=list)
    webhooks: list[Webhook] = field(default_factory=list)
    scenarios: list[str] = field(default_factory=list)
    tests: list[str] = field(default_factory=list)
    interfaces: list[Interface] = field(default_factory=list)
    integrations: list[Integration] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)
    roles: list[Role] = field(default_factory=list)
    deploy: Deploy = field(default_factory=Deploy)
    env_refs: list[str] = field(default_factory=list)


# ────────────────────────────────────────────────────────
# Block splitter — finds top-level sections
# ────────────────────────────────────────────────────────

# Top-level keywords that start a new block (column 0, no indent)
_BLOCK_RE = re.compile(
    r'^(APP|VERSION|DOMAIN|AUTHOR|LANGUAGES|DEFAULT_LANGUAGE'
    r'|ENTITY|DATA|TEMPLATE|DOCUMENT|REPORT|DATABASE'
    r'|API_CLIENT|WEBHOOK|INTERFACE|INTEGRATION'
    r'|WORKFLOW|ROLES|ROLE|SCENARIOS|TESTS|DEPLOY)\b',
    re.MULTILINE,
)


def _split_blocks(text: str) -> list[tuple[str, str, str]]:
    """Split .doql text into (keyword, rest_of_header, body) blocks."""
    matches = list(_BLOCK_RE.finditer(text))
    blocks: list[tuple[str, str, str]] = []
    for i, m in enumerate(matches):
        keyword = m.group(1)
        # header = rest of the first line after the keyword
        line_end = text.find("\n", m.start())
        if line_end == -1:
            line_end = len(text)
        header = text[m.end():line_end].strip()
        # body = everything indented until the next block
        body_start = line_end + 1
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[body_start:body_end]
        blocks.append((keyword, header, body))
    return blocks


def _extract_val(body: str, key: str) -> Optional[str]:
    """Extract 'key: value' from an indented block body."""
    m = re.search(rf'^\s+{re.escape(key)}:[ \t]*(.+)', body, re.MULTILINE)
    return m.group(1).strip().strip('"').strip("'") if m else None


def _extract_list(body: str, key: str) -> list[str]:
    """Extract 'key: [a, b, c]' or 'key: value' from body."""
    raw = _extract_val(body, key)
    if not raw:
        return []
    raw = raw.strip("[]")
    return [v.strip().strip('"').strip("'") for v in raw.split(",") if v.strip()]


def _extract_yaml_list(body: str, key: str) -> list[str]:
    """Extract YAML-style list items under a key: header."""
    m = re.search(rf'^\s+{re.escape(key)}:[ \t]*$', body, re.MULTILINE)
    if not m:
        return []
    start = m.end()
    items: list[str] = []
    for line in body[start:].splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
        else:
            break
    return items


def _extract_pages(body: str) -> list[Page]:
    """Extract PAGE definitions from INTERFACE body.

    Supports two formats:
      1. ``PAGE name:``  (web/mobile/desktop)
      2. ``PAGES:`` followed by ``- name:``  (kiosk)
    """
    pages: list[Page] = []

    # Format 1: PAGE keyword
    for m in re.finditer(r'^\s+PAGE\s+(\w+):', body, re.MULTILINE):
        name = m.group(1)
        page_start = m.end()
        next_page = re.search(r'^\s+PAGE\s+\w+:', body[page_start:], re.MULTILINE)
        next_top = re.search(r'^[A-Z]', body[page_start:], re.MULTILINE)
        end = len(body)
        if next_page:
            end = min(end, page_start + next_page.start())
        if next_top:
            end = min(end, page_start + next_top.start())
        sub = body[page_start:end]
        layout = _extract_val(sub, "layout")
        path = _extract_val(sub, "path")
        public_s = _extract_val(sub, "public")
        pages.append(Page(
            name=name,
            layout=layout,
            path=path,
            public=public_s == "true" if public_s else False,
        ))

    # Format 2: PAGES: with YAML list items (- name:)
    if not pages:
        pages_m = re.search(r'^(\s+)PAGES:[ \t]*$', body, re.MULTILINE)
        if pages_m:
            pages_indent = len(pages_m.group(1))
            pages_body = body[pages_m.end():]
            # Only match items at exactly pages_indent+4 spaces (or first-found indent)
            first_item = re.search(r'^(\s+)-\s+(\w+):', pages_body, re.MULTILINE)
            if first_item:
                item_indent = first_item.group(1)
                # Find all items at exactly this indent level
                item_re = re.compile(rf'^{re.escape(item_indent)}-\s+(\w+):', re.MULTILINE)
                matches = list(item_re.finditer(pages_body))
                for idx, item_m in enumerate(matches):
                    name = item_m.group(1)
                    item_start = item_m.end()
                    end = matches[idx + 1].start() if idx + 1 < len(matches) else len(pages_body)
                    sub = pages_body[item_start:end]
                    layout = _extract_val(sub, "layout")
                    path = _extract_val(sub, "path")
                    public_s = _extract_val(sub, "public")
                    pages.append(Page(
                        name=name,
                        layout=layout,
                        path=path,
                        public=public_s == "true" if public_s else False,
                    ))

    return pages


def _extract_entity_fields(body: str) -> list[EntityField]:
    """Extract field definitions from ENTITY body."""
    fields: list[EntityField] = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("COMPUTED") or line.startswith("INDEX") or line.startswith("AUDIT"):
            continue
        if ":" not in line:
            continue
        # skip sub-blocks like IF/ELSE
        if line.startswith("IF ") or line.startswith("ELSE"):
            continue
        parts = line.split(":", 1)
        fname = parts[0].strip()
        ftype_raw = parts[1].strip() if len(parts) > 1 else "string"
        if not fname or not fname[0].islower():
            continue
        required = "!" in ftype_raw
        unique = "unique" in ftype_raw.lower()
        auto = "auto" in ftype_raw.lower()
        computed = "computed" in ftype_raw.lower()
        ref_m = re.search(r'(\w+)\s+ref', ftype_raw)
        ref = ref_m.group(1) if ref_m else None
        default_m = re.search(r'default=(\S+)', ftype_raw)
        default = default_m.group(1) if default_m else None
        # clean type
        base_type = re.split(r'[!\s]', ftype_raw)[0]
        fields.append(EntityField(
            name=fname, type=base_type, required=required,
            unique=unique, computed=computed, ref=ref,
            default=default, auto=auto,
        ))
    return fields


def _collect_env_refs(text: str) -> list[str]:
    """Find all env.VAR_NAME references in the text."""
    return sorted(set(re.findall(r'env\.([A-Z_][A-Z0-9_]*)', text)))


# ────────────────────────────────────────────────────────
# Main parse
# ────────────────────────────────────────────────────────

def parse_file(path: pathlib.Path) -> DoqlSpec:
    """Parse a .doql file into a DoqlSpec."""
    if not path.exists():
        raise DoqlParseError(f"File not found: {path}")

    text = path.read_text(encoding="utf-8")
    spec = DoqlSpec()
    spec.env_refs = _collect_env_refs(text)

    for keyword, header, body in _split_blocks(text):

        if keyword == "APP":
            m = re.match(r':\s*"(.+)"', header)
            spec.app_name = m.group(1) if m else header.strip(': "')

        elif keyword == "VERSION":
            spec.version = header.strip(': "\'')

        elif keyword == "DOMAIN":
            spec.domain = header.strip(': "\'')

        elif keyword == "LANGUAGES":
            raw = header.strip(": ")
            spec.languages = [v.strip().strip('"\'') for v in raw.strip("[]").split(",") if v.strip()]

        elif keyword == "ENTITY":
            name = header.split(":")[0].strip()
            fields = _extract_entity_fields(body)
            audit = _extract_val(body, "AUDIT")
            idx = _extract_list(body, "INDEX")
            spec.entities.append(Entity(name=name, fields=fields, audit=audit, indexes=idx))

        elif keyword == "DATA":
            name = header.split(":")[0].strip()
            source = _extract_val(body, "source") or "json"
            spec.data_sources.append(DataSource(
                name=name,
                source=source,
                file=_extract_val(body, "file"),
                url=_extract_val(body, "url"),
                schema=_extract_val(body, "schema"),
                auth=_extract_val(body, "auth"),
                token=_extract_val(body, "token"),
                cache=_extract_val(body, "cache"),
                read_only=_extract_val(body, "read_only") == "true",
                env_overrides=_extract_val(body, "env_overrides") == "true",
            ))

        elif keyword == "TEMPLATE":
            name = header.split(":")[0].strip()
            spec.templates.append(Template(
                name=name,
                type=_extract_val(body, "type") or "html",
                file=_extract_val(body, "file"),
                vars=_extract_list(body, "vars"),
            ))

        elif keyword == "DOCUMENT":
            name = header.split(":")[0].strip()
            partials = _extract_list(body, "partials")
            if not partials:
                # YAML-style list under partials:
                partials = _extract_yaml_list(body, "partials")
            spec.documents.append(Document(
                name=name,
                type=_extract_val(body, "type") or "pdf",
                template=_extract_val(body, "template"),
                output=_extract_val(body, "path") or _extract_val(body, "output"),
                partials=partials,
            ))

        elif keyword == "REPORT":
            name = header.split(":")[0].strip()
            spec.reports.append(Report(
                name=name,
                schedule=_extract_val(body, "schedule"),
                template=_extract_val(body, "template"),
                output=_extract_val(body, "output") or "pdf",
                retention=_extract_val(body, "retention"),
            ))

        elif keyword == "DATABASE":
            name = header.split(":")[0].strip()
            spec.databases.append(Database(
                name=name,
                type=_extract_val(body, "type") or "sqlite",
                url=_extract_val(body, "url"),
                file=_extract_val(body, "file"),
                read_only=_extract_val(body, "read_only") == "true",
                backup=_extract_val(body, "backup"),
            ))

        elif keyword == "API_CLIENT":
            name = header.split(":")[0].strip()
            retry_s = _extract_val(body, "retry")
            spec.api_clients.append(ApiClient(
                name=name,
                base_url=_extract_val(body, "base_url"),
                auth=_extract_val(body, "auth"),
                token=_extract_val(body, "token"),
                openapi=_extract_val(body, "openapi"),
                retry=int(retry_s) if retry_s and retry_s.isdigit() else 0,
                timeout=_extract_val(body, "timeout"),
            ))

        elif keyword == "WEBHOOK":
            name = header.split(":")[0].strip()
            spec.webhooks.append(Webhook(
                name=name,
                source=_extract_val(body, "source"),
                event=_extract_val(body, "event"),
                auth=_extract_val(body, "auth"),
                secret=_extract_val(body, "secret"),
            ))

        elif keyword == "INTERFACE":
            name = header.split(":")[0].strip()
            itype = _extract_val(body, "type") or name
            pages = _extract_pages(body)
            framework = _extract_val(body, "framework")
            target = _extract_val(body, "target")
            pwa_s = _extract_val(body, "pwa")
            spec.interfaces.append(Interface(
                name=name,
                type=itype,
                pages=pages,
                target=target,
                framework=framework,
                pwa=pwa_s == "true" if pwa_s else False,
            ))

        elif keyword == "INTEGRATION":
            name = header.split(":")[0].strip()
            spec.integrations.append(Integration(name=name))

        elif keyword == "WORKFLOW":
            name = header.split(":")[0].strip()
            trigger = _extract_val(body, "trigger")
            schedule = _extract_val(body, "schedule")
            condition = _extract_val(body, "condition")
            spec.workflows.append(Workflow(
                name=name, trigger=trigger,
                schedule=schedule, condition=condition,
            ))

        elif keyword in ("ROLES", "ROLE"):
            for rm in re.finditer(r'^\s+-\s+(\w+)', body, re.MULTILINE):
                spec.roles.append(Role(name=rm.group(1)))
            # inline role name
            name = header.split(":")[0].strip()
            if name and name not in [r.name for r in spec.roles]:
                spec.roles.append(Role(name=name))

        elif keyword == "SCENARIOS":
            for im in re.finditer(r'IMPORT:\s*(.+)', body):
                spec.scenarios.append(im.group(1).strip())

        elif keyword == "TESTS":
            for im in re.finditer(r'IMPORT:\s*(.+)', body):
                spec.tests.append(im.group(1).strip())

        elif keyword == "DEPLOY":
            target = "docker-compose"
            rootless = False
            target_v = _extract_val(body, "target")
            if target_v:
                target = target_v
            elif "quadlet" in (header + body).lower():
                target = "quadlet"
            elif "kiosk" in (header + body).lower():
                target = "kiosk-appliance"
            elif "docker" in (header + body).lower():
                target = "docker-compose"
            rootless_s = _extract_val(body, "rootless")
            if rootless_s == "true":
                rootless = True
            spec.deploy = Deploy(target=target, rootless=rootless)

    return spec


# ────────────────────────────────────────────────────────
# .env parser
# ────────────────────────────────────────────────────────

def parse_env(path: pathlib.Path) -> dict[str, str]:
    """Parse a .env file into a dict. Missing file → empty dict."""
    if not path.exists():
        return {}

    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


# ────────────────────────────────────────────────────────
# Validator
# ────────────────────────────────────────────────────────

def validate(spec: DoqlSpec, env_vars: dict[str, str], project_root: Optional[pathlib.Path] = None) -> list[ValidationIssue]:
    """Validate a parsed DoqlSpec against env vars and internal consistency."""
    issues: list[ValidationIssue] = []

    # APP name required
    if not spec.app_name or spec.app_name == "Untitled":
        issues.append(ValidationIssue("APP", "APP name is required", "error"))

    # Check env.* references
    for ref in spec.env_refs:
        if ref not in env_vars:
            issues.append(ValidationIssue(
                f"env.{ref}",
                f"Referenced env var '{ref}' not found in .env",
                "warning",
            ))

    # Check DATA source files exist (if project_root given)
    if project_root:
        for ds in spec.data_sources:
            if ds.file and ds.source in ("json", "sqlite", "csv", "excel"):
                fpath = project_root / ds.file
                if not fpath.exists():
                    issues.append(ValidationIssue(
                        f"DATA {ds.name}",
                        f"File not found: {ds.file}",
                        "error",
                    ))

    # Check DOCUMENT templates exist
    if project_root:
        for doc in spec.documents:
            if doc.template:
                tpath = project_root / doc.template
                if not tpath.exists():
                    issues.append(ValidationIssue(
                        f"DOCUMENT {doc.name}",
                        f"Template not found: {doc.template}",
                        "warning",
                    ))

    # Check TEMPLATE files exist
    if project_root:
        for tmpl in spec.templates:
            if tmpl.file:
                tpath = project_root / tmpl.file
                if not tpath.exists():
                    issues.append(ValidationIssue(
                        f"TEMPLATE {tmpl.name}",
                        f"File not found: {tmpl.file}",
                        "warning",
                    ))

    # Cross-reference: DOCUMENT partials must reference known TEMPLATEs
    template_names = {t.name for t in spec.templates}
    for doc in spec.documents:
        for partial in doc.partials:
            if partial not in template_names:
                issues.append(ValidationIssue(
                    f"DOCUMENT {doc.name}",
                    f"Partial '{partial}' not found in TEMPLATEs",
                    "warning",
                ))

    # Cross-reference: ENTITY ref fields must reference known entities
    entity_names = {e.name for e in spec.entities}
    for ent in spec.entities:
        for f in ent.fields:
            if f.ref and f.ref not in entity_names:
                issues.append(ValidationIssue(
                    f"ENTITY {ent.name}.{f.name}",
                    f"References unknown entity '{f.ref}'",
                    "error",
                ))

    # Warn on interfaces with no pages
    for iface in spec.interfaces:
        if not iface.pages and iface.name not in ("api",):
            issues.append(ValidationIssue(
                f"INTERFACE {iface.name}",
                "No pages defined (will generate empty shell)",
                "warning",
            ))

    return issues
