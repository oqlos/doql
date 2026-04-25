"""Full build logic for the build command.

This module handles complete rebuilds by running all applicable generators.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
import time
from typing import Callable

from pathlib import Path

from .. import parser as doql_parser
from ..generators import api_gen, web_gen, mobile_gen, desktop_gen, infra_gen, document_gen, report_gen, i18n_gen, integrations_gen, workflow_gen, ci_gen, vite_gen
from .. import plugins as _plugins
from .context import BuildContext, build_context, load_spec
from .lockfile import write_lockfile


def _watch_files(paths: list[Path], callback: Callable[[], None]) -> None:
    """Watch *paths* for changes and invoke *callback*.

    Prefers ``watchfiles`` or ``watchdog`` when installed, otherwise falls
    back to a simple polling loop.
    """
    # 1. Try watchfiles (modern, rust-based, lowest CPU)
    try:
        from watchfiles import watch
        print("👀 Watching (watchfiles) — Ctrl-C to stop")
        for changes in watch(*paths, recursive=False):
            callback()
        return
    except ImportError:
        pass

    # 2. Try watchdog (pure Python, stable)
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler

        class _Handler(FileSystemEventHandler):
            def __init__(self, cb: Callable[[], None]) -> None:
                self._cb = cb
                self._last = 0.0

            def on_modified(self, event) -> None:
                if event.is_directory:
                    return
                now = time.time()
                if now - self._last < 0.5:
                    return
                self._last = now
                self._cb()

        print("👀 Watching (watchdog) — Ctrl-C to stop")
        observer = Observer()
        for p in paths:
            observer.schedule(_Handler(callback), str(p.parent), recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        return
    except ImportError:
        pass

    # 3. Polling fallback (no deps)
    print("👀 Watching (polling) — Ctrl-C to stop")
    mtimes = {str(p): p.stat().st_mtime for p in paths if p.exists()}
    while True:
        time.sleep(1)
        changed = False
        for p in paths:
            if not p.exists():
                continue
            m = p.stat().st_mtime
            key = str(p)
            if key not in mtimes or mtimes[key] != m:
                mtimes[key] = m
                changed = True
        if changed:
            callback()


def should_generate_interface(name: str, spec) -> bool:
    """Check if interface should be generated.
    
    Args:
        name: Interface name (api, web, mobile, desktop, infra)
        spec: Parsed DoqlSpec
        
    Returns:
        True if interface should be generated
    """
    if name == "infra":
        return True
    return any(i.name == name for i in spec.interfaces)


def run_core_generators(spec, env_vars, ctx: BuildContext, no_overwrite: bool = False) -> None:
    """Run core interface generators (api, web, mobile, desktop, infra)."""
    generators = {
        "api": api_gen.generate,
        "web": web_gen.generate,
        "mobile": mobile_gen.generate,
        "desktop": desktop_gen.generate,
        "infra": infra_gen.generate,
    }
    
    for name, fn in generators.items():
        if not should_generate_interface(name, spec):
            continue
        
        print(f"🛠  Generating {name}...")
        if name == "infra":
            target_dir = ctx.build_dir / name
        else:
            target_dir = ctx.build_dir / name
        target_dir.mkdir(parents=True, exist_ok=True)
        fn(spec, env_vars, target_dir)


def run_document_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run document generators if documents are defined."""
    if not spec.documents:
        return
    
    print("🛠  Generating documents...")
    doc_dir = ctx.build_dir / "documents"
    doc_dir.mkdir(parents=True, exist_ok=True)
    document_gen.generate(spec, env_vars, doc_dir, project_root=ctx.root)


def _run_conditional_generator(
    ctx: BuildContext,
    condition: bool,
    label: str,
    output_path: str,
    generate_fn: Callable,
    spec,
    env_vars,
) -> None:
    """Generic generator runner — reduces duplication across report/i18n/integration/workflow gens."""
    if not condition:
        return
    print(f"🛠  Generating {label}...")
    out_dir = ctx.build_dir / output_path
    out_dir.mkdir(parents=True, exist_ok=True)
    generate_fn(spec, env_vars, out_dir)


