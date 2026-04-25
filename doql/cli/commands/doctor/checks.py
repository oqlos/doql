"""Individual health checks for the doctor command."""
from __future__ import annotations

import os
import pathlib
import shutil

from .... import parser as doql_parser
from ....parsers.models import DoqlSpec
from .report import DoctorReport


def _check_parse(root: pathlib.Path, doql_file: pathlib.Path, report: DoctorReport) -> DoqlSpec | None:
    """Parse the .doql file and report errors."""
    try:
        spec = doql_parser.parse_file(doql_file)
    except Exception as exc:
        report.add("parse", "fail", f"Cannot parse {doql_file.name}: {exc}")
        return None

    if spec.parse_errors:
        for err in spec.parse_errors:
            report.add("parse", "fail", f"{err.path}: {err.message}")
        return spec

    report.add("parse", "ok", f"{doql_file.name} parsed ({len(spec.entities)} entities)")
    return spec


def _find_missing_env_refs(spec, env_vars: dict) -> list[str]:
    """Return list of env var names referenced in spec but not resolved."""
    missing = []
    for ref in spec.env_refs:
        if ref in env_vars:
            continue
        if ref.endswith("_") and any(k.startswith(ref) for k in env_vars):
            continue
        if ref in os.environ:
            continue
        missing.append(ref)
    return missing


def _check_env(root: pathlib.Path, spec: DoqlSpec, report: DoctorReport) -> dict[str, str]:
    """Check .env file presence and variable coverage."""
    env_file = root / ".env"
    env_vars: dict[str, str] = {}
    if env_file.exists():
        env_vars = doql_parser.parse_env(env_file)
        report.add("env-file", "ok", f".env loaded ({len(env_vars)} vars)")
    elif spec.env_refs:
        report.add("env-file", "warn", ".env missing but spec references env vars")
    else:
        report.add("env-file", "ok", "No .env required")

    missing = _find_missing_env_refs(spec, env_vars)
    if missing:
        report.add("env-vars", "warn", f"Missing env vars: {', '.join(missing)}")
    elif spec.env_refs:
        report.add("env-vars", "ok", f"All {len(spec.env_refs)} env refs resolved")

    return env_vars


def _collect_missing_files(root: pathlib.Path, spec: DoqlSpec) -> list[str]:
    """Return list of missing file descriptions from spec references."""
    missing: list[str] = []
    for ds in spec.data_sources:
        if ds.file and not pathlib.PurePosixPath(ds.file).is_absolute() and not (root / ds.file).exists():
            missing.append(f"DATA {ds.name}: {ds.file}")
    for tmpl in spec.templates:
        if tmpl.file and not (root / tmpl.file).exists():
            missing.append(f"TEMPLATE {tmpl.name}: {tmpl.file}")
    for doc in spec.documents:
        if doc.template and not (root / doc.template).exists():
            missing.append(f"DOCUMENT {doc.name}: {doc.template}")
    return missing


def _check_files(root: pathlib.Path, spec: DoqlSpec, report: DoctorReport) -> None:
    """Check that referenced files exist."""
    missing = _collect_missing_files(root, spec)
    if missing:
        for m in missing:
            report.add("files", "fail", f"Not found: {m}")
    else:
        report.add("files", "ok", "All referenced files exist")


def _check_databases(spec: DoqlSpec, report: DoctorReport) -> None:
    """Check database configuration."""
    if not spec.databases:
        report.add("databases", "skip", "No databases defined")
        return
    for db in spec.databases:
        if db.type == "sqlite":
            report.add(f"db:{db.name}", "ok", "SQLite (file-based, no connectivity check)")
        elif db.url:
            report.add(f"db:{db.name}", "ok", f"{db.type} url configured")
        else:
            report.add(f"db:{db.name}", "warn", f"{db.type} has no url configured")


