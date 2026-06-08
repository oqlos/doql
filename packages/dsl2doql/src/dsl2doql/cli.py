import argparse
import sys
from pathlib import Path
from dsl2doql.converter import convert_dsl_to_doql

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="dsl2doql",
        description="Convert OQL scenario files into DOQL workflow syntax",
    )
    parser.add_argument("file", help="Path to OQL scenario file to convert")
    args = parser.parse_args(argv or sys.argv[1:])

    path = Path(args.file)
    if not path.is_file():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    dsl_text = path.read_text(encoding="utf-8")
    default_name = path.stem
    doql_workflow = convert_dsl_to_doql(dsl_text, default_name)

    print(doql_workflow, end="")
    return 0

if __name__ == "__main__":
    sys.exit(main())
