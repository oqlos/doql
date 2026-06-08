import argparse
import sys
from pathlib import Path
from doql.parsers.models import DoqlSpec
from cli2doql.scanner import scan_python_cli

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cli2doql",
        description="Scan codebase for CLI tools and output DOQL blocks",
    )
    parser.add_argument("path", nargs="?", default=".", help="Root directory to scan")
    args = parser.parse_args(argv or sys.argv[1:])

    root = Path(args.path).resolve()
    spec = DoqlSpec()
    scan_python_cli(root, spec)

    if not spec.interfaces:
        print("// No CLI interfaces detected.", file=sys.stderr)
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
        print('}')
    return 0

if __name__ == "__main__":
    sys.exit(main())
