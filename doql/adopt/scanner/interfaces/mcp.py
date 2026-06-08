"""MCP server interface detection (FastMCP, *-mcp entry points)."""
from __future__ import annotations

import re
from pathlib import Path

from ....parsers.models import DoqlSpec, Interface, Page

_MCP_TOOL_RE = re.compile(r'@mcp\.tool\(\)\s*\n\s*def\s+(\w+)')
_FASTMCP_RE = re.compile(r'\bFastMCP\s*\(')


def _load_pyproject_scripts(root: Path) -> dict[str, str]:
    pyproj = root / "pyproject.toml"
    if not pyproj.exists():
        return {}
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]
    try:
        with open(pyproj, "rb") as fh:
            data = tomllib.load(fh)
    except OSError:
        return {}
    return data.get("project", {}).get("scripts", {}) or {}


def _discover_mcp_tools(root: Path) -> list[str]:
    tools: list[str] = []
    src = root / "src"
    search_roots = [src] if src.is_dir() else [root]
    for base in search_roots:
        for py_file in base.rglob("*.py"):
            if any(skip in py_file.parts for skip in ("venv", ".venv", "tests", "__pycache__")):
                continue
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if "FastMCP" not in text and "@mcp.tool" not in text:
                continue
            tools.extend(_MCP_TOOL_RE.findall(text))
    return sorted(set(tools))


def scan_python_mcp(root: Path, spec: DoqlSpec) -> None:
    """Detect MCP stdio servers and tool surfaces."""
    scripts = _load_pyproject_scripts(root)
    entry_pages: list[Page] = []
    for name, target in scripts.items():
        if name.endswith("-mcp") or "-mcp" in name or target.endswith("_mcp.server:main"):
            entry_pages.append(Page(name=name, entry=target))

    tool_names = _discover_mcp_tools(root)
    has_fastmcp = bool(tool_names) or any(
        _FASTMCP_RE.search(p.read_text(encoding="utf-8", errors="ignore"))
        for p in (root / "src").rglob("*mcp*.py")
        if p.is_file() and ".venv" not in p.parts
    )

    if not entry_pages and not has_fastmcp:
        return

    iface = Interface(name="mcp", type="mcp", framework="stdio")
    for page in entry_pages:
        iface.pages.append(page)
    if tool_names:
        iface.config["tools"] = ", ".join(tool_names[:20])
        if len(tool_names) > 20:
            iface.config["tools_more"] = str(len(tool_names) - 20)
    spec.interfaces.append(iface)
