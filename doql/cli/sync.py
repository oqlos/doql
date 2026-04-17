"""Selective rebuild logic for the sync command.

This module handles incremental rebuilds by comparing current spec state
with the previous lockfile and regenerating only changed sections.
"""
from __future__ import annotations

import sys
import argparse
from typing import Set

from .. import parser as doql_parser
from ..generators import api_gen, web_gen, infra_gen, document_gen, report_gen, i18n_gen, integrations_gen, workflow_gen, ci_gen
from .. import plugins as _plugins
from .context import BuildContext, load_spec
from .lockfile import read_lockfile, write_lockfile, diff_sections, spec_section_hashes


def determine_regeneration_set(diff_result: dict, spec) -> Set[str]:
    """Determine which generators need to re-run based on diff.
    
    Args:
        diff_result: Result from diff_sections() with added/changed/removed keys
        spec: Parsed DoqlSpec
        
    Returns:
        Set of generator names to re-run
    """
    all_changes = {**diff_result["added"], **diff_result["changed"]}
    regen: Set[str] = set()
    
    for key in list(all_changes.keys()) + list(diff_result["removed"].keys()):
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
    
    return regen


def regenerate_api(spec, env_vars, build_dir) -> None:
    """Regenerate API section if needed."""
    if not spec.entities:
        return
    print("🛠  Generating api...")
    api_dir = build_dir / "api"
    api_dir.mkdir(parents=True, exist_ok=True)
    api_gen.generate(spec, env_vars, api_dir)


def regenerate_web(spec, env_vars, build_dir) -> None:
    """Regenerate Web section if needed."""
    for iface in spec.interfaces:
        if iface.type in ("web", "pwa"):
            print("🛠  Generating web...")
            target_dir = build_dir / "web"
            target_dir.mkdir(parents=True, exist_ok=True)
            web_gen.generate(spec, env_vars, target_dir)
            break


def regenerate_infra(spec, env_vars, build_dir) -> None:
    """Regenerate Infrastructure section."""
    print("🛠  Generating infra...")
    infra_dir = build_dir / "infra"
    infra_dir.mkdir(parents=True, exist_ok=True)
    infra_gen.generate(spec, env_vars, infra_dir)


def regenerate_documents(spec, env_vars, build_dir, project_root) -> None:
    """Regenerate Documents section if needed."""
    if not spec.documents:
        return
    print("🛠  Generating documents...")
    doc_dir = build_dir / "documents"
    doc_dir.mkdir(parents=True, exist_ok=True)
    document_gen.generate(spec, env_vars, doc_dir, project_root=project_root)


def regenerate_reports(spec, env_vars, build_dir) -> None:
    """Regenerate Reports section if needed."""
    if not spec.reports:
        return
    print("🛠  Generating reports...")
    rpt_dir = build_dir / "reports"
    rpt_dir.mkdir(parents=True, exist_ok=True)
    report_gen.generate(spec, env_vars, rpt_dir)


def regenerate_i18n(spec, env_vars, build_dir) -> None:
    """Regenerate i18n section if needed."""
    if not spec.languages:
        return
    print("🛠  Generating i18n...")
    i18n_dir = build_dir / "i18n"
    i18n_dir.mkdir(parents=True, exist_ok=True)
    i18n_gen.generate(spec, env_vars, i18n_dir)


def regenerate_integrations(spec, env_vars, build_dir) -> None:
    """Regenerate Integrations section if needed."""
    if not spec.integrations:
        return
    print("🛠  Generating integrations...")
    svc_dir = build_dir / "api" / "services"
    svc_dir.mkdir(parents=True, exist_ok=True)
    integrations_gen.generate(spec, env_vars, svc_dir)


def run_generators(regen: Set[str], spec, env_vars, ctx: BuildContext) -> int:
    """Run selected generators based on regen set.
    
    Args:
        regen: Set of generator names to run
        spec: Parsed DoqlSpec
        env_vars: Environment variables dict
        ctx: BuildContext
        
    Returns:
        Number of generators that were run
    """
    count = 0
    
    if "api" in regen:
        regenerate_api(spec, env_vars, ctx.build_dir)
        count += 1
    
    if "web" in regen:
        regenerate_web(spec, env_vars, ctx.build_dir)
        count += 1
    
    if "infra" in regen:
        regenerate_infra(spec, env_vars, ctx.build_dir)
        count += 1
    
    if "documents" in regen:
        regenerate_documents(spec, env_vars, ctx.build_dir, ctx.root)
        count += 1
    
    if "reports" in regen:
        regenerate_reports(spec, env_vars, ctx.build_dir)
        count += 1
    
    if "i18n" in regen:
        regenerate_i18n(spec, env_vars, ctx.build_dir)
        count += 1
    
    if "integrations" in regen:
        regenerate_integrations(spec, env_vars, ctx.build_dir)
        count += 1
    
    return count


def cmd_sync(args: argparse.Namespace) -> int:
    """Selective rebuild — only regenerate sections that changed since last build.
    
    This command compares the current spec state with the previous lockfile
    and regenerates only the sections that have changed, been added, or removed.
    """
    from .build import cmd_build
    
    ctx = BuildContext(
        root=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve(),
        doql_file=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve() / (getattr(args, "file", None) or "app.doql"),
        env_file=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve() / ".env",
        build_dir=__import__('pathlib').Path(getattr(args, "dir", None) or ".").resolve() / "build",
    )
    
    spec, env_vars = load_spec(ctx)
    
    old_lock = read_lockfile(ctx)
    new_hashes = spec_section_hashes(spec, ctx)
    
    if not old_lock or "sections" not in old_lock:
        print("🔄 No previous lockfile — doing full build...")
        return cmd_build(args)
    
    diff = diff_sections(old_lock["sections"], new_hashes)
    all_changes = {**diff["added"], **diff["changed"]}
    
    if not all_changes and not diff["removed"]:
        print("✅ No changes detected — everything up to date.")
        return 0
    
    # Determine which generators to re-run
    regen = determine_regeneration_set(diff, spec)
    
    print(f"🔄 Changes detected in: {', '.join(sorted(all_changes.keys()))}")
    if diff["removed"]:
        print(f"   Removed: {', '.join(sorted(diff['removed'].keys()))}")
    print(f"   Regenerating: {', '.join(sorted(regen))}")
    
    # Run selected generators
    count = run_generators(regen, spec, env_vars, ctx)
    
    write_lockfile(spec, ctx)
    print(f"\n✅ Sync complete — {count} generators re-run.")
    return 0
