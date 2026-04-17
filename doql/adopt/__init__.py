"""Project adoption — reverse-engineer existing projects into DoqlSpec.

doql adopt ./path → scans the project, builds a DoqlSpec, writes app.doql.css
"""
from __future__ import annotations

from .scanner import scan_project
from .emitter import emit_css

__all__ = ["scan_project", "emit_css"]
