"""Project scanner — detects services, frameworks, databases, deploy patterns.

Walks a project directory and builds a DoqlSpec by detecting:
- pyproject.toml / package.json → app metadata
- Python FastAPI/Flask → API interface
- React/Vue/Svelte → web interface
- Dockerfile / docker-compose.yml → deploy
- .env → env_refs
- models.py / schemas → entities (basic)
- Makefile / Taskfile.yml → variables
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from ..parsers.models import (
    Database, Deploy, DoqlSpec, Entity, EntityField, Integration,
    Interface, Page, Role, Environment,
)


def scan_project(root: str | Path) -> DoqlSpec:
    """Scan *root* directory and return a reverse-engineered DoqlSpec."""
    root = Path(root).resolve()
    spec = DoqlSpec()

    _scan_metadata(root, spec)
    _scan_env(root, spec)
    _scan_databases(root, spec)
    _scan_interfaces(root, spec)
    _scan_deploy(root, spec)
    _scan_environments(root, spec)
    _scan_integrations(root, spec)
    _scan_entities(root, spec)
    _scan_roles(root, spec)

    return spec


# ── Metadata ──────────────────────────────────────────────────

def _scan_metadata(root: Path, spec: DoqlSpec) -> None:
    """Extract app name, version, domain from config files."""
    pyproj = root / "pyproject.toml"
    if pyproj.exists():
        _parse_pyproject(pyproj, spec)

    pkg = root / "package.json"
    if pkg.exists():
        _parse_package_json(pkg, spec)

    goal = root / "goal.yaml"
    if goal.exists():
        _parse_goal_yaml(goal, spec)

    version_file = root / "VERSION"
    if version_file.exists():
        v = version_file.read_text().strip()
        if v:
            spec.version = v


def _parse_pyproject(path: Path, spec: DoqlSpec) -> None:
    """Extract metadata from pyproject.toml (stdlib tomllib)."""
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(path, "rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    spec.app_name = project.get("name", spec.app_name)
    spec.version = project.get("version", spec.version)

    # Detect entry points (CLI scripts)
    scripts = project.get("scripts", {})
    for name, ep in scripts.items():
        if "api" in name or "server" in name:
            # Likely an API service entry point
            pass  # handled by interface scan


def _parse_package_json(path: Path, spec: DoqlSpec) -> None:
    """Extract metadata from package.json."""
    data = json.loads(path.read_text())
    spec.app_name = data.get("name", spec.app_name)
    spec.version = data.get("version", spec.version)


def _parse_goal_yaml(path: Path, spec: DoqlSpec) -> None:
    """Extract metadata from goal.yaml if present."""
    try:
        import yaml
        data = yaml.safe_load(path.read_text()) or {}
        if "name" in data:
            spec.app_name = data["name"]
    except Exception:
        pass


# ── Environment variables ─────────────────────────────────────

def _scan_env(root: Path, spec: DoqlSpec) -> None:
    """Detect .env files and extract variable names."""
    for name in (".env", ".env.example", ".env.local"):
        env_path = root / name
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key = line.split("=", 1)[0].strip()
                    if key:
                        spec.env_refs.append(key)
            break  # use first found


# ── Databases ─────────────────────────────────────────────────

_GENERIC_DB_NAMES = {"db", "database", "pg", "sql", "data"}


def _db_name(svc_name: str, db_type: str) -> str:
    """Return a meaningful DB block name. Generic compose service names like
    ``db`` / ``database`` are replaced with the concrete engine type so the
    generated ``.doql.css`` is self-documenting."""
    if svc_name.lower() in _GENERIC_DB_NAMES:
        return db_type
    return svc_name


def _scan_databases(root: Path, spec: DoqlSpec) -> None:
    """Detect database setup from docker-compose, .env, config files."""
    compose = _find_compose(root)
    if compose:
        data = _load_yaml(compose)
        if data:
            services = data.get("services", {})
            for svc_name, svc in services.items():
                image = svc.get("image", "")
                if "postgres" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "postgres"), type="postgresql",
                        url=f"env.DATABASE_URL",
                    ))
                elif "mysql" in image or "mariadb" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "mysql"), type="mysql",
                        url="env.DATABASE_URL",
                    ))
                elif "redis" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "redis"), type="redis",
                        url="env.REDIS_URL",
                    ))
                elif "mongo" in image:
                    spec.databases.append(Database(
                        name=_db_name(svc_name, "mongodb"), type="mongodb",
                        url="env.MONGO_URL",
                    ))

    # Check for SQLite references in .env
    for ref in spec.env_refs:
        if "SQLITE" in ref.upper() or "DB_PATH" in ref.upper():
            if not any(db.type == "sqlite" for db in spec.databases):
                spec.databases.append(Database(
                    name="main", type="sqlite",
                    url=f"env.{ref}",
                ))


# ── Interfaces (API, Web, Mobile, Desktop) ────────────────────

def _scan_interfaces(root: Path, spec: DoqlSpec) -> None:
    """Detect service interfaces from project structure."""
    _scan_python_api(root, spec)
    _scan_python_cli(root, spec)
    _scan_web_frontend(root, spec)
    _scan_mobile(root, spec)
    _scan_desktop(root, spec)


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
    framework_dep = None
    has_entry_point = False

    if pyproj.exists():
        text = pyproj.read_text().lower()
        if "fastapi" in text:
            framework_dep = "fastapi"
        elif "flask" in text:
            framework_dep = "flask"
        elif "django" in text:
            framework_dep = "django"

    # Check for common API directories/files
    api_dirs = ["api", "app", "src/api", "apps/api"]
    api_main = None
    # Also check inside package directories (e.g. oqlos/api/main.py)
    for child in root.iterdir():
        if child.is_dir() and not child.name.startswith((".","_")) and \
           child.name not in ("venv", ".venv", "node_modules", "dist", "build", "tests"):
            api_dirs.append(f"{child.name}/api")

    for d in api_dirs:
        candidate = root / d / "main.py"
        if candidate.exists():
            api_main = candidate
            break
        candidate = root / d / "app.py"
        if candidate.exists():
            api_main = candidate
            break

    # Check for entry points in pyproject.toml
    if pyproj.exists():
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]
        with open(pyproj, "rb") as f:
            data = tomllib.load(f)
        scripts = data.get("project", {}).get("scripts", {})
        for name, _ep in scripts.items():
            if "server" in name or "api" in name:
                has_entry_point = True
                break

    # Top-level main.py with web framework import counts as evidence too
    main_py = root / "main.py"
    main_py_framework = None
    if main_py.exists():
        try:
            text = main_py.read_text()
        except OSError:
            text = ""
        if "FastAPI" in text or "from fastapi" in text:
            main_py_framework = "fastapi"
        elif "Flask" in text:
            main_py_framework = "flask"

    has_evidence = bool(api_main or has_entry_point or main_py_framework)
    if not has_evidence:
        return

    framework = framework_dep or main_py_framework or "fastapi"
    port = "8000"  # noqa: F841 — reserved for future port detection

    # Detect port from .env or docker
    for ref in spec.env_refs:
        if "PORT" in ref.upper() and "API" in ref.upper():
            port = f"env.{ref}"
            break
        if ref.upper() in ("PORT", "WEB_PORT", "SERVER_PORT"):
            port = f"env.{ref}"

    auth = None
    for ref in spec.env_refs:
        if "JWT" in ref.upper() or "SECRET" in ref.upper():
            auth = "jwt"
            break

    iface = Interface(
        name="api",
        type="rest",
        framework=framework or "fastapi",
    )
    if auth:
        iface.auth = {"type": auth}
    spec.interfaces.append(iface)


def _scan_python_cli(root: Path, spec: DoqlSpec) -> None:
    """Detect Python CLI tools (click, argparse entry points)."""
    pyproj = root / "pyproject.toml"
    if not pyproj.exists():
        return

    try:
        import tomllib
    except ImportError:
        import tomli as tomllib  # type: ignore[no-redef]

    with open(pyproj, "rb") as f:
        data = tomllib.load(f)

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


def _scan_web_frontend(root: Path, spec: DoqlSpec) -> None:
    """Detect web frontend (React, Vue, Svelte, plain HTML)."""
    # Check package.json for framework
    pkg = root / "package.json"
    framework = None
    pages: list[Page] = []

    if pkg.exists():
        data = json.loads(pkg.read_text())
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

        if "react" in deps or "@vitejs/plugin-react" in deps:
            framework = "react"
        elif "vue" in deps or "@vitejs/plugin-vue" in deps:
            framework = "vue"
        elif "svelte" in deps:
            framework = "svelte"

    # Check for src/pages/ or src/views/ directory
    page_seen: set[str] = set()
    for pages_dir in ("src/pages", "src/views", "pages", "views", "src/routes"):
        pdir = root / pages_dir
        if pdir.is_dir():
            for entry in sorted(pdir.iterdir()):
                name = entry.stem
                if entry.is_file() and entry.suffix in (".jsx", ".tsx", ".vue", ".svelte", ".js"):
                    if name.lower() not in ("index", "main", "_app", "_layout", "layout"):
                        kebab = _camel_to_kebab(name)
                        if kebab not in page_seen:
                            pages.append(Page(name=kebab))
                            page_seen.add(kebab)
                elif entry.is_dir() and not name.startswith(("_", ".")):
                    kebab = _camel_to_kebab(name)
                    if kebab not in page_seen:
                        pages.append(Page(name=kebab))
                        page_seen.add(kebab)
            break

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


def _scan_mobile(root: Path, spec: DoqlSpec) -> None:
    """Detect mobile targets."""
    # Check for React Native, Flutter, or PWA mobile
    pkg = root / "package.json"
    if pkg.exists():
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

    # Check for mobile/ subdirectory
    if (root / "mobile").is_dir():
        spec.interfaces.append(Interface(
            name="mobile", type="pwa",
        ))


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
        data = json.loads(pkg.read_text())
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "electron" in deps:
            spec.interfaces.append(Interface(
                name="desktop", type="electron",
                framework="electron",
            ))


# ── Deploy ────────────────────────────────────────────────────

def _scan_deploy(root: Path, spec: DoqlSpec) -> None:
    """Detect deployment infrastructure."""
    compose = _find_compose(root)
    has_dockerfile = _find_dockerfiles(root)
    has_quadlet = (root / "infra" / "quadlet").is_dir() or \
                  (root / "deploy" / "quadlet").is_dir()
    has_ansible = any((root / d).is_dir() for d in ("ansible", "deploy/ansible", "infra/ansible"))
    has_makefile = (root / "Makefile").exists()

    deploy = Deploy()

    if compose:
        deploy.target = "docker-compose"
        deploy.config["compose_file"] = str(compose.relative_to(root))
    elif has_dockerfile:
        deploy.target = "docker"
    elif has_quadlet:
        deploy.target = "podman-quadlet"
    elif has_makefile:
        deploy.target = "makefile"

    if has_quadlet:
        deploy.config["quadlet"] = True
    if has_ansible:
        deploy.config["ansible"] = True

    # Detect rootless podman
    for ref in spec.env_refs:
        if "ROOTLESS" in ref.upper():
            deploy.rootless = True
            break

    # Detect services from docker-compose
    if compose:
        data = _load_yaml(compose)
        if data:
            services = data.get("services", {})
            for svc_name, svc in services.items():
                image = svc.get("image", "")
                build = svc.get("build")
                ports = svc.get("ports", [])
                # Skip databases (already scanned)
                if any(db in image for db in ("postgres", "mysql", "redis", "mongo")):
                    continue
                container = {"name": svc_name}
                if image:
                    container["image"] = image
                if build:
                    container["build"] = build if isinstance(build, str) else build.get("context", ".")
                if ports:
                    container["ports"] = ports
                deploy.containers.append(container)

    spec.deploy = deploy


# ── Environments ──────────────────────────────────────────────

def _scan_environments(root: Path, spec: DoqlSpec) -> None:
    """Detect environments from .env files and docker-compose variants."""
    # Local environment (always present)
    local_env = Environment(name="local")
    if (root / ".env").exists():
        local_env.env_file = ".env"
    local_env.runtime = spec.deploy.target if spec.deploy else "docker-compose"
    spec.environments.append(local_env)

    # Detect staging/prod from .env.* files
    for env_file in sorted(root.glob(".env.*")):
        name = env_file.name.split(".", 2)[-1]  # .env.staging → staging
        if name in ("example", "local", "docker", "test", "bak"):
            continue
        env = Environment(name=name, env_file=env_file.name)
        env.runtime = spec.deploy.target if spec.deploy else "docker-compose"

        # Check for ssh_host in env vars
        for ref in spec.env_refs:
            if name.upper() in ref.upper() and "HOST" in ref.upper():
                env.ssh_host = f"env.{ref}"
                break
        spec.environments.append(env)

    # Detect from docker-compose variant files
    compose_patterns = [
        ("dev", ["docker-compose.dev.yml", "docker/docker-compose.dev.yml",
                  "infra/docker/dev/docker-compose.dev.yml"]),
        ("staging", ["docker-compose.staging.yml", "docker/docker-compose.staging.yml"]),
        ("prod", ["docker-compose.prod.yml", "docker/docker-compose.prod.yml",
                   "infra/docker/prod/docker-compose.prod.yml"]),
    ]
    for env_name, paths in compose_patterns:
        if any(e.name == env_name for e in spec.environments):
            continue
        for p in paths:
            if (root / p).exists():
                env = Environment(name=env_name, runtime="docker-compose")
                env_file = root / f".env.{env_name}"
                if env_file.exists():
                    env.env_file = env_file.name
                spec.environments.append(env)
                break


# ── Integrations ──────────────────────────────────────────────

def _scan_integrations(root: Path, spec: DoqlSpec) -> None:
    """Detect external integrations from .env and code."""
    env_text = " ".join(spec.env_refs).upper()

    if "SMTP" in env_text or "EMAIL" in env_text or "MAIL" in env_text:
        spec.integrations.append(Integration(name="email", type="smtp"))

    if "SLACK" in env_text:
        spec.integrations.append(Integration(name="slack", type="webhook"))

    if "STRIPE" in env_text:
        spec.integrations.append(Integration(name="stripe", type="payment"))

    if "S3" in env_text or "MINIO" in env_text or "STORAGE" in env_text:
        spec.integrations.append(Integration(name="storage", type="s3"))

    if "MQTT" in env_text:
        spec.integrations.append(Integration(name="mqtt", type="mqtt"))

    if "MODBUS" in env_text:
        spec.integrations.append(Integration(name="modbus", type="hardware"))

    if "NLP" in env_text:
        spec.integrations.append(Integration(name="nlp", type="api"))

    if "GITHUB" in env_text:
        spec.integrations.append(Integration(name="github", type="scm"))


# ── Entities (basic detection from Python models) ─────────────

def _scan_entities(root: Path, spec: DoqlSpec) -> None:
    """Detect entities from Python models / schemas or SQL files."""
    # Check for models.py / schemas.py in common locations
    model_files: list[Path] = []
    for pattern in ("**/models.py", "**/schemas.py", "**/models/*.py"):
        model_files.extend(root.glob(pattern))

    seen: set[str] = set()
    for mf in model_files:
        if ".venv" in str(mf) or "venv" in str(mf) or "node_modules" in str(mf):
            continue
        _extract_entities_from_python(mf, spec, seen)

    # Check SQL init files
    for sql in root.rglob("*.sql"):
        if ".venv" in str(sql) or "venv" in str(sql):
            continue
        _extract_entities_from_sql(sql, spec, seen)


# Suffixes that indicate a class is a transient API DTO rather than a
# persistent domain entity. We strip these from the candidate pool so that
# generated specs stay focused on the data model the user actually owns.
_DTO_SUFFIXES = (
    "Request", "Response", "Result", "Create", "Update", "Patch",
    "Delete", "In", "Out", "Schema", "DTO", "Dto", "Params", "Query",
    "Payload", "Body", "Form", "Reply",
)

# SQLAlchemy / SQLModel / Django bases imply a persistent entity even if the
# class name happens to end with a DTO-looking suffix.
_PERSISTENT_BASES = (
    "Base", "db.Model", "SQLModel", "DeclarativeBase",
    "models.Model",
)

# Pydantic / generic bases produce *candidate* entities that we then filter by
# name to weed out request/response wrappers.
_DTO_BASES = ("BaseModel", "Model")


def _is_dto_name(name: str) -> bool:
    """Return True when *name* looks like an API DTO rather than an entity."""
    return any(name.endswith(suffix) for suffix in _DTO_SUFFIXES)


def _extract_entities_from_python(path: Path, spec: DoqlSpec, seen: set[str]) -> None:
    """Extract entity names from Python class definitions.

    Persistent classes (SQLAlchemy / SQLModel / Django) are always kept.
    Pydantic / dataclass-style classes are kept only when their name does
    *not* match a known DTO suffix (Request/Response/Result/...).
    """
    try:
        text = path.read_text()
    except Exception:
        return

    for m in re.finditer(r'class\s+(\w+)\s*\((.*?)\)\s*:', text):
        name = m.group(1)
        bases_raw = m.group(2)
        if name in seen or name.startswith("_"):
            continue

        # Tokenise the comma-separated base list so "Base" does not match
        # "BaseModel" (subclass of Pydantic), only an actual ``Base`` parent.
        base_tokens = {
            b.split("[", 1)[0].strip() for b in bases_raw.split(",") if b.strip()
        }
        is_persistent = bool(base_tokens & set(_PERSISTENT_BASES))
        is_dto_base = bool(base_tokens & set(_DTO_BASES))

        if not (is_persistent or is_dto_base):
            continue

        # Filter out obvious DTOs unless they inherit from a persistent base.
        if not is_persistent and _is_dto_name(name):
            continue

        entity = Entity(name=name)
        _extract_fields(text, m.end(), entity)
        spec.entities.append(entity)
        seen.add(name)


def _extract_fields(text: str, start: int, entity: Entity) -> None:
    """Extract field definitions from a Python class body."""
    # Get the indented block after the class definition
    lines = text[start:].split("\n")
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith('"""'):
            continue
        # Check if we're still in the class body (indented)
        if line and not line[0].isspace():
            break

        # Match: field_name: type = ...  or  field_name = Column(...)
        field_match = re.match(
            r'\s+(\w+)\s*:\s*([\w\[\], |]+)', stripped
        )
        if field_match:
            fname = field_match.group(1)
            ftype = field_match.group(2).strip()
            if fname.startswith("_") or fname in ("model_config", "Config"):
                continue
            ef = EntityField(name=fname, type=_normalize_python_type(ftype))
            if "Optional" in ftype or "None" in ftype:
                ef.required = False
            else:
                ef.required = True
            entity.fields.append(ef)

        # Match SQLAlchemy Column
        col_match = re.match(
            r'\s+(\w+)\s*=\s*Column\(\s*(\w+)', stripped
        )
        if col_match and not field_match:
            fname = col_match.group(1)
            ftype = col_match.group(2)
            if not fname.startswith("_"):
                entity.fields.append(EntityField(
                    name=fname,
                    type=_normalize_sqlalchemy_type(ftype),
                ))