def _warn_unknown_entity_refs(iface, entity_names: set, report: DoctorReport) -> None:
    """Warn if interface references entities that don't exist in the spec."""
    for ename in iface.entities:
        if ename not in entity_names:
            report.add(f"interface:{iface.name}", "warn",
                       f"References unknown entity '{ename}'")


def _check_interfaces(spec: DoqlSpec, report: DoctorReport) -> None:
    """Check interface consistency."""
    if not spec.interfaces:
        report.add("interfaces", "skip", "No interfaces defined")
        return
    entity_names = {e.name for e in spec.entities}
    for iface in spec.interfaces:
        _warn_unknown_entity_refs(iface, entity_names, report)
        if iface.name != "api" and not iface.pages:
            report.add(f"interface:{iface.name}", "warn", "No pages defined")

    ok_count = sum(1 for i in spec.interfaces
                   if not (i.name != "api" and not i.pages))
    if ok_count:
        report.add("interfaces", "ok", f"{len(spec.interfaces)} interface(s) configured")


def _collect_required_tools(spec) -> list[tuple[str, str]]:
    """Return list of (binary, reason) pairs for tools required by this spec."""
    tools: list[tuple[str, str]] = []
    # Support both canonical names (v1.0+) and legacy aliases
    if spec.deploy.target in ("docker_full", "docker-compose", "compose"):
        tools.append(("docker", "deploy target is docker_full"))
    if spec.deploy.target in ("podman_quadlet", "quadlet", "podman"):
        tools.append(("podman", "deploy target uses podman_quadlet"))
    for iface in spec.interfaces:
        if iface.name == "web":
            tools.append(("node", "web interface needs Node.js"))
            tools.append(("npm", "web interface needs npm"))
        if iface.name == "desktop" and iface.type == "tauri":
            tools.append(("cargo", "Tauri desktop needs Rust"))
        if iface.name == "api":
            tools.append(("python3", "API backend needs Python"))
    return tools


def _check_tools(spec: DoqlSpec, report: DoctorReport) -> None:
    """Check required tools are available on PATH."""
    checked: set[str] = set()
    for binary, reason in _collect_required_tools(spec):
        if binary in checked:
            continue
        checked.add(binary)
        if shutil.which(binary):
            report.add(f"tool:{binary}", "ok", f"{binary} found")
        else:
            report.add(f"tool:{binary}", "warn", f"{binary} not found ({reason})")


def _check_deploy(spec: DoqlSpec, report: DoctorReport, root: pathlib.Path) -> None:
    """Check deploy configuration and redeploy integration."""
    if not spec.deploy.target:
        report.add("deploy", "skip", "No deploy target configured")
        return
    report.add("deploy", "ok", f"Deploy target: {spec.deploy.target}")

    # Check redeploy integration (v1.0+)
    has_redeploy = shutil.which("redeploy") is not None
    try:
        import redeploy  # noqa: F401
        has_redeploy_api = True
    except ImportError:
        has_redeploy_api = False

    if has_redeploy_api:
        report.add("redeploy", "ok", "redeploy Python API available (doql[deploy] installed)")
    elif has_redeploy:
        report.add("redeploy", "ok", "redeploy CLI available on PATH")
    else:
        report.add("redeploy", "warn", "redeploy not found — install: pip install doql[deploy]")

    # Check migration.yaml was generated
    migration_yaml = root / "build" / "infra" / "migration.yaml"
    if migration_yaml.exists():
        report.add("migration.yaml", "ok", f"Found {migration_yaml}")
    else:
        report.add("migration.yaml", "warn", "Run 'doql build' to generate migration.yaml")


def _check_environments(spec: DoqlSpec, report: DoctorReport) -> None:
    """Check environment definitions."""
    if not spec.environments:
        report.add("environments", "skip", "No environments defined")
        return
    for env in spec.environments:
        parts = [env.runtime]
        if env.ssh_host:
            parts.append(f"ssh={env.ssh_host}")
        if env.replicas > 1:
            parts.append(f"replicas={env.replicas}")
        report.add(f"env:{env.name}", "ok", ", ".join(parts))
