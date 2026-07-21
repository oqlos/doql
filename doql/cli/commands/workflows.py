"""Workflows command — print a project's declared workflows and dependencies.

`doql drift` compares a declaration against a live device and needs op3 plus an
SSH target. This command answers the local question instead — "what does this
project say it runs?" — so a CI job, a scheduler or an agent can check its own
commands against the declaration without any device access.
"""
from __future__ import annotations

import argparse
import json
import pathlib

from ...workflows import declared_dependencies, find_declaration, workflow_commands


def cmd_workflows(args: argparse.Namespace) -> int:
    """Print declared workflows; return 1 when the project has no declaration."""
    root = pathlib.Path(getattr(args, "dir", None) or ".").resolve()
    explicit = getattr(args, "file", None)
    source = pathlib.Path(explicit).resolve() if explicit else root

    declaration = find_declaration(root) if source.is_dir() else source
    if declaration is None or not declaration.is_file():
        print(f"❌ No DOQL declaration found in {root}")
        return 1

    workflows = workflow_commands(declaration)
    dependencies = declared_dependencies(declaration)

    if getattr(args, "format", "text") == "json":
        payload = {
            "file": str(declaration),
            "workflows": {name: [list(command) for command in commands] for name, commands in workflows.items()},
            "dependencies": {group: list(entries) for group, entries in dependencies.items()},
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    print(f"📋 {declaration}")
    if dependencies:
        print("\ndependencies:")
        for group, entries in sorted(dependencies.items()):
            print(f"  {group}: {', '.join(entries)}")
    print("\nworkflows:")
    for name, commands in sorted(workflows.items()):
        if not commands:
            print(f"  {name}: (no commands)")
            continue
        for command in commands:
            print(f"  {name}: {' '.join(command)}")
    return 0