def _extract_entities_from_sql(path: Path, spec: DoqlSpec, seen: set[str]) -> None:
    """Extract entities from CREATE TABLE statements."""
    try:
        text = path.read_text()
    except Exception:
        return

    for m in re.finditer(
        r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?["`]?(\w+)["`]?\s*\((.*?)\)',
        text, re.IGNORECASE | re.DOTALL
    ):
        table_name = m.group(1)
        if table_name in seen:
            continue
        entity = Entity(name=_snake_to_pascal(table_name))
        body = m.group(2)
        for col_match in re.finditer(
            r'["`]?(\w+)["`]?\s+([\w()]+)',
            body
        ):
            col_name = col_match.group(1)
            col_type = col_match.group(2)
            if col_name.upper() in ("PRIMARY", "FOREIGN", "UNIQUE", "CHECK",
                                     "CONSTRAINT", "INDEX", "KEY", "NOT",
                                     "DEFAULT", "IF", "CREATE", "TABLE",
                                     "REFERENCES", "ON", "CASCADE", "SET",
                                     "NULL", "RESTRICT", "NO", "ACTION"):
                continue
            entity.fields.append(EntityField(
                name=col_name,
                type=_normalize_sql_type(col_type),
            ))
        if entity.fields:
            spec.entities.append(entity)
            seen.add(table_name)


# ── Roles ─────────────────────────────────────────────────────

def _scan_roles(root: Path, spec: DoqlSpec) -> None:
    """Detect roles from env vars or code patterns."""
    env_text = " ".join(spec.env_refs).upper()
    if "ADMIN" in env_text or "ROLE" in env_text:
        spec.roles.append(Role(name="admin", permissions=["*"]))

    # Check for role definitions in SQL
    for sql in root.rglob("*.sql"):
        if ".venv" in str(sql) or "venv" in str(sql):
            continue
        try:
            text = sql.read_text().lower()
        except Exception:
            continue
        if "role" in text:
            for m in re.finditer(r"'(admin|user|editor|manager|operator|viewer)'", text):
                role_name = m.group(1)
                if not any(r.name == role_name for r in spec.roles):
                    spec.roles.append(Role(name=role_name))


# ── Helpers ───────────────────────────────────────────────────

def _find_compose(root: Path) -> Path | None:
    """Find docker-compose file."""
    candidates = [
        root / "docker-compose.yml",
        root / "docker-compose.yaml",
        root / "infra" / "docker-compose.yml",
        root / "infra" / "docker" / "prod" / "docker-compose.prod.yml",
        root / "infra" / "docker" / "dev" / "docker-compose.dev.yml",
        root / "docker" / "docker-compose.yml",
        root / "docker" / "docker-compose.dev.yml",
        root / "docker" / "docker-compose.prod.yml",
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


def _find_dockerfiles(root: Path) -> list[Path]:
    """Find all Dockerfiles."""
    results = []
    for p in root.rglob("Dockerfile*"):
        if ".venv" not in str(p) and "venv" not in str(p) and "node_modules" not in str(p):
            results.append(p)
    return results


def _load_yaml(path: Path) -> dict[str, Any] | None:
    """Safely load a YAML file."""
    try:
        import yaml
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return None


def _camel_to_kebab(name: str) -> str:
    """Convert CamelCase/PascalCase to kebab-case."""
    name = name.removesuffix("Page").removesuffix("View")
    s1 = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', name)
    return re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', s1).lower()


def _snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(w.capitalize() for w in name.split("_"))


def _normalize_python_type(t: str) -> str:
    """Normalize Python type annotations to DOQL types."""
    t = t.strip()
    t = re.sub(r'Optional\[(.+)\]', r'\1', t)
    mapping = {
        "str": "string", "int": "int", "float": "float",
        "bool": "bool", "datetime": "datetime", "date": "date",
        "UUID": "uuid", "uuid": "uuid", "dict": "json",
        "list": "json", "List": "json", "Dict": "json",
        "Any": "json",
    }
    return mapping.get(t, t)


def _normalize_sqlalchemy_type(t: str) -> str:
    """Normalize SQLAlchemy Column types to DOQL types."""
    mapping = {
        "String": "string", "Integer": "int", "Float": "float",
        "Boolean": "bool", "DateTime": "datetime", "Date": "date",
        "Text": "text", "JSON": "json", "UUID": "uuid",
    }
    return mapping.get(t, t.lower())


def _normalize_sql_type(t: str) -> str:
    """Normalize SQL column types to DOQL types."""
    t = t.upper()
    if "VARCHAR" in t or "TEXT" in t or "CHAR" in t:
        return "string"
    if "INT" in t:
        return "int"
    if "FLOAT" in t or "REAL" in t or "DOUBLE" in t or "NUMERIC" in t:
        return "float"
    if "BOOL" in t:
        return "bool"
    if "DATE" in t or "TIME" in t:
        return "datetime"
    if "UUID" in t:
        return "uuid"
    if "JSON" in t:
        return "json"
    if "BLOB" in t or "BYTE" in t:
        return "binary"
    return t.lower()
