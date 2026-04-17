"""Main entry point for doql CLI.

This module sets up the argument parser and dispatches to command handlers.
All actual command logic is in doql/cli/commands/.
"""
from __future__ import annotations

import argparse
import sys

from .. import __version__
from .commands import (
    cmd_init, cmd_validate, cmd_plan, cmd_run, cmd_deploy,
    cmd_export, cmd_import, cmd_generate, cmd_render, cmd_query,
    cmd_kiosk, cmd_quadlet, cmd_docs,
)
from .build import cmd_build
from .sync import cmd_sync


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser with all subcommands."""
    p = argparse.ArgumentParser(
        prog="doql",
        description="Declarative OQL — build apps from .doql files"
    )
    p.add_argument("--version", action="version", version=f"doql {__version__}")
    p.add_argument("-d", "--dir", help="Project directory (default: current)")
    p.add_argument("-f", "--file", help="Doql file (default: app.doql)")
    
    sub = p.add_subparsers(dest="cmd", required=True)
    
    # init
    s = sub.add_parser("init", help="Create new project from template")
    s.add_argument("name", help="Project name / directory (use '-' with --list to just list)")
    s.add_argument("--template", "-t", help="Template name — use --list-templates to see all")
    s.add_argument("--list-templates", action="store_true", help="List available templates and exit")
    s.set_defaults(func=cmd_init)
    
    # validate
    s = sub.add_parser("validate", help="Validate .doql + .env")
    s.set_defaults(func=cmd_validate)
    
    # plan
    s = sub.add_parser("plan", help="Dry-run: show what would be generated")
    s.set_defaults(func=cmd_plan)
    
    # build
    s = sub.add_parser("build", help="Generate all code")
    s.add_argument("--force", action="store_true")
    s.set_defaults(func=cmd_build)
    
    # run
    s = sub.add_parser("run", help="Run locally (dev mode)")
    s.add_argument("--target", "-t", choices=["api", "web", "mobile", "desktop"],
                   help="Run a specific target (default: full stack via docker-compose)")
    s.set_defaults(func=cmd_run)
    
    # deploy
    s = sub.add_parser("deploy", help="Deploy to environment")
    s.add_argument("--env", choices=["dev", "staging", "prod"])
    s.set_defaults(func=cmd_deploy)
    
    # sync
    s = sub.add_parser("sync", help="Re-generate changed parts (merge-friendly)")
    s.set_defaults(func=cmd_sync)
    
    # export
    s = sub.add_parser("export", help="Export OpenAPI / Postman / TS SDK / YAML / Markdown / CSS / LESS / SASS")
    s.add_argument("--format", required=True,
                   choices=["openapi", "postman", "typescript-sdk",
                            "yaml", "markdown", "css", "less", "sass"])
    s.add_argument("-o", "--output", help="Output file path (default: stdout)")
    s.set_defaults(func=cmd_export)

    # import
    s = sub.add_parser("import", help="Import YAML → DOQL format")
    s.add_argument("source", help="Source YAML file path")
    s.add_argument("--format", required=True,
                   choices=["yaml", "css", "less", "sass"],
                   help="Output format")
    s.add_argument("-o", "--output", help="Output file path")
    s.set_defaults(func=cmd_import)
    
    # generate
    s = sub.add_parser("generate", help="Generate a single document/artifact")
    s.add_argument("artifact", help="Artifact name (must match DOCUMENT in .doql)")
    s.set_defaults(func=cmd_generate)
    
    # render
    s = sub.add_parser("render", help="Render a template with data")
    s.add_argument("template", help="Template file path")
    s.set_defaults(func=cmd_render)
    
    # query
    s = sub.add_parser("query", help="Query a DATA source → JSON")
    s.add_argument("data", help="DATA source name")
    s.set_defaults(func=cmd_query)
    
    # kiosk
    s = sub.add_parser("kiosk", help="Kiosk appliance management")
    s.add_argument("--install", action="store_true", help="Install kiosk on this device")
    s.set_defaults(func=cmd_kiosk)
    
    # quadlet
    s = sub.add_parser("quadlet", help="Podman Quadlet management")
    s.add_argument("--install", action="store_true", help="Install Quadlet to systemd")
    s.set_defaults(func=cmd_quadlet)
    
    # docs
    s = sub.add_parser("docs", help="Generate documentation site")
    s.set_defaults(func=cmd_docs)
    
    return p


def main() -> int:
    """Main entry point for doql CLI.
    
    Parses arguments and dispatches to the appropriate command handler.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    p = create_parser()
    args = p.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
