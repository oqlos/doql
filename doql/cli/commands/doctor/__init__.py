"""Doctor command — comprehensive project health check.

Checks parse validity, file references, environment variables,
database connectivity, deploy readiness, and optional remote diagnostics.
"""
from __future__ import annotations

import argparse
import pathlib

from ....parsers import detect_doql_file
from ....parsers.models import DoqlSpec
from .report import DoctorReport, _print_report
from .checks import (
    _check_parse,
    _check_env,
    _check_files,
    _check_databases,
    _check_interfaces,
    _check_tools,
    _check_deploy,
    _check_environments,
)
from .remote import _check_remote
from .fixes import _apply_fixes

__all__ = ["cmd_doctor"]


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
    _check_deploy(spec, report, root)

    # 8. Environments
    _check_environments(spec, report)

    # 9. Remote diagnostics (optional --env flag)
    if env_name:
        _check_remote(spec, env_name, report)

    _print_report(report)

    # 10. Auto-fixes (optional --fix flag)
    if getattr(args, "fix", False):
        _apply_fixes(report, root, spec)

    return 1 if report.failures else 0
