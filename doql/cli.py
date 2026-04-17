"""doql CLI — backward compatibility shim.

This module re-exports all CLI functionality from the new modular structure.
All new code should import from doql.cli directly.

Migration path:
- Old: from doql.cli import main
- New: from doql.cli import main  (same import, new location)
"""
from __future__ import annotations

# Re-export all public API from new modular structure
from .cli.main import main, create_parser
from .cli.context import BuildContext, build_context, load_spec, scaffold_from_template, estimate_file_count
from .cli.lockfile import read_lockfile, write_lockfile, diff_sections, spec_section_hashes

# Command implementations (backward compatibility)
from .cli.commands import (
    cmd_init,
    cmd_validate,
    cmd_plan,
    cmd_run,
    cmd_deploy,
    cmd_export,
    cmd_generate,
    cmd_render,
    cmd_query,
    cmd_kiosk,
    cmd_quadlet,
    cmd_docs,
)
from .cli.build import cmd_build
from .cli.sync import cmd_sync

__all__ = [
    "main",
    "create_parser",
    "BuildContext",
    "build_context",
    "load_spec",
    "scaffold_from_template",
    "estimate_file_count",
    "read_lockfile",
    "write_lockfile",
    "diff_sections",
    "spec_section_hashes",
    # Commands
    "cmd_init",
    "cmd_validate",
    "cmd_plan",
    "cmd_build",
    "cmd_run",
    "cmd_deploy",
    "cmd_sync",
    "cmd_export",
    "cmd_generate",
    "cmd_render",
    "cmd_query",
    "cmd_kiosk",
    "cmd_quadlet",
    "cmd_docs",
]
