from __future__ import annotations

import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rest2doql")
    sub = parser.add_subparsers(dest="cmd")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8210)
    args = parser.parse_args(argv)
    if args.cmd == "serve":
        import uvicorn
        from rest2doql.app import create_app

        uvicorn.run(create_app(), host=args.host, port=args.port)
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
