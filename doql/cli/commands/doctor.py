"""Doctor command — comprehensive project health check.

Checks parse validity, file references, environment variables,
database connectivity, deploy readiness, and optional remote diagnostics.
"""
from __future__ import annotations

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

from ... import parser as doql_parser
from ...parsers import detect_doql_file
from ...parsers.models import DoqlSpec


@dataclass
class Check:
    name: str
    status: str = "ok"          # ok | warn | fail | skip
    message: str = ""


@dataclass
class DoctorReport:
    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, status: str, message: str = "") -> None:
        self.checks.append(Check(name, status, message))

    @property
    def ok(self) -> int:
        return sum(1 for c in self.checks if c.status == "ok")

    @property
    def warnings(self) -> int:
        return sum(1 for c in self.checks if c.status == "warn")

    @property
    def failures(self) -> int:
        return sum(1 for c in self.checks if c.status == "fail")


ICONS = {"ok": "✅", "warn": "⚠️ ", "fail": "❌", "skip": "⏭️ "}


# ── individual checks ──────────────────────────────────────────

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

    missing = []
    for ref in spec.env_refs:
        if ref in env_vars:
            continue
        if ref.endswith("_") and any(k.startswith(ref) for k in env_vars):
            continue
        if ref in os.environ:
            continue
        missing.append(ref)

    if missing:
        report.add("env-vars", "warn", f"Missing env vars: {', '.join(missing)}")
    elif spec.env_refs:
        report.add("env-vars", "ok", f"All {len(spec.env_refs)} env refs resolved")

    return env_vars


def _check_files(root: pathlib.Path, spec: DoqlSpec, report: DoctorReport) -> None:
    """Check that referenced files exist."""
    missing: list[str] = []

    for ds in spec.data_sources:
        if ds.file and not pathlib.PurePosixPath(ds.file).is_absolute():
            if not (root / ds.file).exists():
                missing.append(f"DATA {ds.name}: {ds.file}")

    for tmpl in spec.templates:
        if tmpl.file and not (root / tmpl.file).exists():
            missing.append(f"TEMPLATE {tmpl.name}: {tmpl.file}")

    for doc in spec.documents:
        if doc.template and not (root / doc.template).exists():
            missing.append(f"DOCUMENT {doc.name}: {doc.template}")

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


def _check_interfaces(spec: DoqlSpec, report: DoctorReport) -> None:
    """Check interface consistency."""
    if not spec.interfaces:
        report.add("interfaces", "skip", "No interfaces defined")
        return
    entity_names = {e.name for e in spec.entities}
    for iface in spec.interfaces:
        for ename in iface.entities:
            if ename not in entity_names:
                report.add(f"interface:{iface.name}", "warn",
                           f"References unknown entity '{ename}'")
        if iface.name != "api" and not iface.pages:
            report.add(f"interface:{iface.name}", "warn", "No pages defined")

    ok_count = sum(1 for i in spec.interfaces
                   if not (i.name != "api" and not i.pages))
    if ok_count:
        report.add("interfaces", "ok", f"{len(spec.interfaces)} interface(s) configured")


def _check_tools(spec: DoqlSpec, report: DoctorReport) -> None:
    """Check required tools are available on PATH."""
    tools: list[tuple[str, str]] = []  # (binary, reason)

    if spec.deploy.target in ("docker-compose", "compose"):
        tools.append(("docker", "deploy target is docker-compose"))
    if spec.deploy.target in ("quadlet", "podman"):
        tools.append(("podman", "deploy target uses podman"))

    for iface in spec.interfaces:
        if iface.name == "web":
            tools.append(("node", "web interface needs Node.js"))
            tools.append(("npm", "web interface needs npm"))
        if iface.name == "desktop" and iface.type == "tauri":
            tools.append(("cargo", "Tauri desktop needs Rust"))
        if iface.name == "api":
            tools.append(("python3", "API backend needs Python"))

    checked: set[str] = set()
    for binary, reason in tools:
        if binary in checked:
            continue
        checked.add(binary)
        if shutil.which(binary):
            report.add(f"tool:{binary}", "ok", f"{binary} found")
        else:
            report.add(f"tool:{binary}", "warn", f"{binary} not found ({reason})")


def _check_deploy(spec: DoqlSpec, report: DoctorReport) -> None:
    """Check deploy configuration."""
    if not spec.deploy.target:
        report.add("deploy", "skip", "No deploy target configured")
        return
    report.add("deploy", "ok", f"Deploy target: {spec.deploy.target}")


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


def _check_remote(spec: DoqlSpec, env_name: str, report: DoctorReport) -> None:
    """Run remote diagnostics via SSH for a specific environment."""
    env = next((e for e in spec.environments if e.name == env_name), None)
    if not env:
        report.add("remote", "fail", f"Environment '{env_name}' not found")
        return
    if not env.ssh_host:
        report.add("remote", "skip", f"No ssh_host for '{env_name}'")
        return

    # SSH connectivity
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
             env.ssh_host, "echo ok"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            report.add("remote:ssh", "ok", f"SSH to {env.ssh_host} reachable")
        else:
            report.add("remote:ssh", "fail",
                        f"SSH to {env.ssh_host} failed: {result.stderr.strip()}")
            return  # no point checking further
    except (subprocess.TimeoutExpired, FileNotFoundError):
        report.add("remote:ssh", "fail", f"SSH to {env.ssh_host} timed out / ssh not found")
        return

    # Check remote runtime
    runtime = env.runtime
    check_cmd = "podman --version" if runtime in ("quadlet", "podman") else "docker --version"
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", env.ssh_host, check_cmd],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            report.add("remote:runtime", "ok", result.stdout.strip())
        else:
            report.add("remote:runtime", "warn", f"{check_cmd} not available on remote")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        report.add("remote:runtime", "warn", "Could not check remote runtime")

    # Disk space
    try:
        result = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=5", env.ssh_host,
             "df -h / | tail -1 | awk '{print $4}'"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            report.add("remote:disk", "ok", f"Free space: {result.stdout.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


# ── main entry point ───────────────────────────────────────────

def cmd_doctor(args: argparse.Namespace) -> int:
    """Run comprehensive project health check."""
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    explicit = getattr(args, "file", None)
    doql_file = root / explicit if explicit else detect_doql_file(root)
    env_name = getattr(args, "env", None)

    print(f"🩺 doql doctor — {root.name}\n")

    report = DoctorReport()

    # 1. Parse
    spec = _check_parse(root, doql_file, report)
    if spec is None:
        _print_report(report)
        return 1

    # 2. Environment variables
    _check_env(root, spec, report)

    # 3. Referenced files
    _check_files(root, spec, report)

    # 4. Databases
    _check_databases(spec, report)

    # 5. Interfaces
    _check_interfaces(spec, report)

    # 6. Required tools
    _check_tools(spec, report)

    # 7. Deploy config
    _check_deploy(spec, report)

    # 8. Environments
    _check_environments(spec, report)

    # 9. Remote diagnostics (optional —env flag)
    if env_name:
        _check_remote(spec, env_name, report)

    _print_report(report)
    return 1 if report.failures else 0


def _print_report(report: DoctorReport) -> None:
    """Print the doctor report."""
    for c in report.checks:
        icon = ICONS.get(c.status, "?")
        msg = f"  {icon} {c.name}"
        if c.message:
            msg += f" — {c.message}"
        print(msg)

    print(f"\n  {report.ok} ok, {report.warnings} warning(s), {report.failures} failure(s)")
