"""Selective rebuild logic for the sync command.

This module handles incremental rebuilds by comparing current spec state
with the previous lockfile and regenerating only changed sections.
"""
from __future__ import annotations

import sys
import argparse
from typing import Set

from .. import parser as doql_parser
from .context import build_context, load_spec
from .lockfile import read_lockfile, write_lockfile, diff_sections, spec_section_hashes
from .build import (
    run_core_generators,
    run_document_generators,
    run_report_generators,
    run_i18n_generators,
    run_integration_generators,
    run_workflow_generators,
    run_plugins,
)


def determine_regeneration_set(diff_result: dict, spec) -> Set[str]:
    """Determine which generators need to re-run based on diff."""
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


def run_generators(regen: Set[str], spec, env_vars, ctx) -> int:
    """Run selected generators based on regen set. Returns count of generators run."""
    count = 0

    if "api" in regen or "web" in regen or "infra" in regen:
        targets = regen & {"api", "web", "infra"}
        for name in targets:
            from .build import should_generate_interface
            if name == "infra" or should_generate_interface(name, spec):
                from ..generators import api_gen, web_gen, infra_gen
                gen_map = {"api": api_gen.generate, "web": web_gen.generate, "infra": infra_gen.generate}
                target_dir = ctx.build_dir / name
                target_dir.mkdir(parents=True, exist_ok=True)
                print(f"🛠  Generating {name}...")
                gen_map[name](spec, env_vars, target_dir)
                count += 1

    if "documents" in regen:
        run_document_generators(spec, env_vars, ctx)
        count += 1

    if "reports" in regen:
        run_report_generators(spec, env_vars, ctx)
        count += 1

    if "i18n" in regen:
        run_i18n_generators(spec, env_vars, ctx)
        count += 1

    if "integrations" in regen:
        run_integration_generators(spec, env_vars, ctx)
        count += 1

    return count


def cmd_sync(args: argparse.Namespace) -> int:
    """Selective rebuild — only regenerate sections that changed since last build."""
    from .build import cmd_build

    ctx = build_context(args)
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

    regen = determine_regeneration_set(diff, spec)

    print(f"🔄 Changes detected in: {', '.join(sorted(all_changes.keys()))}")
    if diff["removed"]:
        print(f"   Removed: {', '.join(sorted(diff['removed'].keys()))}")
    print(f"   Regenerating: {', '.join(sorted(regen))}")

    count = run_generators(regen, spec, env_vars, ctx)

    write_lockfile(spec, ctx)
    print(f"\n✅ Sync complete — {count} generators re-run.")
    return 0
