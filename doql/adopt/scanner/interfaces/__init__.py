"""Interface scanning — API, Web, Mobile, Desktop detection."""
from __future__ import annotations

from pathlib import Path

from ....parsers.models import DoqlSpec
from .api import scan_python_api
from .cli import scan_python_cli
from .web import scan_web_frontend
from .mobile import scan_mobile
from .desktop import scan_desktop

__all__ = ["scan_interfaces"]


def scan_interfaces(root: Path, spec: DoqlSpec) -> None:
    """Detect service interfaces from project structure."""
    scan_python_api(root, spec)
    scan_python_cli(root, spec)
    scan_web_frontend(root, spec)
    scan_mobile(root, spec)
    scan_desktop(root, spec)
