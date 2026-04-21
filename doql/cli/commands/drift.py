"""``doql drift`` — compare declared state vs. live device scan.

Exit codes follow the convention shared with ``doql doctor``:

- ``0`` → no drift detected (intended == actual)
- ``1`` → drift detected
- ``2`` → usage error (missing args, unsupported format)
- ``3`` → environment error (op3 not installed, intended file missing)

Rationale for separating "drift found" from "error": a CI check wants
``0`` vs ``1`` to gate merges, but wants to treat "couldn't even scan"
differently from "scanned successfully and found drift".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from opstree.drift.detector import DriftReport
    from opstree.snapshot.diff import Change


# Exit codes — exported so tests can reference them symbolically.
EXIT_NO_DRIFT = 0
EXIT_DRIFT = 1
EXIT_USAGE = 2
EXIT_ENV = 3


# ── rendering ─────────────────────────────────────────────────────────────


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


def _report_to_json(report: "DriftReport", intended_file: Path, target: str) -> dict:
    """Serialise a :class:`DriftReport` to plain dicts.

    ``DriftReport`` is a ``@dataclass``; ``Change`` is a frozen dataclass.
    ``dataclasses.asdict`` would work but we spell it out so the shape is
    stable and documented as the public contract for ``--json`` consumers.
    """
    return {
        "intended_file": str(intended_file),
        "target": target,
        "intended_source": report.intended_source,
        "actual_target": report.actual_target,
        "has_drift": report.has_drift,
        "summary": report.summary,
        "changes": [
            {
                "layer_id": c.layer_id,
                "path": c.path,
                "type": c.type,
                "old_value": c.old_value,
                "new_value": c.new_value,
            }
            for c in report.changes
        ],
    }


# ── CLI entry point ───────────────────────────────────────────────────────


def cmd_drift(args: argparse.Namespace) -> int:
    """Entry point for ``doql drift``."""
    target = getattr(args, "from_device", None)
    if not target:
        print(
            "❌ drift requires --from-device USER@HOST",
            file=sys.stderr,
        )
        return EXIT_USAGE

    # Resolve the intended-state file up-front so we can give a specific
    # error when the user has e.g. only app.doql.css.
    from doql.drift import detect_drift, find_intended_file
    from doql.drift.detector import _has_unsupported_intended

    if args.file:
        intended_file = Path(args.file).resolve()
        if not intended_file.is_file():
            print(f"❌ Intended-state file not found: {intended_file}", file=sys.stderr)
            return EXIT_ENV
    else:
        intended_file = find_intended_file()
        if intended_file is None:
            # Look for unsupported formats so the hint is actionable.
            other = _has_unsupported_intended(Path.cwd())
            if other is not None:
                print(
                    f"❌ drift currently supports .doql.less only. Found: "
                    f"{other.name}. Run `doql export --format less -o "
                    f"app.doql.less` first.",
                    file=sys.stderr,
                )
                return EXIT_USAGE
            print(
                "❌ No app.doql.less found — pass --file PATH or run in a "
                "project directory that contains one.",
                file=sys.stderr,
            )
            return EXIT_ENV

    layers = list(args.layers) if args.layers else None

    try:
        report = detect_drift(
            target=target,
            file=intended_file,
            layers=layers,
            ssh_key=getattr(args, "ssh_key", None),
        )
    except RuntimeError as exc:
        # op3 missing — require_op3 already formatted a hint.
        print(f"❌ {exc}", file=sys.stderr)
        return EXIT_ENV
    except FileNotFoundError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return EXIT_ENV
    except ValueError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return EXIT_USAGE

    if getattr(args, "json", False):
        payload = _report_to_json(report, intended_file, target)
        print(json.dumps(payload, indent=2, default=str))
    else:
        _render_rich(report, intended_file, target)

    return EXIT_DRIFT if report.has_drift else EXIT_NO_DRIFT
