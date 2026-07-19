"""Shared output / console helpers for workspace commands."""
from __future__ import annotations

import re

__all__ = [
    "_print",
    "_tf_analyze",
    "_tf_discover",
    "_tf_filter",
    "_tf_fix",
    "_tf_validate",
    "console",
]

try:
    from rich.console import Console
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

try:
    from taskfile.workspace import (
        discover_projects as _tf_discover,
        filter_projects as _tf_filter,
        analyze_project as _tf_analyze,
        validate_project as _tf_validate,
        fix_project as _tf_fix,
    )
    _HAS_TASKFILE = True
except ImportError:
    _HAS_TASKFILE = False


console = Console() if _HAS_RICH else None


def _print(msg: str) -> None:
    if console:
        console.print(msg)
    else:
        # Strip rich markup for plain print
        print(re.sub(r'\[[^\]]+\]', '', msg))
