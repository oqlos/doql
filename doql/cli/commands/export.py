"""Export command — export OpenAPI / Postman / TS SDK."""
from __future__ import annotations

import sys
import argparse
import pathlib

from ... import parser as doql_parser
from ...generators import api_gen, export_postman, export_ts_sdk


def cmd_export(args: argparse.Namespace) -> int:
    """Export project specification to various formats.
    
    Supported formats:
    - openapi: OpenAPI 3.0 specification
    - postman: Postman collection
    - typescript-sdk: TypeScript client SDK
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    doql_file = root / (getattr(args, "file", None) or "app.doql")
    
    fmt = args.format
    spec = doql_parser.parse_file(doql_file)
    
    if fmt == "openapi":
        api_gen.export_openapi(spec, sys.stdout)
    elif fmt == "postman":
        export_postman.run(spec, sys.stdout)
    elif fmt == "typescript-sdk":
        export_ts_sdk.run(spec, sys.stdout)
    else:
        print(f"❌ Unknown format: {fmt}", file=sys.stderr)
        return 1
    
    return 0
