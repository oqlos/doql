"""Block handler registry — dispatch pattern for parsing .doql sections.

This replaces the massive if/elif chain in _apply_block with a clean
registry pattern, reducing cyclomatic complexity from 49 to ~5.
"""
from __future__ import annotations

import re
from typing import Callable, TYPE_CHECKING

from .extractors import extract_val, extract_list, extract_yaml_list, extract_pages, extract_entity_fields

if TYPE_CHECKING:
    from .models import DoqlSpec


# Registry: keyword -> handler function
_block_handlers: dict[str, Callable[[DoqlSpec, str, str], None]] = {}


def register(keyword: str) -> Callable:
    """Decorator to register a block handler for a keyword."""
    def decorator(fn: Callable[[DoqlSpec, str, str], None]) -> Callable:
        _block_handlers[keyword] = fn
        return fn
    return decorator


def get_handler(keyword: str) -> Callable[[DoqlSpec, str, str], None] | None:
    """Get the handler for a keyword, or None if not registered."""
    return _block_handlers.get(keyword)


def list_registered() -> list[str]:
    """Return list of registered keywords."""
    return list(_block_handlers.keys())


# ═══════════════════════════════════════════════════════════
# Block Handlers
# ═══════════════════════════════════════════════════════════

from .models import (
    Entity, DataSource, Template, Document, Report, Database,
    ApiClient, Webhook, Interface, Integration, Workflow, Role, Deploy
)


@register("APP")
def _handle_app(spec: DoqlSpec, header: str, body: str) -> None:
    m = re.match(r':\s*"(.+)"', header)
    spec.app_name = m.group(1) if m else header.strip(': "')


@register("VERSION")
def _handle_version(spec: DoqlSpec, header: str, body: str) -> None:
    spec.version = header.strip(': "\'')


@register("DOMAIN")
def _handle_domain(spec: DoqlSpec, header: str, body: str) -> None:
    spec.domain = header.strip(': "\'')


@register("LANGUAGES")
def _handle_languages(spec: DoqlSpec, header: str, body: str) -> None:
    raw = header.strip(": ")
    spec.languages = [v.strip().strip('"\'') for v in raw.strip("[]").split(",") if v.strip()]


@register("AUTHOR")
def _handle_author(spec: DoqlSpec, header: str, body: str) -> None:
    author = header.strip(': "\'')
    if author and author not in spec.authors:
        spec.authors.append(author)


@register("DEFAULT_LANGUAGE")
def _handle_default_language(spec: DoqlSpec, header: str, body: str) -> None:
    spec.default_language = header.strip(': "\'')


