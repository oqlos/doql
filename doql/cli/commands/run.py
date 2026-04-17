"""Run command — run locally in dev mode."""
from __future__ import annotations

import os
import shutil
import sys
import subprocess
import argparse
import pathlib


def _build_into(doql_file: pathlib.Path, workspace: pathlib.Path) -> int:
    """Parse *doql_file*, run generators, write output into *workspace*/build.

    Returns 0 on success, non-zero on failure.
    """
    from .. import build as _build_mod
    from ..context import BuildContext, load_spec
    from ..lockfile import write_lockfile
    from ... import parser as doql_parser

    build_dir = workspace / "build"
    env_file = doql_file.parent / ".env"

    ctx = BuildContext(
        root=workspace,
        doql_file=doql_file,
        env_file=env_file,
        build_dir=build_dir,
    )

    try:
        spec, env_vars = load_spec(ctx)
    except Exception as exc:
        print(f"❌ Failed to parse {doql_file}: {exc}", file=sys.stderr)
        return 1

    issues = doql_parser.validate(spec, env_vars)
    errors = [i for i in issues if i.severity == "error"]
    if errors:
        print("⚠  Validation warnings (continuing anyway):", file=sys.stderr)
        for e in errors:
            print(f"   {e.path}: {e.message}", file=sys.stderr)

    build_dir.mkdir(parents=True, exist_ok=True)
    _build_mod.run_core_generators(spec, env_vars, ctx)
    _build_mod.run_document_generators(spec, env_vars, ctx)
    _build_mod.run_report_generators(spec, env_vars, ctx)
    _build_mod.run_i18n_generators(spec, env_vars, ctx)
    _build_mod.run_integration_generators(spec, env_vars, ctx)
    _build_mod.run_workflow_generators(spec, env_vars, ctx)
    _build_mod.run_plugins(spec, env_vars, ctx)
    write_lockfile(spec, ctx)

    print(f"✅ Build complete → {build_dir}/")
    return 0


def _workspace_for_file(doql_file: pathlib.Path) -> pathlib.Path:
    """Return the .doql/ workspace directory next to *doql_file*."""
    return doql_file.parent / ".doql"


def cmd_run(args: argparse.Namespace) -> int:
    """Run project locally in dev mode.

    With -f <file>: build on-the-fly into .doql/ and run target.
    Without -f: use existing project build/ directory.
    Without --target: run full stack via docker-compose.
    With --target: run a specific interface (api, web, mobile, desktop).
    """
    explicit_file = getattr(args, "file", None)
    target = getattr(args, "target", None)
    port = getattr(args, "port", None)

    if explicit_file:
        doql_file = pathlib.Path(explicit_file).resolve()
        if not doql_file.exists():
            print(f"❌ File not found: {doql_file}", file=sys.stderr)
            return 1
        workspace = _workspace_for_file(doql_file)
        workspace.mkdir(parents=True, exist_ok=True)

        # Copy .env if present in source directory
        src_env = doql_file.parent / ".env"
        ws_env = workspace / ".env"
        if src_env.exists() and not ws_env.exists():
            shutil.copy2(src_env, ws_env)

        print(f"📦 Building {doql_file.name} → {workspace}/build/")
        rc = _build_into(doql_file, workspace)
        if rc != 0:
            return rc
        build_dir = workspace / "build"
    else:
        root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
        build_dir = root / "build"

    if target:
        return _run_target(build_dir, target, port=port)

    compose = build_dir / "infra" / "docker-compose.yml"
    if not compose.exists():
        print("❌ No build found. Run `doql build` first.", file=sys.stderr)
        return 1
    return subprocess.call(["docker", "compose", "-f", str(compose), "up", "--build"])


def _run_target(build_dir: pathlib.Path, target: str, port: int | None = None) -> int:
    """Run a specific interface target."""
    target_dir = build_dir / target
    if not target_dir.exists():
        print(f"❌ Target '{target}' not found in build/. Run `doql build` first.", file=sys.stderr)
        return 1

    if target == "api":
        api_port = port or 8000
        req = target_dir / "requirements.txt"
        if req.exists():
            subprocess.call([sys.executable, "-m", "pip", "install", "-q", "-r", str(req)])
        print(f"🚀 Starting API: http://localhost:{api_port}  (docs: http://localhost:{api_port}/docs)")
        return subprocess.call(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload",
             "--host", "127.0.0.1", "--port", str(api_port)],
            cwd=target_dir,
        )

    if target == "web":
        pkg = target_dir / "package.json"
        if not pkg.exists():
            print("❌ build/web/package.json not found.", file=sys.stderr)
            return 1
        web_port = port or 5173
        subprocess.call(["npm", "install"], cwd=target_dir)
        print(f"🚀 Starting Web: http://localhost:{web_port}")
        env = {**os.environ, "PORT": str(web_port)}
        return subprocess.call(["npm", "run", "dev", "--", "--port", str(web_port)], cwd=target_dir, env=env)

    if target == "mobile":
        mobile_port = port or 8091
        print(f"🚀 Starting Mobile (PWA): http://localhost:{mobile_port}")
        return subprocess.call(
            [sys.executable, "-m", "http.server", str(mobile_port)],
            cwd=target_dir,
        )

    if target == "desktop":
        pkg = target_dir / "package.json"
        if not pkg.exists():
            print("❌ build/desktop/package.json not found.", file=sys.stderr)
            return 1
        subprocess.call(["npm", "install"], cwd=target_dir)
        print(f"🚀 Starting Desktop (Tauri)...")
        return subprocess.call(["npm", "run", "dev"], cwd=target_dir)

    print(f"❌ Unknown target '{target}'. Use: api, web, mobile, desktop", file=sys.stderr)
    return 1
