"""CLI for DOQL control DSL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dsl2doql.engine import execute_dsl, execute_dsl_line


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dsl2doql",
        description="Control DOQL manifests via DSL commands (QUERY, PATCH, VALIDATE, ...)",
    )
    parser.add_argument("script", nargs="?", help="Optional .dsl script file")
    parser.add_argument("-c", "--command", help="Execute single DSL command")
    parser.add_argument("--file", help="Default app.doql.less path for block URIs")
    parser.add_argument("--json", action="store_true", help="Print JSON results")
    args = parser.parse_args(argv or sys.argv[1:])

    if args.command:
        results = [execute_dsl_line(args.command, default_file=args.file)]
    elif args.script:
        text = Path(args.script).read_text(encoding="utf-8")
        results = execute_dsl(text, default_file=args.file)
    else:
        text = sys.stdin.read()
        if not text.strip():
            parser.print_help()
            return 1
        results = execute_dsl(text, default_file=args.file)

    exit_code = 0
    for result in results:
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            if result.error:
                print(f"error: {result.error}", file=sys.stderr)
            if result.output:
                print(result.output.rstrip())
        if not result.ok:
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
