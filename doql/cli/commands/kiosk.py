"""Kiosk command — kiosk appliance management."""
from __future__ import annotations

import argparse


def cmd_kiosk(args: argparse.Namespace) -> int:
    """Manage kiosk appliance installation.
    
    Use --install to set up kiosk mode on a Raspberry Pi.
    """
    if args.install:
        print("🖥️  Installing kiosk appliance...")
        print("   Target: Raspberry Pi OS Lite 64-bit")
        # TODO: Faza 2 — Openbox autostart, chromium --kiosk, udev rules, systemd
        print("⚠️  Kiosk installer not yet implemented — stub only.")
        return 0
    
    print("ℹ️  Use --install to set up kiosk on this device.")
    return 0
