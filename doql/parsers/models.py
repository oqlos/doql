"""Data models for .doql specification — SPEC v0.2.

All section types: APP, VERSION, DATA, ENTITY, TEMPLATE, DOCUMENT,
REPORT, DATABASE, API_CLIENT, WEBHOOK, INTERFACE, WORKFLOW, ROLES,
SCENARIOS, TESTS, DEPLOY, INTEGRATION.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


class DoqlParseError(Exception):
    """Raised when a .doql file cannot be parsed."""


@dataclass
class ValidationIssue:
    path: str
    message: str
    severity: str = "error"  # "error" | "warning"
    line: int = 0   # 0-indexed, 0 = unknown
    column: int = 0


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
    directives: dict[str, str] = field(default_factory=dict)


@dataclass
class Environment:
    name: str
    runtime: str = "docker-compose"
    ssh_host: Optional[str] = None
    env_file: Optional[str] = None
    replicas: int = 1
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Infrastructure:
    name: str
    type: str = "docker-compose"
    provider: Optional[str] = None
    namespace: Optional[str] = None
    replicas: int = 1
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Ingress:
    name: str
    type: str = "traefik"
    tls: bool = False
    cert_manager: Optional[str] = None
    rate_limit: Optional[str] = None
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class CiConfig:
    name: str
    type: str = "github"
    runner: Optional[str] = None
    stages: list[str] = field(default_factory=list)
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Subproject:
    """A named sub-project inside a monorepo DOQL manifest."""
    name: str
    spec: Optional["DoqlSpec"] = None
    path: str = ""  # relative path from root manifest


@dataclass
class DoqlSpec:
    app_name: str = "Untitled"
    version: str = "0.1.0"
    description: Optional[str] = None
    license: Optional[str] = None
    authors: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    homepage: Optional[str] = None
    repository: Optional[str] = None
    python_requires: Optional[str] = None
    dependencies: dict[str, str] = field(default_factory=dict)
    domain: Optional[str] = None
    languages: list[str] = field(default_factory=list)
    default_language: Optional[str] = None
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
    environments: list[Environment] = field(default_factory=list)
    infrastructures: list[Infrastructure] = field(default_factory=list)
    ingresses: list[Ingress] = field(default_factory=list)
    ci_configs: list[CiConfig] = field(default_factory=list)
    env_refs: list[str] = field(default_factory=list)
    parse_errors: list[ValidationIssue] = field(default_factory=list)
    subprojects: list[Subproject] = field(default_factory=list)