def run_report_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run report generators if reports are defined."""
    _run_conditional_generator(ctx, spec.reports, "reports", "reports", report_gen.generate, spec, env_vars)


def run_i18n_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run i18n generators if languages are defined."""
    _run_conditional_generator(ctx, spec.languages, "i18n", "i18n", i18n_gen.generate, spec, env_vars)


def run_integration_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run integration generators if integrations are defined."""
    has_integrations = bool(spec.integrations or spec.api_clients or spec.webhooks)
    _run_conditional_generator(ctx, has_integrations, "integrations", "api/services", integrations_gen.generate, spec, env_vars)


def run_workflow_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run workflow generators if workflows are defined."""
    _run_conditional_generator(ctx, spec.workflows, "workflows", "api/workflows", workflow_gen.generate, spec, env_vars)


def run_ci_generator(spec, env_vars, ctx: BuildContext) -> None:
    """Run CI/CD generator (always into project root)."""
    print("🛠  Generating CI...")
    ci_gen.generate(spec, env_vars, ctx.root)


def run_vite_generator(spec, env_vars, ctx: BuildContext) -> None:
    """Run Vite config generator when a vite framework interface is present."""
    has_vite = any(
        getattr(i, "framework", None) == "vite" or getattr(i, "type", None) == "vite"
        for i in spec.interfaces
    )
    if not has_vite:
        return
    print("🛠  Generating Vite tooling config...")
    out = ctx.build_dir / "web"
    out.mkdir(parents=True, exist_ok=True)
    vite_gen.generate(spec, env_vars, out)


def run_plugins(spec, env_vars, ctx: BuildContext) -> None:
    """Run plugin generators."""
    _plugins.run_plugins(spec, env_vars, ctx.build_dir, ctx.root)


