"""Quadlet command — Podman Quadlet management via redeploy.

Uses redeploy Python API when doql[deploy] is installed,
falls back to direct systemctl when running standalone.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys


def _install_via_redeploy_api(infra_dir: pathlib.Path, app: str, dry_run: bool) -> int:
    """Install Quadlet units via redeploy Python API.

    Returns 0=ok, 1=error, -1=redeploy not available.
    """
    migration_yaml = infra_dir / "migration.yaml"
    if not migration_yaml.exists():
        return -1

    try:
        from redeploy.models import MigrationSpec
        from redeploy.plan import Planner
        from redeploy.apply.executor import Executor
    except ImportError:
        return -1

    from rich.console import Console
    console = Console()

    spec = MigrationSpec.from_file(str(migration_yaml))
    planner = Planner.from_spec(spec)
    migration = planner.run()

    console.print(f"[bold]quadlet install[/bold]  via redeploy  "
                  f"({'dry-run' if dry_run else 'apply'})")
    for i, step in enumerate(migration.steps, 1):
        console.print(f"  {i}. [{step.risk.value}] {step.description}")

    if dry_run:
        console.print("[dim]--dry-run: no changes made[/dim]")
        return 0

    executor = Executor(migration, dry_run=False)
    results = executor.run()
    ok = all(r.get("ok", True) for r in results)
    console.print(f"{'[green]✅ Quadlet install complete[/green]' if ok else '[red]✗ Failed[/red]'}")
    return 0 if ok else 1


def _install_via_systemctl(infra_dir: pathlib.Path, app: str, dry_run: bool) -> int:
    """Install Quadlet units directly via cp + systemctl (no redeploy)."""
    quadlet_dst = pathlib.Path.home() / ".config" / "containers" / "systemd"
    container_files = list(infra_dir.glob("*.container")) + list(infra_dir.glob("*.network")) + list(infra_dir.glob("*.volume"))

    if not container_files:
        print(f"❌ No .container/.network/.volume files in {infra_dir}", file=sys.stderr)
        return 1

    print(f"🐳 Installing {len(container_files)} Quadlet unit(s) → {quadlet_dst}")
    for f in container_files:
        print(f"   {'[dry-run] ' if dry_run else ''}cp {f.name} → {quadlet_dst}/")
        if not dry_run:
            quadlet_dst.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, quadlet_dst / f.name)

    if not dry_run:
        print("🔄 systemctl --user daemon-reload")
        subprocess.call(["systemctl", "--user", "daemon-reload"])
        print(f"▶  systemctl --user start {app}.service")
        rc = subprocess.call(["systemctl", "--user", "start", f"{app}.service"])
        if rc != 0:
            print(f"⚠  systemctl start returned {rc} — check: journalctl --user -u {app}", file=sys.stderr)
            return rc
    print("✅ Quadlet install complete." if not dry_run else "✅ Dry-run complete.")
    return 0


def cmd_quadlet(args: argparse.Namespace) -> int:
    """Manage Podman Quadlet containers.

    --install   Deploy .container/.network files to ~/.config/containers/systemd/
                and reload systemd. Uses redeploy API if doql[deploy] installed.
    --dry-run   Show steps without executing.
    """
    if not args.install:
        print("ℹ️  Use --install to deploy Quadlet containers to systemd.")
        print("   Install redeploy support: pip install doql[deploy]")
        return 0

    dry_run: bool = getattr(args, "dry_run", False)
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    infra_dir = root / "build" / "infra"

    if not infra_dir.exists():
        print(f"❌ build/infra/ not found — run `doql build` first.", file=sys.stderr)
        return 1

    # infer app name from .container file or directory name
    containers = list(infra_dir.glob("*.container"))
    app = containers[0].stem if containers else root.name

    # Try redeploy API first
    rc = _install_via_redeploy_api(infra_dir, app, dry_run)
    if rc >= 0:
        return rc

    # Fallback: direct systemctl
    return _install_via_systemctl(infra_dir, app, dry_run)
