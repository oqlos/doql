"""Integrations with sister projects.

Currently ships:
- :mod:`doql.integrations.op3_bridge` — thin shim between doql and op3.
"""
from __future__ import annotations

from .op3_bridge import (
    OP3_ENABLED_ENV,
    op3_available,
    op3_enabled,
    should_use_op3,
)

__all__ = [
    "OP3_ENABLED_ENV",
    "op3_available",
    "op3_enabled",
    "should_use_op3",
]
