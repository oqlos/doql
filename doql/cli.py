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

from . import __version__
from . import parser as doql_parser
from .generators import api_gen, web_gen, mobile_gen, desktop_gen, infra_gen, document_gen, report_gen, i18n_gen, integrations_gen


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
        issues = doql_parser.validate(spec, env_vars, project_root=ctx.root)
    except doql_parser.DoqlParseError as e:
        print(f"❌ Parse error: {e}", file=sys.stderr)
        return 1

    if not issues:
        print("✅ Everything looks good.")
        return 0

    errors = sum(1 for i in issues if i.severity == "error")
    warnings = sum(1 for i in issues if i.severity == "warning")
    for issue in issues:
        level = "❌" if issue.severity == "error" else "⚠️ "
        print(f"{level} {issue.path}: {issue.message}")
    print(f"\n  {errors} error(s), {warnings} warning(s)")
    return 1 if errors > 0 else 0


def cmd_plan(args) -> int:
    ctx = _build_context(args)
    spec = doql_parser.parse_file(ctx.doql_file)

    print(f"📋 Plan for {spec.app_name} (v{spec.version}):\n")
    print(f"  Domain:         {spec.domain or '(not set)'}")
    print(f"  Languages:      {spec.languages or ['(default)']}")
    print(f"  Entities:       {len(spec.entities)}")
    for e in spec.entities:
        print(f"    • {e.name} ({len(e.fields)} fields)")
    print(f"  DATA sources:   {len(spec.data_sources)}")
    for d in spec.data_sources:
        print(f"    • {d.name} ({d.source}{' → ' + d.file if d.file else ''})")
    print(f"  Templates:      {len(spec.templates)}")
    print(f"  Documents:      {len(spec.documents)}")
    for d in spec.documents:
        print(f"    • {d.name} ({d.type})")
    print(f"  Reports:        {len(spec.reports)}")
    print(f"  Databases:      {len(spec.databases)}")
    print(f"  API clients:    {len(spec.api_clients)}")
    for a in spec.api_clients:
        print(f"    • {a.name} ({a.base_url or '?'})")
    print(f"  Webhooks:       {len(spec.webhooks)}")
    print(f"  Scenarios:      {len(spec.scenarios)}")
    print(f"  Interfaces:     {[i.name for i in spec.interfaces]}")
    for i in spec.interfaces:
        pages = [p.name for p in i.pages]
        print(f"    • {i.name} ({i.type}) pages={pages}")
    print(f"  Integrations:   {[i.name for i in spec.integrations]}")
    print(f"  Workflows:      {len(spec.workflows)}")
    for w in spec.workflows:
        print(f"    • {w.name} (trigger={w.trigger or w.schedule or '?'})")
    print(f"  Roles:          {[r.name for r in spec.roles]}")
    print(f"  Deploy target:  {spec.deploy.target}")
    print(f"  Env references: {len(spec.env_refs)} vars")

    print("\n  Files to generate:")
    total = 0
    for iface in spec.interfaces:
        count = _estimate_file_count(iface)
        total += count
        print(f"    {iface.name:12} ~{count} files")
    print(f"    infra        ~{len(spec.integrations) + 3} files")
    print(f"  TOTAL:          ~{total + len(spec.integrations) + 3} files\n")
    return 0


def _load_spec(ctx: BuildContext):
    """Parse spec and env, return (spec, env_vars)."""
    spec = doql_parser.parse_file(ctx.doql_file)
    env_vars = doql_parser.parse_env(ctx.env_file)
    return spec, env_vars


