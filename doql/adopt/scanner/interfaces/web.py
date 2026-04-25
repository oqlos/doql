"""Web frontend interface detection (React, Vue, Svelte, Vite, static)."""
from __future__ import annotations

import json
from pathlib import Path

from ....parsers.models import DoqlSpec, Interface, Page
from ..utils import camel_to_kebab


def _detect_web_framework(root: Path) -> str | None:
    """Detect web framework from package.json and config files."""
    pkg = root / "package.json"
    if pkg.exists():
        try:
            data = json.loads(pkg.read_text())
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

            if "react" in deps or "@vitejs/plugin-react" in deps:
                return "react"
            if "vue" in deps or "@vitejs/plugin-vue" in deps:
                return "vue"
            if "svelte" in deps:
                return "svelte"
            if "vite" in deps:
                return "vite"
        except (json.JSONDecodeError, OSError):
            pass

    # Standalone Vite without package.json (rare)
    if any((root / f).exists() for f in ("vite.config.ts", "vite.config.js", "vite.config.mjs")):
        return "vite"
    return None


def _scan_pages_dir(pdir, page_seen: set) -> list:
    """Yield Page objects from a directory of page components."""
    pages = []
    for entry in sorted(pdir.iterdir()):
        name = entry.stem
        if entry.is_file() and entry.suffix in (".jsx", ".tsx", ".vue", ".svelte", ".js"):
            if name.lower() not in ("index", "main", "_app", "_layout", "layout"):
                kebab = camel_to_kebab(name)
                if kebab not in page_seen:
                    pages.append(Page(name=kebab))
                    page_seen.add(kebab)
        elif entry.is_dir() and not name.startswith(("_", ".")):
            kebab = camel_to_kebab(name)
            if kebab not in page_seen:
                pages.append(Page(name=kebab))
                page_seen.add(kebab)
    return pages


def _extract_web_pages(root: Path) -> list[Page]:
    """Extract page names from src/pages/, src/views/, etc."""
    page_seen: set[str] = set()
    for pages_dir in ("src/pages", "src/views", "pages", "views", "src/routes"):
        pdir = root / pages_dir
        if pdir.is_dir():
            return _scan_pages_dir(pdir, page_seen)
    return []


def scan_web_frontend(root: Path, spec: DoqlSpec) -> None:
    """Detect web frontend (React, Vue, Svelte, plain HTML)."""
    framework = _detect_web_framework(root)
    pages = _extract_web_pages(root)

    # Check for static HTML sites
    if not framework and (root / "index.html").exists():
        framework = "static"

    if framework:
        pwa = (
            (root / "public" / "manifest.json").exists()
            or (root / "public" / "manifest.webmanifest").exists()
            or (root / "manifest.json").exists()
        )

        iface = Interface(
            name="web",
            type="spa",
            framework=framework,
            pages=pages,
            pwa=pwa,
        )
        spec.interfaces.append(iface)
