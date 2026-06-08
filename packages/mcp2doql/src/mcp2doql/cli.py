import argparse
import sys
from pathlib import Path
from doql.parsers.models import DoqlSpec
from mcp2doql.scanner import scan_python_mcp

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mcp2doql",
        description="Scan codebase for MCP servers/tools and output DOQL blocks",
    )
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    args = parser.parse_args(argv or sys.argv[1:])

    root = Path(args.path).resolve()
    spec = DoqlSpec()
    scan_python_mcp(root, spec)

    if not spec.interfaces:
        print("// No MCP interfaces detected.", file=sys.stderr)
        return 0

    # Output formatted interface block in DOQL/LESS syntax
    for iface in spec.interfaces:
        print(f'interface[type="{iface.type}"] {{')
        print(f'  name: {iface.name};')
        print(f'  framework: {iface.framework};')
        for page in iface.pages:
            print(f'  page[name="{page.name}"] {{')
            print(f'    entry: {page.entry};')
            print('  }')
        if iface.config:
            print('  config {')
            for k, v in iface.config.items():
                print(f'    {k}: "{v}";')
            print('  }')
        print('}')
    return 0

if __name__ == "__main__":
    sys.exit(main())
