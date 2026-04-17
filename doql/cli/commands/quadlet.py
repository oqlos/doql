"""Quadlet command — Podman Quadlet management."""
from __future__ import annotations

import argparse
import pathlib


def cmd_quadlet(args: argparse.Namespace) -> int:
    """Manage Podman Quadlet containers.
    
    Use --install to deploy Quadlet container definitions to systemd.
    """
    if args.install:
        print("🐳 Installing Quadlet containers to systemd...")
        quadlet_dir = pathlib.Path.home() / ".config" / "containers" / "systemd"
        print(f"   Target: {quadlet_dir}")
        # TODO: Faza 1 — copy .container files, systemctl --user daemon-reload
        print("⚠️  Quadlet installer not yet implemented — stub only.")
        return 0
    
    print("ℹ️  Use --install to deploy Quadlet containers to systemd.")
    return 0
