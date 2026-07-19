"""Plugin system for doql.

Plugins are discovered via the `doql_plugins` entry point group (Python packaging).
A plugin is a callable (or module with a `generate` function) that receives:
  - spec: DoqlSpec
  - env_vars: dict[str, str]
  - out_dir: pathlib.Path
  - project_root: pathlib.Path

Register a plugin in your pyproject.toml:
    [project.entry-points."doql_plugins"]
    my-plugin = "my_package.my_module:generate"

Or in-tree at `.doql-plugins/<name>.py` with a `generate(spec, env_vars, out, project_root)` function.
"""
from __future__ import annotations

import importlib
import importlib.util
import pathlib
import sys
from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from .parsers.models import DoqlSpec

PluginGenerate = Callable[[DoqlSpec, dict[str, str], pathlib.Path, pathlib.Path], None]


@dataclass
class Plugin:
    name: str
    generate: PluginGenerate
    source: str  # "entry-point" or "local"


def _discover_entry_points() -> list[Plugin]:
    """Discover plugins registered via Python entry points."""
    plugins: list[Plugin] = []
    try:
        from importlib.metadata import entry_points
        group = entry_points(group="doql_plugins")
        for ep in group:
            try:
                fn = ep.load()
                if not callable(fn):
                    raise TypeError("plugin entry point is not callable")
                plugins.append(Plugin(
                    name=ep.name,
                    generate=cast(PluginGenerate, fn),
                    source="entry-point",
                ))
            except Exception as e:
                print(f"⚠️  Failed to load plugin '{ep.name}': {e}", file=sys.stderr)
    except Exception as e:
        print(f"⚠️  Plugin discovery error: {e}", file=sys.stderr)
    return plugins


def _discover_local(project_root: pathlib.Path) -> list[Plugin]:
    """Discover plugins in `.doql-plugins/` directory of the project."""
    plugins: list[Plugin] = []
    plugins_dir = project_root / ".doql-plugins"
    if not plugins_dir.is_dir():
        return plugins

    for py_file in sorted(plugins_dir.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        name = py_file.stem
        spec = importlib.util.spec_from_file_location(f"doql_plugin_{name}", py_file)
        if not spec or not spec.loader:
            continue
        try:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            generate = getattr(mod, "generate", None)
            if callable(generate):
                plugins.append(Plugin(
                    name=name,
                    generate=cast(PluginGenerate, generate),
                    source="local",
                ))
            else:
                print(f"⚠️  Plugin '{name}' has no generate() function", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Failed to load local plugin '{name}': {e}", file=sys.stderr)
    return plugins


def discover_plugins(project_root: pathlib.Path) -> list[Plugin]:
    """Discover all plugins — entry-point + local."""
    return _discover_entry_points() + _discover_local(project_root)


def run_plugins(
    spec: DoqlSpec,
    env_vars: dict[str, str],
    build_dir: pathlib.Path,
    project_root: pathlib.Path,
) -> int:
    """Run all discovered plugins. Returns count of plugins executed."""
    plugins = discover_plugins(project_root)
    if not plugins:
        return 0

    print(f"🛠  Running {len(plugins)} plugin(s)...")
    for plugin in plugins:
        plugin_out = build_dir / "plugins" / plugin.name
        plugin_out.mkdir(parents=True, exist_ok=True)
        try:
            plugin.generate(spec, env_vars, plugin_out, project_root)
            print(f"    → plugins/{plugin.name}/ (source: {plugin.source})")
        except Exception as e:
            print(f"    ⚠️  Plugin '{plugin.name}' failed: {e}", file=sys.stderr)

    return len(plugins)