@register("ENTITY")
def _handle_entity(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    fields = extract_entity_fields(body)
    audit = extract_val(body, "AUDIT")
    idx = extract_list(body, "INDEX")
    spec.entities.append(Entity(name=name, fields=fields, audit=audit, indexes=idx))


@register("DATA")
def _handle_data(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    source = extract_val(body, "source") or "json"
    spec.data_sources.append(DataSource(
        name=name,
        source=source,
        file=extract_val(body, "file"),
        url=extract_val(body, "url"),
        schema=extract_val(body, "schema"),
        auth=extract_val(body, "auth"),
        token=extract_val(body, "token"),
        cache=extract_val(body, "cache"),
        read_only=extract_val(body, "read_only") == "true",
        env_overrides=extract_val(body, "env_overrides") == "true",
    ))


@register("TEMPLATE")
def _handle_template(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    spec.templates.append(Template(
        name=name,
        type=extract_val(body, "type") or "html",
        file=extract_val(body, "file"),
        vars=extract_list(body, "vars"),
    ))


@register("DOCUMENT")
def _handle_document(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    partials = extract_list(body, "partials")
    if not partials:
        partials = extract_yaml_list(body, "partials")
    spec.documents.append(Document(
        name=name,
        type=extract_val(body, "type") or "pdf",
        template=extract_val(body, "template"),
        output=extract_val(body, "path") or extract_val(body, "output"),
        partials=partials,
    ))


@register("REPORT")
def _handle_report(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    spec.reports.append(Report(
        name=name,
        schedule=extract_val(body, "schedule"),
        template=extract_val(body, "template"),
        output=extract_val(body, "output") or "pdf",
        retention=extract_val(body, "retention"),
    ))


@register("DATABASE")
def _handle_database(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    spec.databases.append(Database(
        name=name,
        type=extract_val(body, "type") or "sqlite",
        url=extract_val(body, "url"),
        file=extract_val(body, "file"),
        read_only=extract_val(body, "read_only") == "true",
        backup=extract_val(body, "backup"),
    ))


@register("API_CLIENT")
def _handle_api_client(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    retry_s = extract_val(body, "retry")
    spec.api_clients.append(ApiClient(
        name=name,
        base_url=extract_val(body, "base_url"),
        auth=extract_val(body, "auth"),
        token=extract_val(body, "token"),
        openapi=extract_val(body, "openapi"),
        retry=int(retry_s) if retry_s and retry_s.isdigit() else 0,
        timeout=extract_val(body, "timeout"),
    ))


@register("WEBHOOK")
def _handle_webhook(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    spec.webhooks.append(Webhook(
        name=name,
        source=extract_val(body, "source"),
        event=extract_val(body, "event"),
        auth=extract_val(body, "auth"),
        secret=extract_val(body, "secret"),
    ))


@register("INTERFACE")
def _handle_interface(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    itype = extract_val(body, "type") or name
    pages = extract_pages(body)
    framework = extract_val(body, "framework")
    target = extract_val(body, "target")
    pwa_s = extract_val(body, "pwa")
    spec.interfaces.append(Interface(
        name=name,
        type=itype,
        pages=pages,
        target=target,
        framework=framework,
        pwa=pwa_s == "true" if pwa_s else False,
    ))


@register("INTEGRATION")
def _handle_integration(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    spec.integrations.append(Integration(name=name))


@register("WORKFLOW")
def _handle_workflow(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    trigger = extract_val(body, "trigger")
    schedule = extract_val(body, "schedule")
    condition = extract_val(body, "condition")
    spec.workflows.append(Workflow(
        name=name, trigger=trigger,
        schedule=schedule, condition=condition,
    ))


@register("ROLES")
def _handle_roles(spec: DoqlSpec, header: str, body: str) -> None:
    # Match role declarations at one level of indent: "  <name>:"
    seen = {r.name for r in spec.roles}
    for rm in re.finditer(r'^(?:  |\t)(\w+):\s*$', body, re.MULTILINE):
        name = rm.group(1)
        # Skip role-definition keywords (not real role names)
        if name in {"can", "cannot", "extends", "scope", "permissions", "can_read_only"}:
            continue
        if name not in seen:
            spec.roles.append(Role(name=name))
            seen.add(name)


@register("ROLE")
def _handle_role(spec: DoqlSpec, header: str, body: str) -> None:
    name = header.split(":")[0].strip()
    seen = {r.name for r in spec.roles}
    if name and name not in seen:
        spec.roles.append(Role(name=name))


def _handle_import_block(spec: DoqlSpec, body: str, target_attr: str) -> None:
    """Parse IMPORT statements from block body and append to target list."""
    target_list = getattr(spec, target_attr)
    for im in re.finditer(r'IMPORT:\s*(.+)', body):
        target_list.append(im.group(1).strip())


@register("SCENARIOS")
def _handle_scenarios(spec: DoqlSpec, header: str, body: str) -> None:
    _handle_import_block(spec, body, "scenarios")


@register("TESTS")
def _handle_tests(spec: DoqlSpec, header: str, body: str) -> None:
    _handle_import_block(spec, body, "tests")


@register("DEPLOY")
def _handle_deploy(spec: DoqlSpec, header: str, body: str) -> None:
    target = "docker-compose"
    rootless = False
    target_v = extract_val(body, "target")
    if target_v:
        target = target_v
    elif "quadlet" in (header + body).lower():
        target = "quadlet"
    elif "kiosk" in (header + body).lower():
        target = "kiosk-appliance"
    elif "docker" in (header + body).lower():
        target = "docker-compose"
    rootless_s = extract_val(body, "rootless")
    if rootless_s == "true":
        rootless = True
    spec.deploy = Deploy(target=target, rootless=rootless)


@register("INFRASTRUCTURE")
def _handle_infrastructure(spec: DoqlSpec, header: str, body: str) -> None:
    from .models import Infrastructure
    name = header.split(":")[0].strip() if ":" in header else ""
    infra = Infrastructure(
        name=name,
        type=extract_val(body, "type") or "docker-compose",
        provider=extract_val(body, "provider"),
        namespace=extract_val(body, "namespace"),
    )
    replicas = extract_val(body, "replicas")
    if replicas and replicas.isdigit():
        infra.replicas = int(replicas)
    spec.infrastructures.append(infra)


@register("INGRESS")
def _handle_ingress(spec: DoqlSpec, header: str, body: str) -> None:
    from .models import Ingress
    name = header.split(":")[0].strip() if ":" in header else ""
    ingress = Ingress(
        name=name,
        type=extract_val(body, "type") or "traefik",
        tls=extract_val(body, "tls") == "true",
        cert_manager=extract_val(body, "cert_manager"),
        rate_limit=extract_val(body, "rate_limit"),
    )
    spec.ingresses.append(ingress)


@register("CI")
def _handle_ci(spec: DoqlSpec, header: str, body: str) -> None:
    from .models import CiConfig
    name = header.split(":")[0].strip() if ":" in header else ""
    ci = CiConfig(
        name=name,
        type=extract_val(body, "type") or "github",
        runner=extract_val(body, "runner"),
        stages=extract_list(body, "stages"),
    )
    spec.ci_configs.append(ci)


@register("PROJECT")
def _handle_project(spec: DoqlSpec, header: str, body: str) -> None:
    from .models import Subproject, DoqlSpec
    name = header.split(":")[0].strip() if ":" in header else ""
    path = extract_val(body, "path") or ""
    sub = Subproject(name=name, spec=DoqlSpec(), path=path)
    spec.subprojects.append(sub)
