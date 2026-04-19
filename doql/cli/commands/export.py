"""Export command — export to OpenAPI / Postman / TS SDK / YAML / Markdown / CSS / LESS / SASS."""
from __future__ import annotations

import sys
import argparse
import pathlib

from ... import parser as doql_parser
from ...parsers import detect_doql_file
from ...generators import api_gen, export_postman, export_ts_sdk
from ...exporters.yaml_exporter import export_yaml
from ...exporters.markdown_exporter import export_markdown
from ...exporters.css_exporter import export_css, export_less, export_sass

ALL_FORMATS = [
    "openapi", "postman", "typescript-sdk",
    "yaml", "markdown", "css", "less", "sass",
]


_EXPORTERS = {
    "openapi":        lambda spec, out: api_gen.export_openapi(spec, out),
    "postman":        lambda spec, out: export_postman.run(spec, out),
    "typescript-sdk": lambda spec, out: export_ts_sdk.run(spec, out),
    "yaml":           lambda spec, out: export_yaml(spec, out),
    "markdown":       lambda spec, out: export_markdown(spec, out),
    "css":            lambda spec, out: export_css(spec, out),
    "less":           lambda spec, out: export_less(spec, out),
    "sass":           lambda spec, out: export_sass(spec, out),
}


def cmd_export(args: argparse.Namespace) -> int:
    """Export project specification to various formats."""
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    explicit_file = getattr(args, "file", None)
    doql_file = (root / explicit_file) if explicit_file else detect_doql_file(root)

    fmt = args.format
    exporter = _EXPORTERS.get(fmt)
    if exporter is None:
        print(f"❌ Unknown format: {fmt}", file=sys.stderr)
        return 1

    spec = doql_parser.parse_file(doql_file)
    out_path = getattr(args, "output", None)
    out = open(out_path, "w", encoding="utf-8") if out_path else sys.stdout

    try:
        exporter(spec, out)
    finally:
        if out_path:
            out.close()

    if out_path:
        print(f"✅ Exported to {out_path}", file=sys.stderr)

    return 0
