"""Plan command — dry-run showing what would be generated."""
from __future__ import annotations

import argparse
import pathlib
from typing import TYPE_CHECKING

from ... import parsers as doql_parser
from ..context import estimate_file_count

if TYPE_CHECKING:
    from ...parsers.models import DoqlSpec


def _print_header(spec: DoqlSpec) -> None:
    """Print plan header with app name and version."""
    print(f"📋 Plan for {spec.app_name} (v{spec.version}):\n")
    print(f"  Domain:         {spec.domain or '(not set)'}")
    print(f"  Languages:      {spec.languages or ['(default)']}")


def _print_entities(spec: DoqlSpec) -> None:
    """Print entities section."""
    print(f"  Entities:       {len(spec.entities)}")
    for e in spec.entities:
        print(f"    • {e.name} ({len(e.fields)} fields)")


def _print_data_sources(spec: DoqlSpec) -> None:
    """Print DATA sources section."""
    print(f"  DATA sources:   {len(spec.data_sources)}")
    for d in spec.data_sources:
        file_info = f" → {d.file}" if d.file else ""
        print(f"    • {d.name} ({d.source}{file_info})")


def _print_documents(spec: DoqlSpec) -> None:
    """Print documents and templates section."""
    print(f"  Templates:      {len(spec.templates)}")
    print(f"  Documents:      {len(spec.documents)}")
    for d in spec.documents:
        print(f"    • {d.name} ({d.type})")


def _print_api_clients(spec: DoqlSpec) -> None:
    """Print API clients section."""
    print(f"  API clients:    {len(spec.api_clients)}")
    for a in spec.api_clients:
        print(f"    • {a.name} ({a.base_url or ' ?'})")


def _print_interfaces(spec: DoqlSpec) -> None:
    """Print interfaces section."""
    print(f"  Interfaces:     {[i.name for i in spec.interfaces]}")
    for i in spec.interfaces:
        pages = [p.name for p in i.pages]
        print(f"    • {i.name} ({i.type}) pages={pages}")


def _print_workflows(spec: DoqlSpec) -> None:
    """Print workflows section."""
    print(f"  Workflows:      {len(spec.workflows)}")
    for w in spec.workflows:
        trigger = w.trigger or w.schedule or '?'
        print(f"    • {w.name} (trigger={trigger})")


def _print_summary(spec: DoqlSpec) -> None:
    """Print summary statistics."""
    print(f"  Reports:        {len(spec.reports)}")
    print(f"  Databases:      {len(spec.databases)}")
    print(f"  Webhooks:       {len(spec.webhooks)}")
    print(f"  Scenarios:      {len(spec.scenarios)}")
    print(f"  Integrations:   {[ig.name for ig in spec.integrations]}")
    print(f"  Roles:          {[r.name for r in spec.roles]}")
    print(f"  Deploy target:  {spec.deploy.target if spec.deploy else '(none)'}")
    print(f"  Env references: {len(spec.env_refs)} vars")


def _print_file_counts(spec: DoqlSpec) -> None:
    """Print estimated file generation counts."""
    print("\n  Files to generate:")
    total = 0
    for iface in spec.interfaces:
        count = estimate_file_count(iface)
        total += count
        print(f"    {iface.name:12} ~{count} files")

    infra_count = len(spec.integrations) + 3
    print(f"    infra        ~{infra_count} files")
    print(f"  TOTAL:          ~{total + infra_count} files\n")


def cmd_plan(args: argparse.Namespace) -> int:
    """Show dry-run plan of what would be generated.

    Displays project overview including entities, data sources, interfaces,
    and estimated file counts per interface type.
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    doql_file = root / (getattr(args, "file", None) or "app.doql")

    spec = doql_parser.parse_file(doql_file)

    _print_header(spec)
    _print_entities(spec)
    _print_data_sources(spec)
    _print_documents(spec)
    _print_api_clients(spec)
    _print_summary(spec)
    _print_interfaces(spec)
    _print_workflows(spec)
    _print_file_counts(spec)

    return 0
