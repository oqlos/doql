"""doql CLI — generator aplikacji z deklaracji .doql.

Szkielet — minimalny runnable przykład, pełna implementacja wymaga
generatorów dla każdego targetu (API, web, mobile, desktop, infra).
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from dataclasses import dataclass
from typing import Optional

from . import parser as doql_parser
from .generators import api_gen, web_gen, mobile_gen, desktop_gen, infra_gen


@dataclass
class BuildContext:
    root: pathlib.Path
    doql_file: pathlib.Path
    env_file: pathlib.Path
    build_dir: pathlib.Path
    target_env: str = "dev"


def cmd_init(args) -> int:
    template = args.template or "minimal"
    target = pathlib.Path(args.name)
    if target.exists():
        print(f"❌ Directory {target} already exists", file=sys.stderr)
        return 1

    print(f"📦 Scaffolding {target} from template '{template}'...")
    _scaffold_from_template(template, target)
    print(f"✅ Created {target}/")
    print(f"   Next steps:")
    print(f"     cd {target}")
    print(f"     cp .env.example .env && $EDITOR .env")
    print(f"     doql validate")
    print(f"     doql build")
    return 0


def cmd_validate(args) -> int:
    ctx = _build_context(args)
    print(f"🔍 Validating {ctx.doql_file}...")
    try:
        spec = doql_parser.parse_file(ctx.doql_file)
        env_vars = doql_parser.parse_env(ctx.env_file)
        issues = doql_parser.validate(spec, env_vars)
    except doql_parser.DoqlParseError as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 1

    if not issues:
        print("✅ Everything looks good.")
        return 0

    for issue in issues:
        level = "❌" if issue.severity == "error" else "⚠️ "
        print(f"{level} {issue.path}: {issue.message}")
    return 1 if any(i.severity == "error" for i in issues) else 0


def cmd_plan(args) -> int:
    ctx = _build_context(args)
    spec = doql_parser.parse_file(ctx.doql_file)

    print(f"📋 Plan for {spec.app_name} (v{spec.version}):\n")
    print(f"  Entities:       {len(spec.entities)}")
    print(f"  Scenarios:      {len(spec.scenarios)}")
    print(f"  Interfaces:     {[i.name for i in spec.interfaces]}")
    print(f"  Integrations:   {[i.name for i in spec.integrations]}")
    print(f"  Workflows:      {len(spec.workflows)}")
    print(f"  Roles:          {[r.name for r in spec.roles]}")
    print(f"  Deploy target:  {spec.deploy.target}")

    print("\n  Files to generate:")
    total = 0
    for iface in spec.interfaces:
        count = _estimate_file_count(iface)
        total += count
        print(f"    {iface.name:12} ~{count} files")
    print(f"    infra        ~{len(spec.integrations) + 3} files")
    print(f"  TOTAL:          ~{total + len(spec.integrations) + 3} files\n")
    return 0


def cmd_build(args) -> int:
    ctx = _build_context(args)
    spec = doql_parser.parse_file(ctx.doql_file)
    env_vars = doql_parser.parse_env(ctx.env_file)

    issues = doql_parser.validate(spec, env_vars)
    errors = [i for i in issues if i.severity == "error"]
    if errors and not args.force:
        print("❌ Validation errors (use --force to ignore):", file=sys.stderr)
        for e in errors:
            print(f"   {e.path}: {e.message}", file=sys.stderr)
        return 1

    ctx.build_dir.mkdir(parents=True, exist_ok=True)

    generators = {
        "api": api_gen.generate,
        "web": web_gen.generate,
        "mobile": mobile_gen.generate,
        "desktop": desktop_gen.generate,
        "infra": infra_gen.generate,
    }

    for name, fn in generators.items():
        target_dir = ctx.build_dir / name
        should_generate = (
            name == "infra"
            or any(i.name == name for i in spec.interfaces)
        )
        if not should_generate:
            continue
        print(f"🛠  Generating {name}...")
        target_dir.mkdir(parents=True, exist_ok=True)
        fn(spec, env_vars, target_dir)

    _write_lockfile(spec, ctx)
    print(f"\n✅ Build complete — see {ctx.build_dir}/")
    return 0


def cmd_run(args) -> int:
    ctx = _build_context(args)
    # Dev mode — używa docker-compose z build/infra
    import subprocess
    compose = ctx.build_dir / "infra" / "docker-compose.yml"
    if not compose.exists():
        print("❌ No build found. Run `doql build` first.", file=sys.stderr)
        return 1
    return subprocess.call(["docker", "compose", "-f", str(compose), "up", "--build"])


def cmd_deploy(args) -> int:
    ctx = _build_context(args)
    ctx.target_env = args.env or "prod"
    print(f"🚀 Deploying to {ctx.target_env}...")
    # Delegated to infra_gen's deploy script
    from .generators import deploy
    return deploy.run(ctx, target_env=ctx.target_env)


def cmd_sync(args) -> int:
    # Merge-friendly: re-generuje tylko pliki, które nie mają marker'a @doql:keep
    ctx = _build_context(args)
    print("🔄 Syncing (merge-friendly)...")
    # Używa lockfile do wykrycia zmian
    return cmd_build(args)


def cmd_export(args) -> int:
    ctx = _build_context(args)
    fmt = args.format
    spec = doql_parser.parse_file(ctx.doql_file)
    if fmt == "openapi":
        from .generators import api_gen
        api_gen.export_openapi(spec, sys.stdout)
    elif fmt == "postman":
        from .generators import export_postman
        export_postman.run(spec, sys.stdout)
    elif fmt == "typescript-sdk":
        from .generators import export_ts_sdk
        export_ts_sdk.run(spec, sys.stdout)
    else:
        print(f"❌ Unknown format: {fmt}", file=sys.stderr)
        return 1
    return 0


def cmd_docs(args) -> int:
    ctx = _build_context(args)
    spec = doql_parser.parse_file(ctx.doql_file)
    from .generators import docs_gen
    out = ctx.root / "docs"
    docs_gen.generate(spec, out)
    print(f"📚 Docs generated in {out}")
    return 0


# ────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────

def _build_context(args) -> BuildContext:
    root = pathlib.Path(args.dir or ".").resolve()
    return BuildContext(
        root=root,
        doql_file=root / (args.file or "app.doql"),
        env_file=root / ".env",
        build_dir=root / "build",
    )


def _scaffold_from_template(template: str, target: pathlib.Path) -> None:
    import shutil, importlib.resources as res
    # TODO: użyj importlib.resources z templates/*
    templates_dir = pathlib.Path(__file__).parent / "scaffolds" / template
    if not templates_dir.exists():
        raise SystemExit(f"Template '{template}' not found")
    shutil.copytree(templates_dir, target)


def _estimate_file_count(iface) -> int:
    # Rough estimate per interface type
    if iface.type == "rest":
        return len(iface.entities) * 4 + 10  # model + schema + route + test + config
    if iface.type in ("spa", "react", "vue"):
        return len(iface.pages) * 2 + 20
    if iface.type == "pwa":
        return 10
    if iface.type in ("electron", "tauri"):
        return 15
    return 5


def _write_lockfile(spec, ctx: BuildContext) -> None:
    import json, hashlib, datetime
    lockfile = ctx.root / "doql.lock"
    content = {
        "version": "1",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "spec_hash": hashlib.sha256(ctx.doql_file.read_bytes()).hexdigest(),
        "doql_version": __version__,
    }
    lockfile.write_text(json.dumps(content, indent=2))


__version__ = "0.1.0"


# ────────────────────────────────────────────────────────
# Entry point
# ────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(prog="doql", description="Declarative OQL — build apps from .doql files")
    p.add_argument("--version", action="version", version=f"doql {__version__}")
    p.add_argument("-d", "--dir", help="Project directory (default: current)")
    p.add_argument("-f", "--file", help="Doql file (default: app.doql)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="Create new project from template")
    s.add_argument("name", help="Project name / directory")
    s.add_argument("--template", "-t", help="Template (minimal|asset-management|calibration-lab|iot-fleet)")
    s.set_defaults(func=cmd_init)

    s = sub.add_parser("validate", help="Validate .doql + .env")
    s.set_defaults(func=cmd_validate)

    s = sub.add_parser("plan", help="Dry-run: show what would be generated")
    s.set_defaults(func=cmd_plan)

    s = sub.add_parser("build", help="Generate all code")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_build)

    s = sub.add_parser("run", help="Run locally (dev mode)")
    s.set_defaults(func=cmd_run)

    s = sub.add_parser("deploy", help="Deploy to environment")
    s.add_argument("--env", choices=["dev", "staging", "prod"])
    s.set_defaults(func=cmd_deploy)

    s = sub.add_parser("sync", help="Re-generate changed parts (merge-friendly)")
    s.set_defaults(func=cmd_sync)

    s = sub.add_parser("export", help="Export OpenAPI / Postman / TS SDK")
    s.add_argument("--format", required=True, choices=["openapi", "postman", "typescript-sdk"])
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("docs", help="Generate documentation site")
    s.set_defaults(func=cmd_docs)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
