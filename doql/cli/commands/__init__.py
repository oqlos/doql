"""CLI command implementations.

Each module implements a single doql subcommand.
Commands are organized by functional area:
- Project lifecycle: init, validate, plan
- Build & deploy: build, sync, run, deploy
- Export: export, generate, render, query
- Utilities: docs, kiosk, quadlet, doctor, adopt
"""
from __future__ import annotations

from .init import cmd_init
from .validate import cmd_validate
from .plan import cmd_plan
from .run import cmd_run
from .deploy import cmd_deploy
from .export import cmd_export
from .generate import cmd_generate
from .render import cmd_render
from .query import cmd_query
from .kiosk import cmd_kiosk
from .quadlet import cmd_quadlet
from .docs import cmd_docs
from .import_cmd import cmd_import
from .adopt import cmd_adopt
from .doctor import cmd_doctor
from .publish import cmd_publish
from ..build import cmd_build
from ..sync import cmd_sync

__all__ = [
    "cmd_adopt",
    "cmd_build",
    "cmd_doctor",
    "cmd_publish",
    "cmd_init",
    "cmd_validate",
    "cmd_plan",
    "cmd_run",
    "cmd_sync",
    "cmd_deploy",
    "cmd_export",
    "cmd_import",
    "cmd_generate",
    "cmd_render",
    "cmd_query",
    "cmd_kiosk",
    "cmd_quadlet",
    "cmd_docs",
]
