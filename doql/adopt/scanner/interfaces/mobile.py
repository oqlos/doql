"""Mobile interface detection (React Native, Expo, PWA)."""
from __future__ import annotations

import json
from pathlib import Path

from ....parsers.models import DoqlSpec, Interface


def scan_mobile(root: Path, spec: DoqlSpec) -> None:
    """Detect mobile targets."""
    # Check for React Native, Flutter, or PWA mobile
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = data.get("dependencies", {})
            if "react-native" in deps:
                spec.interfaces.append(Interface(
                    name="mobile", type="react-native",
                    framework="react-native",
                ))
                return
            if "expo" in deps:
                spec.interfaces.append(Interface(
                    name="mobile", type="expo",
                    framework="expo",
                ))
                return
        except (json.JSONDecodeError, OSError):
            pass

    # Check for mobile/ subdirectory
    if (root / "mobile").is_dir():
        spec.interfaces.append(Interface(
            name="mobile", type="pwa",
        ))
