"""Deploy command — deploy to environment.

Priority chain:
  1. redeploy Python API   (pip install doql[deploy])
  2. redeploy CLI          (subprocess fallback if API unavailable)
  3. @local/@push/@remote  (DEPLOY.directives in app.doql)
  4. docker-compose up     (bare fallback)
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

from ...generators import deploy as deploy_gen
from ..context import build_context, load_spec


def _run_directive(label: str, command: str) -> int:
    """Run a shell command as a deploy directive."""
    print(f"  ▶ @{label}: {command}")
    return subprocess.call(command, shell=True)


def _deploy_via_redeploy_api(migration_yaml: pathlib.Path, dry_run: bool, plan_only: bool) -> int:
    """Deploy using redeploy Python API (doql[deploy] installed).

    Returns exit code: 0=success, 1=failure, -1=redeploy not available.
    """
    try:
        from redeploy.models import MigrationSpec
        from redeploy.plan import Planner
        from redeploy.apply.executor import Executor
    except ImportError:
        return -1  # not installed — fall through

    from rich.console import Console
    console = Console()

    try:
        spec = MigrationSpec.from_file(str(migration_yaml))
    except Exception as exc:
        console.print(f"[red]✗ Failed to load migration.yaml: {exc}[/red]")
        return 1

    console.print(f"[bold]redeploy[/bold]  {spec.source.strategy.value} → "
                  f"[cyan]{spec.target.strategy.value}[/cyan]  ({spec.source.host})")

    planner = Planner.from_spec(spec)
    migration = planner.run()

    from rich.table import Table
    t = Table(show_header=True, box=None, padding=(0, 2))
    t.add_column("#", style="dim", width=3)
    t.add_column("ID")
    t.add_column("Action", style="cyan")
    t.add_column("Description")
    t.add_column("Risk", style="dim")
    for i, step in enumerate(migration.steps, 1):
        t.add_row(str(i), step.id, step.action.value, step.description, step.risk.value)
    console.print(t)
    console.print(f"  risk={migration.risk.value}  downtime={migration.estimated_downtime}")

    if plan_only:
        console.print("\n[dim]--plan-only: stopping before apply[/dim]")
        return 0

    executor = Executor(migration, dry_run=dry_run)
    results = executor.run()

    ok = all(r.get("ok", True) for r in results)
    failed = [r for r in results if not r.get("ok", True)]
    if failed:
        for r in failed:
            console.print(f"[red]✗ {r.get('step_id', '?')}: {r.get('error', '')}[/red]")
    console.print(
        f"\n{'[green]✅ Deploy complete[/green]' if ok else '[red]✗ Deploy failed[/red]'}"
        f"  ({len(results) - len(failed)}/{len(results)} steps OK)"
    )
    return 0 if ok else 1


def _deploy_via_redeploy_cli(migration_yaml: pathlib.Path, dry_run: bool, plan_only: bool) -> int:
    """Deploy using redeploy CLI as subprocess fallback."""
    import shutil
    if not shutil.which("redeploy"):
        return -1  # not on PATH

    cmd = ["redeploy", "run", str(migration_yaml)]
    if dry_run:
        cmd.append("--dry-run")
    if plan_only:
        cmd.append("--plan-only")
    print(f"  ▶ subprocess: {' '.join(cmd)}")
    return subprocess.call(cmd)


def cmd_deploy(args: argparse.Namespace) -> int:
    """Deploy project to target environment.

    Priority: redeploy API → redeploy CLI → @directives → docker-compose.
    Install redeploy support: pip install doql[deploy]
    """
    ctx = build_context(args)
    spec, env_vars = load_spec(ctx)

    dry_run: bool = getattr(args, "dry_run", False)
    plan_only: bool = getattr(args, "plan_only", False)
    target_env: str = getattr(args, "env", None) or "prod"

    print(f"🚀 Deploying {spec.app_name} → {target_env}...")

    # ── 1. redeploy API / CLI (uses build/infra/migration.yaml) ──────────────
    migration_yaml = ctx.build_dir / "infra" / "migration.yaml"
    if migration_yaml.exists():
        rc = _deploy_via_redeploy_api(migration_yaml, dry_run=dry_run, plan_only=plan_only)
        if rc >= 0:
            return rc

        rc = _deploy_via_redeploy_cli(migration_yaml, dry_run=dry_run, plan_only=plan_only)
        if rc >= 0:
            return rc

        print("  ⚠ redeploy not found — install with: pip install doql[deploy]")

    # ── 2. @local/@push/@remote directives ───────────────────────────────────
    directives = spec.deploy.directives
    if directives:
        for phase in ("local", "push", "remote"):
            cmd = directives.get(phase)
            if not cmd:
                continue
            rc = _run_directive(phase, cmd)
            if rc != 0:
                print(f"❌ @{phase} failed (exit {rc})", file=sys.stderr)
                return rc
        print("✅ Deploy complete.")
        return 0

    # ── 3. bare docker-compose fallback ──────────────────────────────────────
    return deploy_gen.run(ctx, target_env=target_env)
