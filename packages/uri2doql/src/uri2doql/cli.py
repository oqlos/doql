"""CLI for doql:// URI query, materialization and patch."""

from __future__ import annotations

import argparse
import json
import sys

from uri2doql.materialize import materialize_uri
from uri2doql.nlp2uri import nlp2uri
from uri2doql.patch import apply_uri, append_uri, patch_uri, update_uri
from uri2doql.query import query_uri


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Control DOQL manifests via doql:// URIs")
    sub = parser.add_subparsers(dest="cmd", required=True)

    query = sub.add_parser("query", help="Query addressed block from DOQL file")
    query.add_argument("--uri", required=True, help="doql:// URI")
    query.add_argument("--file", help="Override source .doql.less path")
    query.add_argument("--format", choices=["json", "yaml", "less"], default="json")
    query.add_argument("--json", action="store_true", help="Print full result JSON")

    mat = sub.add_parser("materialize", help="Write addressed content to destination file")
    mat.add_argument("--uri", required=True, help="doql:// URI")
    mat.add_argument("--dest", default="", help="Destination path")

    resolve = sub.add_parser("resolve", help="Map NL prompt to doql:// URIs (nlp2uri)")
    resolve.add_argument("prompt", help="Natural language hint")
    resolve.add_argument("--file", help="Source DOQL file for block URIs")
    resolve.add_argument("--dest", help="Destination hint for materialize URIs")
    resolve.add_argument("--json", action="store_true")

    patch = sub.add_parser("patch", help="Replace block in DOQL file")
    patch.add_argument("--uri", required=True)
    patch.add_argument("--with", dest="with_file", required=True, help="Replacement block file")
    patch.add_argument("--file", help="Source DOQL manifest")

    upd = sub.add_parser("update", help="Alias for patch")
    upd.add_argument("--uri", required=True)
    upd.add_argument("--with", dest="with_file", required=True)
    upd.add_argument("--file")

    app = sub.add_parser("append", help="Append blocks to DOQL manifest")
    app.add_argument("--file", required=True, help="Target DOQL manifest")
    app.add_argument("--with", dest="with_file", required=True, help="Blocks to append")

    apply = sub.add_parser("apply", help="Apply URI action (materialize/patch/append)")
    apply.add_argument("--uri", required=True)
    apply.add_argument("--mode", default="materialize", choices=["materialize", "patch", "append", "update"])
    apply.add_argument("--dest")
    apply.add_argument("--with", dest="with_file")
    apply.add_argument("--file")

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
        hits = nlp2uri(args.prompt, file=args.file, dest=args.dest)
        payload = [hit.to_dict() for hit in hits]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            for hit in hits:
                print(f"{hit.confidence:.2f}  {hit.uri}  ({hit.match_reason})")
        return 0

    if args.cmd in {"patch", "update"}:
        content = open(args.with_file, encoding="utf-8").read()
        fn = patch_uri if args.cmd == "patch" else update_uri
        result = fn(args.uri, content=content, file=args.file)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "append":
        content = open(args.with_file, encoding="utf-8").read()
        result = append_uri(args.file, content=content, file=args.file)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    if args.cmd == "apply":
        content = open(args.with_file, encoding="utf-8").read() if args.with_file else None
        result = apply_uri(
            args.uri,
            dest=args.dest,
            content=content,
            file=args.file,
            mode=args.mode,
        )
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        return 0 if result.ok else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
