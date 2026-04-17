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


def cmd_export(args: argparse.Namespace) -> int:
    """Export project specification to various formats."""
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    explicit_file = getattr(args, "file", None)
    if explicit_file:
        doql_file = root / explicit_file
    else:
        doql_file = detect_doql_file(root)

    fmt = args.format
    spec = doql_parser.parse_file(doql_file)

    out_path = getattr(args, "output", None)
    if out_path:
        out = open(out_path, "w", encoding="utf-8")
    else:
        out = sys.stdout

    try:
        if fmt == "openapi":
            api_gen.export_openapi(spec, out)
        elif fmt == "postman":
            export_postman.run(spec, out)
        elif fmt == "typescript-sdk":
            export_ts_sdk.run(spec, out)
        elif fmt == "yaml":
            export_yaml(spec, out)
        elif fmt == "markdown":
            export_markdown(spec, out)
        elif fmt == "css":
            export_css(spec, out)
        elif fmt == "less":
            export_less(spec, out)
        elif fmt == "sass":
            export_sass(spec, out)
        else:
            print(f"❌ Unknown format: {fmt}", file=sys.stderr)
            return 1
    finally:
        if out_path:
            out.close()

    if out_path:
        print(f"✅ Exported to {out_path}", file=sys.stderr)

    return 0
