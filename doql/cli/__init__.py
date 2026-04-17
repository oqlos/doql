"""doql CLI package — modularized command-line interface."""
from __future__ import annotations

from .context import BuildContext, build_context, load_spec, scaffold_from_template, estimate_file_count
from .lockfile import read_lockfile, write_lockfile, diff_sections, spec_section_hashes
from .main import main

__all__ = [
    "BuildContext",
    "build_context",
    "load_spec",
    "scaffold_from_template",
    "estimate_file_count",
    "read_lockfile",
    "write_lockfile",
    "diff_sections",
    "spec_section_hashes",
    "main",
]