def cmd_build(args) -> int:
    ctx = _build_context(args)
    spec, env_vars = _load_spec(ctx)

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

    # Documents (DOCUMENT + TEMPLATE sections)
    if spec.documents:
        print(f"🛠  Generating documents...")
        doc_dir = ctx.build_dir / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)
        document_gen.generate(spec, env_vars, doc_dir, project_root=ctx.root)

    # Reports (REPORT sections)
    if spec.reports:
        print(f"🛠  Generating reports...")
        rpt_dir = ctx.build_dir / "reports"
        rpt_dir.mkdir(parents=True, exist_ok=True)
        report_gen.generate(spec, env_vars, rpt_dir)

    # i18n (LANGUAGES section)
    if spec.languages:
        print(f"🛠  Generating i18n...")
        i18n_dir = ctx.build_dir / "i18n"
        i18n_dir.mkdir(parents=True, exist_ok=True)
        i18n_gen.generate(spec, env_vars, i18n_dir)

    # Integrations (INTEGRATION + API_CLIENT + WEBHOOK sections)
    if spec.integrations or spec.api_clients or spec.webhooks:
        print(f"🛠  Generating integrations...")
        svc_dir = ctx.build_dir / "api" / "services"
        svc_dir.mkdir(parents=True, exist_ok=True)
        integrations_gen.generate(spec, env_vars, svc_dir)

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
    """Selective rebuild — only regenerate sections that changed since last build."""
    ctx = _build_context(args)
    spec, env_vars = _load_spec(ctx)

    old_lock = _read_lockfile(ctx)
    new_hashes = _spec_section_hashes(spec, ctx)

    if not old_lock or "sections" not in old_lock:
        print("🔄 No previous lockfile — doing full build...")
        return cmd_build(args)

    diff = _diff_sections(old_lock["sections"], new_hashes)
    all_changes = {**diff["added"], **diff["changed"]}

    if not all_changes and not diff["removed"]:
        print("✅ No changes detected — everything up to date.")
        return 0

    # Determine which generators to re-run
    regen = set()
    for key in list(all_changes.keys()) + list(diff["removed"].keys()):
        if key.startswith("entity:") or key == "roles":
            regen.add("api")
            regen.add("web")
        elif key.startswith("interface:"):
            regen.add("web")
        elif key.startswith("document:"):
            regen.add("documents")
        elif key.startswith("report:"):
            regen.add("reports")
        elif key.startswith("integration:"):
            regen.add("integrations")
        elif key == "languages":
            regen.add("i18n")
        elif key == "spec_file":
            regen.update(["api", "web", "infra"])

    print(f"🔄 Changes detected in: {', '.join(sorted(all_changes.keys()))}")
    if diff["removed"]:
        print(f"   Removed: {', '.join(sorted(diff['removed'].keys()))}")
    print(f"   Regenerating: {', '.join(sorted(regen))}")

    if "api" in regen and spec.entities:
        print(f"🛠  Generating api...")
        api_dir = ctx.build_dir / "api"
        api_dir.mkdir(parents=True, exist_ok=True)
        api_gen.generate(spec, env_vars, api_dir)

    if "web" in regen:
        for iface in spec.interfaces:
            if iface.type in ("web", "pwa"):
                print(f"🛠  Generating web...")
                target_dir = ctx.build_dir / "web"
                target_dir.mkdir(parents=True, exist_ok=True)
                web_gen.generate(spec, env_vars, target_dir)
                break

    if "infra" in regen:
        print(f"🛠  Generating infra...")
        infra_dir = ctx.build_dir / "infra"
        infra_dir.mkdir(parents=True, exist_ok=True)
        infra_gen.generate(spec, env_vars, infra_dir)

    if "documents" in regen and spec.documents:
        print(f"🛠  Generating documents...")
        doc_dir = ctx.build_dir / "documents"
        doc_dir.mkdir(parents=True, exist_ok=True)
        document_gen.generate(spec, env_vars, doc_dir, project_root=ctx.root)

    if "reports" in regen and spec.reports:
        print(f"🛠  Generating reports...")
        rpt_dir = ctx.build_dir / "reports"
        rpt_dir.mkdir(parents=True, exist_ok=True)
        report_gen.generate(spec, env_vars, rpt_dir)

    if "i18n" in regen and spec.languages:
        print(f"🛠  Generating i18n...")
        i18n_dir = ctx.build_dir / "i18n"
        i18n_dir.mkdir(parents=True, exist_ok=True)
        i18n_gen.generate(spec, env_vars, i18n_dir)

    if "integrations" in regen and spec.integrations:
        print(f"🛠  Generating integrations...")
        svc_dir = ctx.build_dir / "api" / "services"
        svc_dir.mkdir(parents=True, exist_ok=True)
        integrations_gen.generate(spec, env_vars, svc_dir)

    _write_lockfile(spec, ctx)
    print(f"\n✅ Sync complete — {len(regen)} generators re-run.")  
    return 0


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


def cmd_generate(args) -> int:
    ctx = _build_context(args)
    spec = doql_parser.parse_file(ctx.doql_file)
    artifact = args.artifact

    # Find matching DOCUMENT in spec
    doc = next((d for d in spec.documents if d.name == artifact), None)
    if not doc:
        print(f"❌ Unknown artifact '{artifact}'. Available: {[d.name for d in spec.documents]}", file=sys.stderr)
        return 1

    print(f"📄 Generating {artifact} ({doc.type})...")
    # TODO: Faza 1 — Jinja2 + WeasyPrint pipeline
    print(f"   Template: {doc.template or '(none)'}")
    print(f"   Output: {doc.output or f'{artifact}.{doc.type}'}")
    print(f"⚠️  Generator not yet implemented — stub only.")
    return 0


def cmd_render(args) -> int:
    ctx = _build_context(args)
    template_path = pathlib.Path(args.template)
    if not template_path.exists():
        template_path = ctx.root / args.template
    if not template_path.exists():
        print(f"❌ Template not found: {args.template}", file=sys.stderr)
        return 1

    print(f"🎨 Rendering {template_path.name}...")
    # TODO: Faza 1 — Jinja2 render with DATA sources
    print(f"⚠️  Renderer not yet implemented — stub only.")
    return 0


