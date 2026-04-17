"""Import command — import from YAML to .doql / .doql.css / .doql.less / .doql.sass."""
from __future__ import annotations

import sys
import argparse
import pathlib

from ...importers.yaml_importer import import_yaml_file
from ...exporters.css_exporter import export_css_file
from ...exporters.yaml_exporter import export_yaml_file


def cmd_import(args: argparse.Namespace) -> int:
    """Import a YAML spec file and convert to DOQL format."""
    source = pathlib.Path(args.source).resolve()
    if not source.exists():
        print(f"❌ Source file not found: {source}", file=sys.stderr)
        return 1

    fmt = args.format
    output = getattr(args, "output", None)

    spec = import_yaml_file(source)

    if output:
        out_path = pathlib.Path(output).resolve()
    else:
        stem = source.stem.replace(".yml", "").replace(".yaml", "")
        if fmt == "doql":
            out_path = source.parent / f"{stem}.doql"
        elif fmt in ("css", "less", "sass"):
            out_path = source.parent / f"{stem}.doql.{fmt}"
        else:
            out_path = source.parent / f"{stem}.doql.yaml"

    if fmt == "yaml":
        export_yaml_file(spec, out_path)
    elif fmt in ("css", "less", "sass"):
        export_css_file(spec, out_path, fmt=fmt)
    else:
        print(f"❌ Unknown output format: {fmt}", file=sys.stderr)
        return 1

    print(f"✅ Imported {source.name} → {out_path}", file=sys.stderr)
    return 0
