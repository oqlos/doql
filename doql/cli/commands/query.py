"""Query command — query a DATA source → JSON."""
from __future__ import annotations

import sys
import argparse
import pathlib

from ... import parser as doql_parser


def cmd_query(args: argparse.Namespace) -> int:
    """Query a DATA source and output as JSON.
    
    Supports JSON, SQLite, CSV, Excel, and API data sources.
    """
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    doql_file = root / (getattr(args, "file", None) or "app.doql")
    data_name = args.data

    spec = doql_parser.parse_file(doql_file)
    ds = next((d for d in spec.data_sources if d.name == data_name), None)
    
    if not ds:
        available = [d.name for d in spec.data_sources]
        print(f"❌ Unknown DATA source '{data_name}'. Available: {available}", file=sys.stderr)
        return 1

    print(f"🔎 Querying DATA {data_name} (source: {ds.source})...")
    # TODO: Faza 1 — load JSON/SQLite/API and output as JSON
    print("⚠️  Query engine not yet implemented — stub only.")
    return 0