def _scan_device_for_build(ctx: BuildContext, args) -> BuildContext:
    """Scan a live device via op3 and rewrite the build context.

    Writes the resulting ``.doql.less`` to ``<root>/app.doql.less`` (or
    the path the user gave via the global ``-f/--file`` option) and
    returns a new :class:`BuildContext` whose ``doql_file`` points at
    exactly that file.

    Overwriting an existing file requires ``--force`` — we inherit the
    build command's own flag instead of introducing a second one, so the
    user only has to remember one override switch.
    """
    device = args.from_device

    # Resolve the target file path. When the user passed an explicit
    # ``-f/--file`` (global flag) we honour it; otherwise we land on
    # ``<root>/app.doql.less`` which is the convention `doql adopt`
    # already uses.
    explicit_file = getattr(args, "file", None)
    if explicit_file:
        scan_output = (ctx.root / explicit_file).resolve()
    else:
        scan_output = (ctx.root / "app.doql.less").resolve()

    # Refuse to clobber unless the user explicitly asked for it.
    if scan_output.exists() and not getattr(args, "force", False):
        print(
            f"⚠️  {scan_output.name} already exists. Use --force to overwrite "
            f"with the scanned state from {device}.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    # Lazy import — keeps the build path cheap when --from-device isn't used.
    try:
        from ..adopt.device_scanner import adopt_from_device
    except ImportError as exc:  # pragma: no cover — defensive
        print(f"❌ Failed to import device scanner: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    layers = list(args.layers) if args.layers else None

    print(f"🔍 Scanning device {device} via op3 …")
    try:
        adopt_from_device(
            target=device,
            ssh_key=getattr(args, "ssh_key", None),
            layers=layers,
            output=scan_output,
        )
    except RuntimeError as exc:
        # Raised when op3 is not installed — message already carries a hint.
        print(f"❌ {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if not scan_output.exists() or scan_output.stat().st_size == 0:
        print(f"❌ {scan_output.name} was not written (empty output).",
              file=sys.stderr)
        raise SystemExit(1)

    print(f"✅ Wrote {scan_output}")

    # Rebuild the context so the generator pipeline reads the scanned
    # file explicitly (bypassing detect_doql_file, which would otherwise
    # prefer app.doql.css if one is lying around).
    return BuildContext(
        root=ctx.root,
        doql_file=scan_output,
        env_file=ctx.env_file,
        build_dir=ctx.build_dir,
        target_env=ctx.target_env,
    )


def _do_build(args: argparse.Namespace, ctx: BuildContext) -> int:
    """Inner build routine — returns exit code."""
    spec, env_vars = load_spec(ctx)

    # Validate unless --force
    issues = doql_parser.validate(spec, env_vars)
    errors = [i for i in issues if i.severity == "error"]
    if errors and not getattr(args, "force", False):
        print("❌ Validation errors (use --force to ignore):", file=sys.stderr)
        for e in errors:
            print(f"   {e.path}: {e.message}", file=sys.stderr)
        return 1

    no_overwrite = getattr(args, "no_overwrite", False)
    real_build_dir = ctx.build_dir

    if no_overwrite:
        tmp = tempfile.mkdtemp(prefix="doql-build-")
        import pathlib
        ctx = BuildContext(
            root=ctx.root,
            doql_file=ctx.doql_file,
            env_file=ctx.env_file,
            build_dir=pathlib.Path(tmp),
        )

    ctx.build_dir.mkdir(parents=True, exist_ok=True)

    # Run all generators in order
    run_core_generators(spec, env_vars, ctx)
    run_document_generators(spec, env_vars, ctx)
    run_report_generators(spec, env_vars, ctx)
    run_i18n_generators(spec, env_vars, ctx)
    run_integration_generators(spec, env_vars, ctx)
    run_workflow_generators(spec, env_vars, ctx)
    run_ci_generator(spec, env_vars, ctx)
    run_vite_generator(spec, env_vars, ctx)
    run_plugins(spec, env_vars, ctx)

    if no_overwrite:
        skipped = _merge_no_overwrite(ctx.build_dir, real_build_dir)
        shutil.rmtree(ctx.build_dir)
        import pathlib
        ctx = BuildContext(
            root=ctx.root,
            doql_file=ctx.doql_file,
            env_file=ctx.env_file,
            build_dir=real_build_dir,
        )
        if skipped:
            print(f"⏭️  Skipped {skipped} existing file(s) (--no-overwrite)")

    write_lockfile(spec, ctx)
    print(f"\n✅ Build complete — see {real_build_dir}/")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    """Generate all code for the project.

    This command runs all applicable generators to create a complete build.
    Validation is performed first unless --force is specified.
    With --watch, rebuilds automatically when the .doql or .env file changes.
    """
    ctx = build_context(args)

    if getattr(args, "from_device", None):
        try:
            ctx = _scan_device_for_build(ctx, args)
        except SystemExit as exc:
            return int(exc.code) if exc.code is not None else 1

    # Initial build
    rc = _do_build(args, ctx)
    if rc != 0:
        return rc

    if not getattr(args, "watch", False):
        return 0

    # --watch mode
    watch_paths = [ctx.doql_file]
    if ctx.env_file.exists():
        watch_paths.append(ctx.env_file)

    def _rebuild() -> None:
        print("\n🔄 File changed — rebuilding...")
        try:
            _do_build(args, ctx)
        except Exception as exc:
            print(f"⚠️  Build failed: {exc}", file=sys.stderr)

    try:
        _watch_files(watch_paths, _rebuild)
    except KeyboardInterrupt:
        print("\n👋 Watch stopped.")
    return 0


def _merge_no_overwrite(src, dst) -> int:
    """Copy files from *src* to *dst*, skipping existing files. Returns skip count."""
    skipped = 0
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        rel = item.relative_to(src)
        target = dst / rel
        if target.exists():
            skipped += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
    return skipped
