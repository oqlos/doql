"""Emit DoqlSpec as .doql.css text — thin wrapper around exporter."""
from __future__ import annotations

import pathlib

from ..parsers.models import DoqlSpec
from ..exporters.css import export_css_file


def emit_css(spec: DoqlSpec, output: str | pathlib.Path) -> None:
    """Write *spec* as `app.doql.css` to *output* path."""
    output = pathlib.Path(output)
    export_css_file(spec, output, fmt="css")
