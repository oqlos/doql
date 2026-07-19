"""Emit a stable JSON representation of DOQL site topology."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from ...parsers import parse_file


TOPOLOGY_SCHEMA = "doql.site-topology/v1"


def cmd_topology(args: argparse.Namespace) -> int:
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    source = pathlib.Path(getattr(args, "file", None) or "app.doql")
    if not source.is_absolute():
        source = root / source
    source = source.resolve()

    try:
        spec = parse_file(source)
    except Exception as error:
        print(json.dumps({"schema": TOPOLOGY_SCHEMA, "ok": False, "error": str(error)}))
        return 2

    diagnostics = [
        {
            "severity": issue.severity,
            "message": issue.message,
            "path": issue.path,
            "line": issue.line,
        }
        for issue in spec.parse_errors
    ]
    errors = [item for item in diagnostics if item["severity"] == "error"]
    main_domain = str(getattr(args, "main_domain", None) or "").strip().lower().rstrip(".")
    sites = [
        {
            "domain": site.domain,
            "source": site.source,
            "remote_path": site.remote_path,
            "is_main": bool(site.is_main or (main_domain and site.domain == main_domain)),
        }
        for site in spec.sites
    ]
    print(json.dumps({
        "schema": TOPOLOGY_SCHEMA,
        "ok": not errors,
        "profile": "doql:site-topology/v1",
        "source": str(source),
        "sites": sites,
        "diagnostics": diagnostics,
    }, ensure_ascii=False))
    return 0 if not errors else 1
