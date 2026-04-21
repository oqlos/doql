"""Drift detection between declared `.doql.less` and a live device scan.

Public surface:

``detect_drift(target, *, file=None, layers=None, ssh_key=None, context_factory=None)``
    Parse the intended state from ``file`` (or an auto-detected
    ``app.doql.less``), scan the device via op3, return an
    :class:`opstree.DriftReport`.
"""
from __future__ import annotations

from .detector import (
    detect_drift,
    find_intended_file,
    parse_intended,
)

__all__ = [
    "detect_drift",
    "find_intended_file",
    "parse_intended",
]
