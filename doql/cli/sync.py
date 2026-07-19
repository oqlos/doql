"""Selective rebuild logic for the sync command.

This module handles incremental rebuilds by comparing current spec state
with the previous lockfile and regenerating only changed sections.
"""
from __future__ import annotations

import argparse
from typing import Any, cast

from ..parsers.models import DoqlSpec
from .context import BuildContext, build_context, load_spec
from .lockfile import read_lockfile, write_lockfile, diff_sections, spec_section_hashes
from .build import (
    run_document_generators,
    run_report_generators,
    run_i18n_generators,
    run_integration_generators,
)

DiffResult = dict[str, dict[str, str]]


def determine_regeneration_set(diff_result: DiffResult, spec: DoqlSpec) -> set[str]:
    """Determine which generators need to re-run based on diff."""
    all_changes = {**diff_result["added"], **diff_result["changed"]}
    regen: set[str] = set()

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


def _run_interface_generators(
    regen: set[str],
    spec: DoqlSpec,
    env_vars: dict[str, str],
    ctx: BuildContext,
) -> int:
    """Run api/web/infra generators for any of those that are in *regen*. Returns count."""
    targets = regen & {"api", "web", "infra"}
    if not targets:
        return 0
    from .build import should_generate_interface
    from ..generators import api_gen, web_gen, infra_gen
    gen_map = {"api": api_gen.generate, "web": web_gen.generate, "infra": infra_gen.generate}
    count = 0
    for name in targets:
        if name == "infra" or should_generate_interface(name, spec):
            target_dir = ctx.build_dir / name
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"🛠  Generating {name}...")
            gen_map[name](spec, env_vars, target_dir)
            count += 1
    return count


def run_generators(
    regen: set[str],
    spec: DoqlSpec,
    env_vars: dict[str, str],
    ctx: BuildContext,
) -> int:
    """Run selected generators based on regen set. Returns count of generators run."""
    count = _run_interface_generators(regen, spec, env_vars, ctx)

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

    old_sections: Any = old_lock.get("sections") if old_lock else None
    if (
        not isinstance(old_sections, dict)
        or not all(isinstance(key, str) and isinstance(value, str)
                   for key, value in old_sections.items())
    ):
        print("🔄 No previous lockfile — doing full build...")
        return cmd_build(args)

    diff = diff_sections(cast(dict[str, str], old_sections), new_hashes)
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
