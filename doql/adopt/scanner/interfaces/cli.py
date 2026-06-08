"""Python CLI interface detection for doql adopt."""
from __future__ import annotations

from pathlib import Path

from ....parsers.models import DoqlSpec, Interface, Page


def _is_server_entry(name: str, target: str) -> bool:
    lowered = f"{name} {target}".lower()
    return "server" in lowered or (".api:" in lowered and "api" in name)


def _is_mcp_entry(name: str, target: str) -> bool:
    lowered = f"{name} {target}".lower()
    return name.endswith("-mcp") or "-mcp" in name or "_mcp.server:" in lowered


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
    if not scripts:
        return

    framework = "argparse"
    deps = data.get("project", {}).get("dependencies", [])
    if deps:
        deps_str = " ".join(deps).lower()
        if "click" in deps_str:
            framework = "click"
    if framework == "argparse":
        for cli_file in [root / "cli.py"] + list(root.glob("*/cli.py")):
            if cli_file.exists() and "click" in cli_file.read_text(encoding="utf-8", errors="ignore").lower():
                framework = "click"
                break

    pages: list[Page] = []
    for name, ep in scripts.items():
        if _is_server_entry(name, ep) or _is_mcp_entry(name, ep):
            continue
        pages.append(Page(name=name, entry=ep))

    if not pages:
        return

    spec.interfaces.append(
        Interface(name="cli", type="cli", framework=framework, pages=pages),
    )
