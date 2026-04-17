"""Publish command — publish artifacts to registries.

Supports PyPI (twine), npm, Docker/Podman registries, and GitHub releases.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

from ..context import build_context, load_spec


TARGETS = ("pypi", "npm", "docker", "github")


def _publish_pypi(root: pathlib.Path, dry_run: bool) -> int:
    """Publish Python package to PyPI."""
    if not (root / "pyproject.toml").exists() and not (root / "setup.py").exists():
        print("  ⏭️  No pyproject.toml or setup.py — skipping PyPI")
        return 0

    if not shutil.which("twine"):
        print("  ❌ twine not found — install with: pip install twine", file=sys.stderr)
        return 1

    print("  📦 Building Python package...")
    rc = subprocess.call([sys.executable, "-m", "build"], cwd=root)
    if rc != 0:
        return rc

    cmd = ["twine", "upload"]
    if dry_run:
        cmd.append("--repository-url")
        cmd.append("https://test.pypi.org/legacy/")
    cmd.append("dist/*")

    print(f"  📤 Publishing to {'TestPyPI' if dry_run else 'PyPI'}...")
    return subprocess.call(cmd, cwd=root)


def _publish_npm(root: pathlib.Path, dry_run: bool) -> int:
    """Publish npm package."""
    pkg_json = root / "package.json"
    if not pkg_json.exists():
        # Check build/web
        pkg_json = root / "build" / "web" / "package.json"
        if not pkg_json.exists():
            print("  ⏭️  No package.json — skipping npm")
            return 0

    if not shutil.which("npm"):
        print("  ❌ npm not found", file=sys.stderr)
        return 1

    cwd = pkg_json.parent
    cmd = ["npm", "publish"]
    if dry_run:
        cmd.append("--dry-run")
    print(f"  📤 Publishing to npm{'  (dry-run)' if dry_run else ''}...")
    return subprocess.call(cmd, cwd=cwd)


def _publish_docker(root: pathlib.Path, spec, dry_run: bool) -> int:
    """Build and push Docker/Podman image."""
    dockerfile = root / "Dockerfile"
    if not dockerfile.exists():
        dockerfile = root / "build" / "infra" / "Dockerfile"
    if not dockerfile.exists():
        print("  ⏭️  No Dockerfile — skipping docker")
        return 0

    runtime = "podman" if shutil.which("podman") else "docker"
    if not shutil.which(runtime):
        print(f"  ❌ Neither podman nor docker found", file=sys.stderr)
        return 1

    tag = f"{spec.app_name.lower().replace(' ', '-')}:{spec.version}"
    print(f"  🐳 Building image {tag}...")

    rc = subprocess.call(
        [runtime, "build", "-t", tag, "-f", str(dockerfile), "."],
        cwd=root,
    )
    if rc != 0:
        return rc

    if dry_run:
        print(f"  ⏭️  Dry-run: skipping push of {tag}")
        return 0

    print(f"  📤 Pushing {tag}...")
    return subprocess.call([runtime, "push", tag], cwd=root)


def _publish_github(root: pathlib.Path, spec, dry_run: bool) -> int:
    """Create GitHub release via gh CLI."""
    if not shutil.which("gh"):
        print("  ⏭️  gh CLI not found — skipping GitHub release")
        return 0

    tag = f"v{spec.version}"
    cmd = ["gh", "release", "create", tag, "--title", f"{spec.app_name} {spec.version}",
           "--notes", f"Release {spec.version}"]
    if dry_run:
        print(f"  ⏭️  Dry-run: would create release {tag}")
        return 0

    print(f"  🏷️  Creating GitHub release {tag}...")
    return subprocess.call(cmd, cwd=root)


def cmd_publish(args: argparse.Namespace) -> int:
    """Publish project artifacts to registries."""
    ctx = build_context(args)
    spec, env_vars = load_spec(ctx)
    dry_run = getattr(args, "dry_run", False)
    targets = getattr(args, "target", None)

    if targets:
        targets = [t.strip() for t in targets.split(",")]
    else:
        targets = list(TARGETS)

    print(f"📦 Publishing {spec.app_name} v{spec.version}"
          f"{'  (dry-run)' if dry_run else ''}...\n")

    publishers = {
        "pypi": lambda: _publish_pypi(ctx.root, dry_run),
        "npm": lambda: _publish_npm(ctx.root, dry_run),
        "docker": lambda: _publish_docker(ctx.root, spec, dry_run),
        "github": lambda: _publish_github(ctx.root, spec, dry_run),
    }

    failed: list[str] = []
    for t in targets:
        if t not in publishers:
            print(f"  ⚠️  Unknown target: {t}")
            continue
        rc = publishers[t]()
        if rc != 0:
            failed.append(t)

    if failed:
        print(f"\n❌ Failed: {', '.join(failed)}", file=sys.stderr)
        return 1

    print("\n✅ Publish complete.")
    return 0
