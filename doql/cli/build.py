"""Full build logic for the build command.

This module handles complete rebuilds by running all applicable generators.
"""
from __future__ import annotations

import sys
import argparse

from .. import parser as doql_parser
from ..generators import api_gen, web_gen, mobile_gen, desktop_gen, infra_gen, document_gen, report_gen, i18n_gen, integrations_gen, workflow_gen, ci_gen
from .. import plugins as _plugins
from .context import BuildContext, load_spec
from .lockfile import write_lockfile


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


def run_core_generators(spec, env_vars, ctx: BuildContext) -> None:
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


def run_report_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run report generators if reports are defined."""
    if not spec.reports:
        return
    
    print("🛠  Generating reports...")
    rpt_dir = ctx.build_dir / "reports"
    rpt_dir.mkdir(parents=True, exist_ok=True)
    report_gen.generate(spec, env_vars, rpt_dir)


def run_i18n_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run i18n generators if languages are defined."""
    if not spec.languages:
        return
    
    print("🛠  Generating i18n...")
    i18n_dir = ctx.build_dir / "i18n"
    i18n_dir.mkdir(parents=True, exist_ok=True)
    i18n_gen.generate(spec, env_vars, i18n_dir)


def run_integration_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run integration generators if integrations are defined."""
    if not (spec.integrations or spec.api_clients or spec.webhooks):
        return
    
    print("🛠  Generating integrations...")
    svc_dir = ctx.build_dir / "api" / "services"
    svc_dir.mkdir(parents=True, exist_ok=True)
    integrations_gen.generate(spec, env_vars, svc_dir)


def run_workflow_generators(spec, env_vars, ctx: BuildContext) -> None:
    """Run workflow generators if workflows are defined."""
    if not spec.workflows:
        return
    
    print("🛠  Generating workflows...")
    wf_dir = ctx.build_dir / "api" / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    workflow_gen.generate(spec, env_vars, wf_dir)


def run_ci_generator(spec, env_vars, ctx: BuildContext) -> None:
    """Run CI/CD generator (always into project root)."""
    print("🛠  Generating CI...")
    ci_gen.generate(spec, env_vars, ctx.root)


def run_plugins(spec, env_vars, ctx: BuildContext) -> None:
    """Run plugin generators."""
    _plugins.run_plugins(spec, env_vars, ctx.build_dir, ctx.root)


def cmd_build(args: argparse.Namespace) -> int:
    """Generate all code for the project.
    
    This command runs all applicable generators to create a complete build.
    Validation is performed first unless --force is specified.
    """
    ctx = BuildContext(
        root=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve(),
        doql_file=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve() / (getattr(args, "file", None) or "app.doql"),
        env_file=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve() / ".env",
        build_dir=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve() / "build",
    )
    
    spec, env_vars = load_spec(ctx)
    
    # Validate unless --force
    issues = doql_parser.validate(spec, env_vars)
    errors = [i for i in issues if i.severity == "error"]
    if errors and not getattr(args, "force", False):
        print("❌ Validation errors (use --force to ignore):", file=sys.stderr)
        for e in errors:
            print(f"   {e.path}: {e.message}", file=sys.stderr)
        return 1
    
    ctx.build_dir.mkdir(parents=True, exist_ok=True)
    
    # Run all generators in order
    run_core_generators(spec, env_vars, ctx)
    run_document_generators(spec, env_vars, ctx)
    run_report_generators(spec, env_vars, ctx)
    run_i18n_generators(spec, env_vars, ctx)
    run_integration_generators(spec, env_vars, ctx)
    run_workflow_generators(spec, env_vars, ctx)
    run_ci_generator(spec, env_vars, ctx)
    run_plugins(spec, env_vars, ctx)
    
    write_lockfile(spec, ctx)
    print(f"\n✅ Build complete — see {ctx.build_dir}/")
    return 0
