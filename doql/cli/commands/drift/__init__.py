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

from .render import _render_rich, _render_plain, _fmt_value
from .export import _report_to_json

if TYPE_CHECKING:  # pragma: no cover
    from opstree.drift.detector import DriftReport


# Exit codes — exported so tests can reference them symbolically.
EXIT_NO_DRIFT = 0
EXIT_DRIFT = 1
EXIT_USAGE = 2
EXIT_ENV = 3


def cmd_drift(args: argparse.Namespace) -> int:
    """Compare intended (``app.doql.less``) with actual device scan."""
    file_arg = getattr(args, "file", None)
    target = getattr(args, "from_device", None)
    fmt = "json" if getattr(args, "json", False) else getattr(args, "format", "rich")
    output = getattr(args, "output", None)
    layers = getattr(args, "layers", ["service.containers"])

    if target is None:
        print("drift: --from-device required", file=sys.stderr)
        return EXIT_USAGE

    # Check for explicitly provided file first
    if file_arg is not None:
        intended_file = Path(file_arg).resolve()
        if not intended_file.exists():
            print(f"drift: file not found: {intended_file}", file=sys.stderr)
            return EXIT_ENV
    else:
        # Auto-detect intended file
        from ....drift.detector import find_intended_file, _has_unsupported_intended
        intended_file = find_intended_file()
        if intended_file is None:
            # Check if there's an unsupported format file to give better error
            unsupported = _has_unsupported_intended(Path.cwd())
            if unsupported:
                print(
                    f"drift: found {unsupported.name} but drift supports .doql.less only. "
                    f"Hint: doql export --format less to convert.",
                    file=sys.stderr,
                )
                return EXIT_USAGE
            print(
                "drift: No app.doql.less found — pass --file PATH or run in a project "
                "directory that contains one.",
                file=sys.stderr,
            )
            return EXIT_ENV

    try:
        from ....drift.detector import detect_drift
    except ImportError:
        print("drift: op3 not installed (pip install doql[op3])", file=sys.stderr)
        return EXIT_ENV

    report = detect_drift(target, file=intended_file, layers=layers)

    if fmt == "json":
        data = _report_to_json(report, intended_file, target)
        if output:
            Path(output).write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"Wrote drift report → {output}")
        else:
            print(json.dumps(data, indent=2))
        return EXIT_DRIFT if report.has_drift else EXIT_NO_DRIFT

    if fmt == "plain":
        _render_plain(report, intended_file, target)
    else:
        _render_rich(report, intended_file, target)

    return EXIT_DRIFT if report.has_drift else EXIT_NO_DRIFT
