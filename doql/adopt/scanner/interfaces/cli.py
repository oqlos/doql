"""Python CLI interface detection (click, argparse entry points)."""
from __future__ import annotations

from pathlib import Path

from ....parsers.models import DoqlSpec, Interface, Page


def scan_python_cli(root: Path, spec: DoqlSpec) -> None:
    """Detect Python CLI tools (click, argparse entry points)."""
    pyproj = root / "pyproject.toml"
    if not pyproj.exists():
        return

    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    try:
        with open(pyproj, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return

    scripts = data.get("project", {}).get("scripts", {})
    # Don't add CLI interface if we already found an API (it's the same project)
    has_api = any(i.name == "api" for i in spec.interfaces)

    for name, ep in scripts.items():
        # Skip if it's an api/server entry point
        if "server" in name or "api" in name:
            continue
        # This is a CLI tool
        # Detect framework from pyproject.toml dependencies or CLI source files
        framework = "argparse"
        deps = data.get("project", {}).get("dependencies", [])
        if deps:
            deps_str = " ".join(deps).lower()
            if "click" in deps_str:
                framework = "click"
        if framework == "argparse":
            # Fallback: scan CLI source files for click usage
            for cli_file in [root / "cli.py", root / name / "cli.py"]:
                if cli_file.exists() and "click" in cli_file.read_text().lower():
                    framework = "click"
                    break
        iface = Interface(
            name="cli",
            type="cli",
            framework=framework,
        )
        # Add entry point as page (command name)
        iface.pages.append(Page(name=name))
        spec.interfaces.append(iface)
        return  # Only add one CLI interface
