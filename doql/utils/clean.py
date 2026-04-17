"""Recursive dict/list cleaning utility."""
from __future__ import annotations

from typing import Any


def _clean(obj: Any) -> Any:
    """Remove None/empty values and internal fields from a dataclass dict."""
    if isinstance(obj, dict):
        return {
            k: _clean(v)
            for k, v in obj.items()
            if v is not None
            and v != []
            and v != {}
            and k not in ("parse_errors",)
        }
    if isinstance(obj, list):
        return [_clean(i) for i in obj]
    return obj
