"""Desktop interface detection (Tauri, Electron)."""
from __future__ import annotations

import json
from pathlib import Path

from ....parsers.models import DoqlSpec, Interface


def scan_desktop(root: Path, spec: DoqlSpec) -> None:
    """Detect desktop targets (Tauri, Electron)."""
    if (root / "src-tauri").is_dir():
        spec.interfaces.append(Interface(
            name="desktop", type="tauri",
            framework="tauri",
        ))
    elif (root / "desktop").is_dir() and (root / "desktop" / "src-tauri").is_dir():
        spec.interfaces.append(Interface(
            name="desktop", type="tauri",
            framework="tauri",
        ))

    # Electron
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            if "electron" in deps:
                spec.interfaces.append(Interface(
                    name="desktop", type="electron",
                    framework="electron",
                ))
        except (json.JSONDecodeError, OSError):
            pass
