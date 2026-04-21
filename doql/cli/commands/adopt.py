"""doql adopt — reverse-engineer an existing project into app.doql.css/.less/.sass."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ...parsers.models import DoqlSpec


def _print_item(label: str, count: int, items: list, display_names: list[str] | None = None) -> None:
    """Print a summary line with optional item names."""
    if count and display_names:
        names_str = ", ".join(display_names[:5])
        suffix = " ..." if len(display_names) > 5 else ""
        print(f"   {label}: {count}  ({names_str}{suffix})")
    elif count:
        print(f"   {label}: {count}")
    else:
        print(f"   {label}: 0")


def _print_scan_summary(spec: DoqlSpec) -> None:
    """Print scan results summary."""
    print(f"   app:          {spec.app_name} v{spec.version}")
    _print_item("entities", len(spec.entities), spec.entities)
    _print_item("interfaces", len(spec.interfaces), spec.interfaces,
                [i.name for i in spec.interfaces])
    _print_item("databases", len(spec.databases), spec.databases,
                [d.name for d in spec.databases])
    _print_item("integrations", len(spec.integrations), spec.integrations,
                [i.name for i in spec.integrations])
    _print_item("workflows", len(spec.workflows), spec.workflows,
                [w.name for w in spec.workflows])
    _print_item("roles", len(spec.roles), spec.roles)
    _print_item("environments", len(spec.environments), spec.environments,
                [e.name for e in spec.environments])
    _print_item("env vars", len(spec.env_refs), spec.env_refs)
    deploy_target = spec.deploy.target if spec.deploy else "none"
    print(f"   deploy:       {deploy_target}")
    print()


def _cleanup_empty_output(output: Path) -> None:
    """Remove empty output file if it exists."""
    try:
        if output.exists() and output.stat().st_size == 0:
            output.unlink()
    except OSError:
        pass


def _validate_output_written(output: Path) -> bool:
    """Check that output file was written successfully."""
    if not output.exists() or output.stat().st_size == 0:
        print(f"❌ {output.name} was not written (empty output).", file=sys.stderr)
        return False
    print(f"✅ Written → {output}")
    return True


def cmd_adopt(args: argparse.Namespace) -> int:
    """Scan *target* directory (or --from-device), produce app.doql.{css|less|sass}."""
    from_device = getattr(args, "from_device", None)
    if from_device:
        return _cmd_adopt_from_device(args, from_device)
    return _cmd_adopt_from_directory(args)


def _cmd_adopt_from_directory(args: argparse.Namespace) -> int:
    """Scan a local directory — the historical ``doql adopt`` behaviour."""
    from doql.adopt.scanner import scan_project
    from doql.adopt.emitter import emit_spec

    if not args.target:
        print(
            "❌ adopt: either a target directory or --from-device USER@HOST is required.",
            file=sys.stderr,
        )
        return 2

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"❌ Not a directory: {target}", file=sys.stderr)
        return 1

    fmt = getattr(args, "format", "css")
    output = target / (args.output or f"app.doql.{fmt}")

    if output.exists() and not args.force:
        print(f"⚠️  {output.name} already exists. Use --force to overwrite.")
        return 1

    print(f"🔍 Scanning {target} …")
    spec = scan_project(target)

    _print_scan_summary(spec)

    try:
        emit_spec(spec, output, fmt=fmt)
    except Exception as exc:
        print(f"❌ Failed to render {output.name}: {exc}", file=sys.stderr)
        _cleanup_empty_output(output)
        return 1

    if not _validate_output_written(output):
        return 1

    return 0


def _cmd_adopt_from_device(args: argparse.Namespace, device: str) -> int:
    """Scan a remote device via op3 and write the resulting ``.doql.less``."""
    # ``--from-device`` only makes sense with the LESS emitter — op3's
    # ``LessAdapter`` is the renderer we delegate to.
    fmt = getattr(args, "format", "less")
    if fmt != "less":
        print(
            f"❌ adopt --from-device currently supports --format less only "
            f"(got: {fmt}).",
            file=sys.stderr,
        )
        return 2

    try:
        from doql.adopt.device_scanner import adopt_from_device
    except ImportError as exc:  # pragma: no cover — defensive
        print(f"❌ Failed to import device scanner: {exc}", file=sys.stderr)
        return 1

    # When the user specified --output we treat it as an absolute / relative
    # path; otherwise land next to the current working directory with the
    # default filename so the file is easy to find.
    default_name = f"app.doql.{fmt}"
    if args.output:
        output = Path(args.output).resolve()
    else:
        output = Path.cwd() / default_name

    if output.exists() and not args.force:
        print(f"⚠️  {output.name} already exists. Use --force to overwrite.")
        return 1

    layers = list(args.layers) if args.layers else None

    print(f"🔍 Scanning device {device} via op3 …")
    try:
        adopt_from_device(
            target=device,
            ssh_key=getattr(args, "ssh_key", None),
            layers=layers,
            output=output,
        )
    except RuntimeError as exc:
        # Raised when op3 is not installed — message already contains a hint.
        print(f"❌ {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover — unexpected failures
        print(f"❌ adopt --from-device failed: {exc}", file=sys.stderr)
        _cleanup_empty_output(output)
        return 1

    if not _validate_output_written(output):
        return 1

    return 0
