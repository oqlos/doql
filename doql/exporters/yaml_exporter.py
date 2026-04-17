"""Export DoqlSpec → YAML."""
from __future__ import annotations

import pathlib
from dataclasses import asdict, fields
from typing import IO, Any

import yaml

from ..parsers.models import DoqlSpec
from ..utils.clean import _clean


def spec_to_dict(spec: DoqlSpec) -> dict[str, Any]:
    """Convert DoqlSpec to a cleaned dictionary suitable for YAML/JSON."""
    raw = asdict(spec)
    return _clean(raw)


def export_yaml(spec: DoqlSpec, out: IO[str]) -> None:
    """Write DoqlSpec as YAML to the given stream."""
    data = spec_to_dict(spec)
    yaml.dump(
        data,
        out,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )


def export_yaml_file(spec: DoqlSpec, path: pathlib.Path) -> None:
    """Write DoqlSpec as YAML to a file."""
    with open(path, "w", encoding="utf-8") as f:
        export_yaml(spec, f)
