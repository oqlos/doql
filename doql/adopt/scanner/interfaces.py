"""Interface scanning — API, Web, Mobile, Desktop detection."""
from __future__ import annotations

import json
from pathlib import Path

from ...parsers.models import DoqlSpec, Interface, Page
from .utils import camel_to_kebab


def scan_interfaces(root: Path, spec: DoqlSpec) -> None:
    """Detect service interfaces from project structure."""
    _scan_python_api(root, spec)
    _scan_python_cli(root, spec)
    _scan_web_frontend(root, spec)
    _scan_mobile(root, spec)
    _scan_desktop(root, spec)


# ─────────────────────────────────────────────────────────────────────────────
# Python API Detection (FastAPI, Flask, Django)
# ─────────────────────────────────────────────────────────────────────────────

def _detect_framework_from_pyproject(pyproj: Path) -> str | None:
    """Detect web framework from pyproject.toml dependencies."""
    if not pyproj.exists():
        return None
    text = pyproj.read_text().lower()
    if "fastapi" in text:
        return "fastapi"
    if "flask" in text:
        return "flask"
    if "django" in text:
        return "django"
    return None


def _detect_framework_from_main_py(main_py: Path) -> str | None:
    """Detect web framework from main.py imports."""
    if not main_py.exists():
        return None
    try:
        text = main_py.read_text()
    except OSError:
        return None
    if "FastAPI" in text or "from fastapi" in text:
        return "fastapi"
    if "Flask" in text:
        return "flask"
    return None


def _find_api_main_file(root: Path) -> Path | None:
    """Find API main file in common locations."""
    api_dirs = ["api", "app", "src/api", "apps/api"]
    
    # Also check inside package directories (e.g. oqlos/api/main.py)
    for child in root.iterdir():
        if child.is_dir() and not child.name.startswith((".", "_")):
            if child.name not in ("venv", ".venv", "node_modules", "dist", "build", "tests"):
                api_dirs.append(f"{child.name}/api")

    for d in api_dirs:
        candidate = root / d / "main.py"
        if candidate.exists():
            return candidate
        candidate = root / d / "app.py"
        if candidate.exists():
            return candidate
    return None


def _has_api_entry_point(pyproj: Path) -> bool:
    """Check if pyproject.toml has api/server entry point."""
    if not pyproj.exists():
        return False
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]
    try:
        with open(pyproj, "rb") as f:
            data = tomllib.load(f)
        scripts = data.get("project", {}).get("scripts", {})
        for name in scripts.keys():
            if "server" in name or "api" in name:
                return True
    except Exception:
        pass
    return False


def _detect_api_auth(spec: DoqlSpec) -> str | None:
    """Detect authentication type from env vars."""
    for ref in spec.env_refs:
        if "JWT" in ref.upper() or "SECRET" in ref.upper():
            return "jwt"
    return None


def _detect_api_port(spec: DoqlSpec) -> str:
    """Detect API port from env vars."""
    for ref in spec.env_refs:
        if "PORT" in ref.upper() and "API" in ref.upper():
            return f"env.{ref}"
        if ref.upper() in ("PORT", "WEB_PORT", "SERVER_PORT"):
            return f"env.{ref}"
    return "8000"


def _scan_python_api(root: Path, spec: DoqlSpec) -> None:
    """Detect Python API (FastAPI, Flask, Django).

    A project is considered to expose an API only when there is *evidence*
    of a serving entry point — not just a transitive dependency in
    ``pyproject.toml``. Evidence is one of:

    * an ``api/main.py`` / ``api/app.py`` (or ``<pkg>/api/main.py``) file,
    * a project script entry point whose name contains ``api``/``server``,
    * a top-level ``main.py`` that imports a known web framework.
    """
    pyproj = root / "pyproject.toml"
    framework_dep = _detect_framework_from_pyproject(pyproj)
    
    api_main = _find_api_main_file(root)
    has_entry_point = _has_api_entry_point(pyproj)
    main_py_framework = _detect_framework_from_main_py(root / "main.py")

    has_evidence = bool(api_main or has_entry_point or main_py_framework)
    if not has_evidence:
        return

    framework = framework_dep or main_py_framework or "fastapi"
    auth = _detect_api_auth(spec)

    iface = Interface(
        name="api",
        type="rest",
        framework=framework,
    )
    if auth:
        iface.auth = {"type": auth}
    spec.interfaces.append(iface)


# ─────────────────────────────────────────────────────────────────────────────
# Python CLI Detection
# ─────────────────────────────────────────────────────────────────────────────

def _scan_python_cli(root: Path, spec: DoqlSpec) -> None:
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
        framework = "click" if "click" in pyproj.read_text().lower() else "argparse"
        iface = Interface(
            name="cli",
            type="cli",
            framework=framework,
        )
        # Add entry point as page (command name)
        iface.pages.append(Page(name=name))
        spec.interfaces.append(iface)
        return  # Only add one CLI interface


# ─────────────────────────────────────────────────────────────────────────────
# Web Frontend Detection
# ─────────────────────────────────────────────────────────────────────────────

def _detect_web_framework(root: Path) -> str | None:
    """Detect web framework from package.json."""
    pkg = root / "package.json"
    if not pkg.exists():
        return None
    try:
        data = json.loads(pkg.read_text())
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

        if "react" in deps or "@vitejs/plugin-react" in deps:
            return "react"
        if "vue" in deps or "@vitejs/plugin-vue" in deps:
            return "vue"
        if "svelte" in deps:
            return "svelte"
    except (json.JSONDecodeError, OSError):
        pass
    return None


def _extract_web_pages(root: Path) -> list[Page]:
    """Extract page names from src/pages/, src/views/, etc."""
    pages: list[Page] = []
    page_seen: set[str] = set()
    
    for pages_dir in ("src/pages", "src/views", "pages", "views", "src/routes"):
        pdir = root / pages_dir
        if pdir.is_dir():
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
            break
    return pages


def _scan_web_frontend(root: Path, spec: DoqlSpec) -> None:
    """Detect web frontend (React, Vue, Svelte, plain HTML)."""
    framework = _detect_web_framework(root)
    pages = _extract_web_pages(root)

    # Check for static HTML sites
    if not framework and (root / "index.html").exists():
        framework = "static"

    if framework:
        pwa = (root / "public" / "manifest.json").exists() or \
              (root / "public" / "manifest.webmanifest").exists() or \
              (root / "manifest.json").exists()

        iface = Interface(
            name="web",
            type="spa",
            framework=framework,
            pages=pages,
            pwa=pwa,
        )
        spec.interfaces.append(iface)


# ─────────────────────────────────────────────────────────────────────────────
# Mobile Detection
# ─────────────────────────────────────────────────────────────────────────────

def _scan_mobile(root: Path, spec: DoqlSpec) -> None:
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


# ─────────────────────────────────────────────────────────────────────────────
# Desktop Detection
# ─────────────────────────────────────────────────────────────────────────────

def _scan_desktop(root: Path, spec: DoqlSpec) -> None:
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
