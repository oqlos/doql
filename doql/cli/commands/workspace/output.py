"""Shared output / console helpers for workspace commands."""
from __future__ import annotations

import re

try:
    from rich import box
    from rich.console import Console
    from rich.table import Table
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

try:
    from taskfile.workspace import (
        Project as TaskfileProject,
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