def cmd_query(args) -> int:
    ctx = _build_context(args)
    spec = doql_parser.parse_file(ctx.doql_file)
    data_name = args.data

    ds = next((d for d in spec.data_sources if d.name == data_name), None)
    if not ds:
        print(f"❌ Unknown DATA source '{data_name}'. Available: {[d.name for d in spec.data_sources]}", file=sys.stderr)
        return 1

    print(f"🔎 Querying DATA {data_name} (source: {ds.source})...")
    # TODO: Faza 1 — load JSON/SQLite/API and output as JSON
    print(f"⚠️  Query engine not yet implemented — stub only.")
    return 0


def cmd_kiosk(args) -> int:
    if args.install:
        print("🖥️  Installing kiosk appliance...")
        print("   Target: Raspberry Pi OS Lite 64-bit")
        # TODO: Faza 2 — Openbox autostart, chromium --kiosk, udev rules, systemd
        print("⚠️  Kiosk installer not yet implemented — stub only.")
        return 0
    print("ℹ️  Use --install to set up kiosk on this device.")
    return 0


def cmd_quadlet(args) -> int:
    ctx = _build_context(args)
    if args.install:
        print("🐳 Installing Quadlet containers to systemd...")
        quadlet_dir = pathlib.Path.home() / ".config" / "containers" / "systemd"
        print(f"   Target: {quadlet_dir}")
        # TODO: Faza 1 — copy .container files, systemctl --user daemon-reload
        print("⚠️  Quadlet installer not yet implemented — stub only.")
        return 0
    print("ℹ️  Use --install to deploy Quadlet containers to systemd.")
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


def _spec_section_hashes(spec, ctx: BuildContext) -> dict:
    """Compute per-section hashes for diff detection."""
    import hashlib
    def _h(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    hashes = {
        "spec_file": hashlib.sha256(ctx.doql_file.read_bytes()).hexdigest(),
    }
    # Entity hashes
    for e in spec.entities:
        key = f"entity:{e.name}"
        fields_str = "|".join(f"{f.name}:{f.type}:{f.required}:{f.unique}:{f.ref}" for f in e.fields)
        hashes[key] = _h(fields_str)
    # Interface hashes
    for i in spec.interfaces:
        key = f"interface:{i.name}"
        pages_str = "|".join(p.name for p in i.pages)
        hashes[key] = _h(f"{i.type}:{pages_str}")
    # Document hashes
    for d in spec.documents:
        hashes[f"document:{d.name}"] = _h(f"{d.type}:{d.template}:{d.output}")
    # Report hashes
    for r in spec.reports:
        hashes[f"report:{r.name}"] = _h(f"{r.schedule}:{r.output}:{r.template}")
    # Integration hashes
    for ig in spec.integrations:
        hashes[f"integration:{ig.name}"] = _h(ig.name)
    # Roles
    if spec.roles:
        hashes["roles"] = _h("|".join(r.name if hasattr(r, 'name') else str(r) for r in spec.roles))
    # Languages
    if spec.languages:
        hashes["languages"] = _h("|".join(spec.languages))
    return hashes


def _read_lockfile(ctx: BuildContext) -> dict | None:
    import json
    lockfile = ctx.root / "doql.lock"
    if not lockfile.exists():
        return None
    try:
        return json.loads(lockfile.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _diff_sections(old_hashes: dict, new_hashes: dict) -> dict:
    """Return dict of changed/added/removed section keys."""
    added = {k: new_hashes[k] for k in new_hashes if k not in old_hashes}
    removed = {k: old_hashes[k] for k in old_hashes if k not in new_hashes}
    changed = {k: new_hashes[k] for k in new_hashes if k in old_hashes and old_hashes[k] != new_hashes[k]}
    return {"added": added, "removed": removed, "changed": changed}


def _write_lockfile(spec, ctx: BuildContext) -> None:
    import json, datetime
    lockfile = ctx.root / "doql.lock"
    hashes = _spec_section_hashes(spec, ctx)
    content = {
        "version": "2",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "doql_version": __version__,
        "sections": hashes,
    }
    lockfile.write_text(json.dumps(content, indent=2))




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

    s = sub.add_parser("generate", help="Generate a single document/artifact")
    s.add_argument("artifact", help="Artifact name (must match DOCUMENT in .doql)")
    s.set_defaults(func=cmd_generate)

    s = sub.add_parser("render", help="Render a template with data")
    s.add_argument("template", help="Template file path")
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("query", help="Query a DATA source → JSON")
    s.add_argument("data", help="DATA source name")
    s.set_defaults(func=cmd_query)

    s = sub.add_parser("kiosk", help="Kiosk appliance management")
    s.add_argument("--install", action="store_true", help="Install kiosk on this device")
    s.set_defaults(func=cmd_kiosk)

    s = sub.add_parser("quadlet", help="Podman Quadlet management")
    s.add_argument("--install", action="store_true", help="Install Quadlet to systemd")
    s.set_defaults(func=cmd_quadlet)

    s = sub.add_parser("docs", help="Generate documentation site")
    s.set_defaults(func=cmd_docs)

    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
