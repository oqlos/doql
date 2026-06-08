"""CLI for doql:// URI query and materialization."""

from __future__ import annotations

import argparse
import json
import sys

from uri2doql.materialize import materialize_uri
from uri2doql.query import query_uri
from uri2doql.resolve import resolve_prompt_to_doql_uri


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Address and materialize DOQL via doql:// URIs")
    sub = parser.add_subparsers(dest="cmd", required=True)

    query = sub.add_parser("query", help="Query addressed block from DOQL file")
    query.add_argument("--uri", required=True, help="doql:// URI")
    query.add_argument("--file", help="Override source .doql.less path")
    query.add_argument("--format", choices=["json", "yaml", "less"], default="json")
    query.add_argument("--json", action="store_true", help="Print full result JSON")

    mat = sub.add_parser("materialize", help="Write addressed content to destination file")
    mat.add_argument("--uri", required=True, help="doql:// URI")
    mat.add_argument("--dest", default="", help="Destination path")

    resolve = sub.add_parser("resolve", help="Map NL prompt to doql:// URIs")
    resolve.add_argument("prompt", help="Natural language hint")
    resolve.add_argument("--file", help="Source DOQL file for block URIs")
    resolve.add_argument("--dest", help="Destination hint for materialize URIs")
    resolve.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "query":
        result = query_uri(args.uri, file=args.file, fmt=args.format)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            if result.error:
                print(f"error: {result.error}", file=sys.stderr)
            print(result.rendered or json.dumps(result.data, ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "materialize":
        result = materialize_uri(args.uri, dest=args.dest or None)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "resolve":
        hits = resolve_prompt_to_doql_uri(args.prompt, file=args.file, dest=args.dest)
        payload = [hit.to_dict() for hit in hits]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for hit in hits:
                print(f"{hit.confidence:.2f}  {hit.uri}  ({hit.match_reason})")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
