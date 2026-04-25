"""Drift report rendering (rich and plain-text)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from opstree.drift.detector import DriftReport


def _change_style(change_type: str) -> str:
    return {
        "added": "green",
        "removed": "red",
        "modified": "yellow",
    }.get(change_type, "white")


def _render_rich(report: "DriftReport", intended_file: Path, target: str) -> None:
    """Pretty-print a drift report with rich. Falls back silently if rich
    is unavailable (we pulled it in as a hard dep, but be robust)."""
    try:
        from rich.console import Console
        from rich.table import Table
        from rich import box
    except ImportError:  # pragma: no cover
        _render_plain(report, intended_file, target)
        return

    console = Console()
    console.print(
        f"[bold]drift[/bold]  intended=[cyan]{intended_file}[/cyan]  "
        f"actual=[cyan]{target}[/cyan]"
    )

    if not report.has_drift:
        console.print("[green]✅ No drift detected[/green]")
        return

    summary = report.summary
    total = summary.get("total_changes", len(report.changes))
    by_type = summary.get("by_type", {})
    by_layer = summary.get("by_layer", {})

    summary_bits = ", ".join(
        f"[{_change_style(k)}]{k}={v}[/{_change_style(k)}]"
        for k, v in sorted(by_type.items())
    )
    console.print(f"[yellow]⚠ {total} changes[/yellow]  ({summary_bits})")

    table = Table(show_header=True, box=box.SIMPLE, padding=(0, 1))
    table.add_column("Layer", style="dim")
    table.add_column("Type", width=10)
    table.add_column("Path")
    table.add_column("Intended", style="cyan")
    table.add_column("Actual", style="magenta")

    for change in report.changes:
        style = _change_style(change.type)
        table.add_row(
            change.layer_id,
            f"[{style}]{change.type}[/{style}]",
            change.path,
            _fmt_value(change.old_value),
            _fmt_value(change.new_value),
        )
    console.print(table)

    if by_layer:
        per_layer = ", ".join(f"{lid}={n}" for lid, n in sorted(by_layer.items()))
        console.print(f"[dim]per-layer: {per_layer}[/dim]")


def _render_plain(report: "DriftReport", intended_file: Path, target: str) -> None:
    """Plain-text renderer — used when rich isn't available or stdout is
    being piped."""
    print(f"drift  intended={intended_file}  actual={target}")
    if not report.has_drift:
        print("OK: no drift detected")
        return

    print(f"DRIFT: {len(report.changes)} change(s)")
    for change in report.changes:
        print(
            f"  [{change.type}] {change.layer_id}:{change.path}  "
            f"{_fmt_value(change.old_value)} -> {_fmt_value(change.new_value)}"
        )


def _fmt_value(value: object) -> str:
    """Compact value formatter: shortens long structures so tables stay
    readable. Full data is always available via ``--json``."""
    if value is None:
        return "—"
    if isinstance(value, (dict, list)):
        try:
            rendered = json.dumps(value, default=str, sort_keys=True)
        except TypeError:
            rendered = repr(value)
        if len(rendered) > 60:
            return rendered[:57] + "..."
        return rendered
    text = str(value)
    if len(text) > 60:
        return text[:57] + "..."
    return text
