"""Import YAML → DoqlSpec."""
from __future__ import annotations

import pathlib
from typing import Any

import yaml

from ..parsers.models import (
    DoqlSpec, Entity, EntityField, DataSource, Template, Document,
    Report, Database, ApiClient, Webhook, Interface, Page,
    Integration, Workflow, WorkflowStep, Role, Deploy,
)


def _get(d: dict, key: str, default=None):
    return d.get(key, default)


def _build_entity_field(data: dict) -> EntityField:
    return EntityField(
        name=data["name"],
        type=data.get("type", "string"),
        required=data.get("required", False),
        unique=data.get("unique", False),
        computed=data.get("computed", False),
        ref=data.get("ref"),
        default=data.get("default"),
        auto=data.get("auto", False),
    )


def _build_entity(data: dict) -> Entity:
    fields = [_build_entity_field(f) for f in data.get("fields", [])]
    return Entity(
        name=data["name"],
        fields=fields,
        audit=data.get("audit"),
        indexes=data.get("indexes", []),
    )


def _build_data_source(data: dict) -> DataSource:
    return DataSource(
        name=data["name"],
        source=data.get("source", "json"),
        file=data.get("file"),
        url=data.get("url"),
        schema=data.get("schema"),
        auth=data.get("auth"),
        token=data.get("token"),
        cache=data.get("cache"),
        read_only=data.get("read_only", False),
        env_overrides=data.get("env_overrides", False),
    )


def _build_template(data: dict) -> Template:
    return Template(
        name=data["name"],
        type=data.get("type", "html"),
        file=data.get("file"),
        content=data.get("content"),
        vars=data.get("vars", []),
        engine=data.get("engine", "jinja2"),
    )


def _build_document(data: dict) -> Document:
    return Document(
        name=data["name"],
        type=data.get("type", "pdf"),
        template=data.get("template"),
        data=data.get("data", {}),
        output=data.get("output"),
        styling=data.get("styling", {}),
        metadata=data.get("metadata", {}),
        signature=data.get("signature", {}),
        hooks=data.get("hooks", {}),
        partials=data.get("partials", []),
    )


def _build_report(data: dict) -> Report:
    return Report(
        name=data["name"],
        schedule=data.get("schedule"),
        template=data.get("template"),
        output=data.get("output", "pdf"),
        query=data.get("query", {}),
        recipients=data.get("recipients", {}),
        retention=data.get("retention"),
    )


def _build_database(data: dict) -> Database:
    return Database(
        name=data["name"],
        type=data.get("type", "sqlite"),
        url=data.get("url"),
        file=data.get("file"),
        read_only=data.get("read_only", False),
        backup=data.get("backup"),
    )


def _build_api_client(data: dict) -> ApiClient:
    return ApiClient(
        name=data["name"],
        base_url=data.get("base_url"),
        auth=data.get("auth"),
        token=data.get("token"),
        openapi=data.get("openapi"),
        retry=data.get("retry", 0),
        timeout=data.get("timeout"),
        methods=data.get("methods", []),
    )


def _build_webhook(data: dict) -> Webhook:
    return Webhook(
        name=data["name"],
        source=data.get("source"),
        event=data.get("event"),
        auth=data.get("auth"),
        secret=data.get("secret"),
    )


def _build_page(data: dict) -> Page:
    return Page(
        name=data["name"],
        layout=data.get("layout"),
        features=data.get("features", []),
        path=data.get("path"),
        public=data.get("public", False),
    )


def _build_interface(data: dict) -> Interface:
    pages = [_build_page(p) for p in data.get("pages", [])]
    return Interface(
        name=data["name"],
        type=data.get("type", "spa"),
        pages=pages,
        entities=data.get("entities", []),
        target=data.get("target"),
        auth=data.get("auth", {}),
        hardware=data.get("hardware", {}),
        framework=data.get("framework"),
        pwa=data.get("pwa", False),
    )


def _build_integration(data: dict) -> Integration:
    return Integration(
        name=data["name"],
        type=data.get("type", "email"),
        config=data.get("config", {}),
    )


def _build_workflow_step(data: dict) -> WorkflowStep:
    return WorkflowStep(
        action=data["action"],
        target=data.get("target"),
        params=data.get("params", {}),
    )


def _build_workflow(data: dict) -> Workflow:
    steps = [_build_workflow_step(s) for s in data.get("steps", [])]
    return Workflow(
        name=data["name"],
        trigger=data.get("trigger"),
        schedule=data.get("schedule"),
        condition=data.get("condition"),
        steps=steps,
    )


def _build_role(data: dict) -> Role:
    return Role(
        name=data["name"],
        permissions=data.get("permissions", []),
    )


def _build_deploy(data: dict) -> Deploy:
    return Deploy(
        target=data.get("target", "docker-compose"),
        rootless=data.get("rootless", False),
        containers=data.get("containers", []),
        config=data.get("config", {}),
    )


def import_yaml(data: dict[str, Any]) -> DoqlSpec:
    """Build a DoqlSpec from a YAML-style dictionary."""
    spec = DoqlSpec()
    spec.app_name = data.get("app_name", "Untitled")
    spec.version = data.get("version", "0.1.0")
    spec.domain = data.get("domain")
    spec.languages = data.get("languages", [])

    for item in data.get("entities", []):
        spec.entities.append(_build_entity(item))
    for item in data.get("data_sources", []):
        spec.data_sources.append(_build_data_source(item))
    for item in data.get("templates", []):
        spec.templates.append(_build_template(item))
    for item in data.get("documents", []):
        spec.documents.append(_build_document(item))
    for item in data.get("reports", []):
        spec.reports.append(_build_report(item))
    for item in data.get("databases", []):
        spec.databases.append(_build_database(item))
    for item in data.get("api_clients", []):
        spec.api_clients.append(_build_api_client(item))
    for item in data.get("webhooks", []):
        spec.webhooks.append(_build_webhook(item))
    for item in data.get("interfaces", []):
        spec.interfaces.append(_build_interface(item))
    for item in data.get("integrations", []):
        spec.integrations.append(_build_integration(item))
    for item in data.get("workflows", []):
        spec.workflows.append(_build_workflow(item))
    for item in data.get("roles", []):
        spec.roles.append(_build_role(item))
    if "deploy" in data and data["deploy"]:
        spec.deploy = _build_deploy(data["deploy"])
    spec.env_refs = data.get("env_refs", [])

    return spec


def import_yaml_text(text: str) -> DoqlSpec:
    """Parse YAML text and return a DoqlSpec."""
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("YAML root must be a mapping")
    return import_yaml(data)


def import_yaml_file(path: pathlib.Path) -> DoqlSpec:
    """Read a YAML file and return a DoqlSpec."""
    text = path.read_text(encoding="utf-8")
    return import_yaml_text(text)
