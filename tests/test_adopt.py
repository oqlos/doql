"""Regression tests for ``doql adopt`` (project scanner + emitter).

These tests cover behaviour that has bitten real projects in
``/home/tom/github/semcod/`` and ``/home/tom/github/oqlos/``:

* JWT-authenticated APIs must not crash the renderer.
* Pydantic Request/Response classes must not pollute ``ENTITY`` blocks.
* Generic compose service names (``db``) must be normalised to engine type.
* ``api`` interface must require evidence beyond a transitive dependency.
* ``cmd_adopt`` must surface render failures via non-zero exit code.
"""
from __future__ import annotations

import argparse
import textwrap
from pathlib import Path

import pytest

from doql.adopt.scanner import scan_project
from doql.adopt.emitter import emit_css
from doql.cli.commands.adopt import cmd_adopt


# ── helpers ───────────────────────────────────────────────────


def _write(root: Path, rel: str, body: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(body).lstrip())
    return p


def _pyproject(name: str = "x", deps: str = '"fastapi"') -> str:
    return f"""\
        [project]
        name = "{name}"
        version = "0.1.0"
        dependencies = [{deps}]
    """


# ── 1. JWT auth bug ──────────────────────────────────────────


def test_jwt_secret_does_not_crash_renderer(tmp_path: Path) -> None:
    """Regression: scanner used to set ``iface.auth = 'jwt'`` (string), but
    the model declares ``auth: dict[str, Any]`` and the renderer calls
    ``.items()``. ``adopt`` would emit an empty file and still print success.
    """
    _write(tmp_path, "pyproject.toml", _pyproject())
    _write(tmp_path, "main.py", "from fastapi import FastAPI\napp = FastAPI()\n")
    _write(tmp_path, ".env", "JWT_SECRET=foo\n")

    spec = scan_project(tmp_path)

    api = next(i for i in spec.interfaces if i.name == "api")
    assert isinstance(api.auth, dict), "auth must remain a dict for the renderer"
    assert api.auth.get("type") == "jwt"

    out = tmp_path / "app.doql.css"
    emit_css(spec, out)
    assert out.stat().st_size > 0
    text = out.read_text()
    assert 'interface[type="api"]' in text
    assert "auth-type: jwt" in text


# ── 2. DTO filtering ─────────────────────────────────────────


def test_pydantic_dtos_are_excluded_from_entities(tmp_path: Path) -> None:
    """Pydantic ``XRequest`` / ``XResponse`` classes are API contracts, not
    persistent entities — they should not appear as ``ENTITY`` blocks.
    SQLAlchemy / SQLModel classes are always kept.
    """
    _write(tmp_path, "pyproject.toml", _pyproject())
    _write(tmp_path, "src/x/models.py", """\
        from pydantic import BaseModel
        from sqlalchemy.orm import DeclarativeBase

        class Base(DeclarativeBase): pass

        class User(Base):
            id: int

        class UserCreate(BaseModel):
            email: str

        class UserResponse(BaseModel):
            id: int

        class HealthResponse(BaseModel):
            status: str
    """)

    spec = scan_project(tmp_path)
    names = {e.name for e in spec.entities}

    assert "User" in names, "persistent SQLAlchemy entity must be kept"
    for dto in ("UserCreate", "UserResponse", "HealthResponse"):
        assert dto not in names, f"{dto} is a DTO and must be filtered out"


# ── 3. Generic DB names ──────────────────────────────────────


def test_generic_db_service_name_is_normalised(tmp_path: Path) -> None:
    """``services.db`` in compose should yield ``database[name="postgres"]``,
    not ``database[name="db"]`` — keeps generated specs self-documenting.
    """
    _write(tmp_path, "docker-compose.yml", """\
        services:
          db:
            image: postgres:16
          cache:
            image: redis:7
    """)

    spec = scan_project(tmp_path)
    names = {db.name: db.type for db in spec.databases}
    assert names.get("postgres") == "postgresql"
    assert names.get("cache") == "redis"
    assert "db" not in names


# ── 4. Stricter API detection ────────────────────────────────


def test_fastapi_dependency_alone_does_not_create_api_interface(tmp_path: Path) -> None:
    """A transitive ``fastapi`` dep (e.g. for a CLI that imports it for type
    hints) used to falsely trigger an ``interface[type="api"]`` block.
    """
    _write(tmp_path, "pyproject.toml", _pyproject(deps='"fastapi", "click"'))
    # NB: no main.py, no api/, no *-server entry point
    spec = scan_project(tmp_path)
    api_ifaces = [i for i in spec.interfaces if i.name == "api"]
    assert api_ifaces == [], "API interface must require serving evidence"


def test_fastapi_with_main_py_creates_api(tmp_path: Path) -> None:
    """``main.py`` importing FastAPI is sufficient evidence."""
    _write(tmp_path, "pyproject.toml", _pyproject())
    _write(tmp_path, "main.py", "from fastapi import FastAPI\napp = FastAPI()\n")
    spec = scan_project(tmp_path)
    api = [i for i in spec.interfaces if i.name == "api"]
    assert len(api) == 1
    assert api[0].framework == "fastapi"


def test_api_entry_point_in_scripts_creates_api(tmp_path: Path) -> None:
    """A ``scripts.x-server = "..."`` entry point counts as evidence."""
    _write(tmp_path, "pyproject.toml", """\
        [project]
        name = "x"
        version = "0.1.0"
        dependencies = ["fastapi"]
        [project.scripts]
        "x-server" = "x:main"
    """)
    spec = scan_project(tmp_path)
    api = [i for i in spec.interfaces if i.name == "api"]
    assert len(api) == 1


# ── 5. cmd_adopt error handling ──────────────────────────────


def _make_args(target: Path, output: str | None = None, force: bool = True) -> argparse.Namespace:
    return argparse.Namespace(target=str(target), output=output, force=force)


def test_cmd_adopt_returns_zero_on_success(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", _pyproject())
    _write(tmp_path, "main.py", "from fastapi import FastAPI\napp = FastAPI()\n")

    rc = cmd_adopt(_make_args(tmp_path))
    assert rc == 0
    out = tmp_path / "app.doql.css"
    assert out.exists() and out.stat().st_size > 0


def test_cmd_adopt_returns_nonzero_on_render_failure(tmp_path: Path, monkeypatch) -> None:
    """If the emitter raises, ``cmd_adopt`` must return non-zero and not
    print a misleading ``✅ Written`` line.
    """
    _write(tmp_path, "pyproject.toml", _pyproject())

    def _boom(*_a, **_kw):
        raise RuntimeError("simulated render failure")

    monkeypatch.setattr("doql.adopt.emitter.emit_spec", _boom)
    rc = cmd_adopt(_make_args(tmp_path))
    assert rc == 1


def test_cmd_adopt_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    _write(tmp_path, "pyproject.toml", _pyproject())
    (tmp_path / "app.doql.css").write_text("# pre-existing\n")
    rc = cmd_adopt(_make_args(tmp_path, force=False))
    assert rc == 1, "must refuse to clobber without --force"
    assert (tmp_path / "app.doql.css").read_text() == "# pre-existing\n"


def test_cmd_adopt_rejects_non_directory(tmp_path: Path, capsys) -> None:
    target = tmp_path / "does-not-exist"
    rc = cmd_adopt(_make_args(target))
    assert rc == 1


# ── 6. Workflow detection (Makefile / Taskfile.yml) ──────────


def test_makefile_targets_become_workflows(tmp_path: Path) -> None:
    """Existing ``Makefile`` automation must survive the round-trip through
    ``app.doql.css`` as ``workflow[name="..."]`` blocks.
    """
    _write(tmp_path, "Makefile", (
        ".PHONY: all build test deploy help\n"
        "\n"
        "all: build test\n"
        "\n"
        "build:\n"
        "\t@echo building\n"
        "\tpython -m build\n"
        "\n"
        "test:\n"
        "\tpytest -q\n"
        "\n"
        "deploy:\n"
        "\tdocker compose up -d\n"
        "\n"
        "help:\n"
        "\t@echo 'usage: make <target>'\n"
    ))

    spec = scan_project(tmp_path)
    names = {w.name for w in spec.workflows}

    # Meaningful targets captured
    assert {"build", "test", "deploy"} <= names
    # Meta targets filtered out
    assert "all" not in names
    assert "help" not in names
    assert "PHONY" not in names and ".PHONY" not in names

    build = next(w for w in spec.workflows if w.name == "build")
    assert build.trigger == "manual"
    cmds = [s.params["cmd"] for s in build.steps]
    assert "echo building" in cmds  # @-prefix stripped
    assert "python -m build" in cmds


def test_makefile_workflows_round_trip_to_css(tmp_path: Path) -> None:
    _write(tmp_path, "Makefile", "lint:\n\truff check .\n")
    spec = scan_project(tmp_path)
    out = tmp_path / "app.doql.css"
    emit_css(spec, out)
    text = out.read_text()
    assert 'workflow[name="lint"]' in text
    assert "ruff check ." in text


def test_taskfile_yml_tasks_become_workflows(tmp_path: Path) -> None:
    """Tasks from a ``Taskfile.yml`` must also be promoted to workflows."""
    _write(tmp_path, "Taskfile.yml", (
        "version: '1'\n"
        "name: demo\n"
        "tasks:\n"
        "  install:\n"
        "    desc: install deps\n"
        "    cmds:\n"
        "      - pip install -e .\n"
        "  serve:\n"
        "    desc: run api\n"
        "    cmds:\n"
        "      - uvicorn app:app\n"
    ))
    spec = scan_project(tmp_path)
    names = {w.name for w in spec.workflows}
    assert {"install", "serve"} <= names

    serve = next(w for w in spec.workflows if w.name == "serve")
    assert [s.params["cmd"] for s in serve.steps] == ["uvicorn app:app"]


def test_dependency_only_targets_emit_depend_steps(tmp_path: Path) -> None:
    """Regression: ``install: install-backend install-frontend`` (no body)
    used to produce an empty ``workflow[name="install"]`` block with only
    ``trigger: manual``. Deps must be preserved as explicit ``depend`` steps
    so the workflow carries meaningful information.
    """
    _write(tmp_path, "Makefile", (
        "install: install-backend install-frontend ## Install everything\n"
        "\n"
        "install-backend:\n"
        "\t@echo backend\n"
        "\n"
        "install-frontend:\n"
        "\t@echo frontend\n"
        "\n"
        "# Aliases\n"
        "up: dev\n"
        "\n"
        "dev:\n"
        "\tuvicorn app:app\n"
    ))
    spec = scan_project(tmp_path)

    install = next(w for w in spec.workflows if w.name == "install")
    assert len(install.steps) == 2
    assert install.steps[0].action == "depend"
    assert install.steps[0].params == {"target": "install-backend"}
    assert install.steps[1].params == {"target": "install-frontend"}

    up = next(w for w in spec.workflows if w.name == "up")
    assert len(up.steps) == 1
    assert up.steps[0].action == "depend"
    assert up.steps[0].params == {"target": "dev"}


def test_empty_target_without_deps_is_skipped(tmp_path: Path) -> None:
    """A truly empty target (no deps, no body) has no useful data \u2014 drop it."""
    _write(tmp_path, "Makefile", "noop:\n\nreal:\n\techo hi\n")
    spec = scan_project(tmp_path)
    names = {w.name for w in spec.workflows}
    assert names == {"real"}


def test_makefile_variable_assignments_are_not_workflows(tmp_path: Path) -> None:
    """Regression: ``VAR := value`` / ``VAR ?= value`` / ``VAR = value`` must
    not be promoted to workflows. Originally the target regex matched the
    ``:`` in ``:=`` and produced bogus entries like ``workflow[name="PYTHON"]``.
    """
    _write(tmp_path, "Makefile", (
        "PYTHON := python3\n"
        "PIP ?= pip\n"
        "GREEN = \\033[0;32m\n"
        "SHELL := /bin/bash\n"
        "VERSION = 1.0.0\n"
        "\n"
        "build:\n"
        "\t$(PYTHON) -m build\n"
    ))
    spec = scan_project(tmp_path)
    names = {w.name for w in spec.workflows}
    assert names == {"build"}
    for forbidden in ("PYTHON", "PIP", "GREEN", "SHELL", "VERSION"):
        assert forbidden not in names, f"{forbidden} is a variable, not a target"


def test_workflows_are_deduplicated_across_makefile_and_taskfile(tmp_path: Path) -> None:
    """A project may have both \u2014 the first file wins so we don't emit two
    ``workflow[name="build"]`` blocks.
    """
    _write(tmp_path, "Makefile", "build:\n\tmake-build\n")
    _write(tmp_path, "Taskfile.yml", (
        "version: '1'\nname: x\ntasks:\n  build:\n    cmds:\n      - taskfile-build\n"
    ))
    spec = scan_project(tmp_path)
    build_ws = [w for w in spec.workflows if w.name == "build"]
    assert len(build_ws) == 1, "build workflow must not be duplicated"
    # Makefile runs first, so its command wins.
    assert build_ws[0].steps[0].params["cmd"] == "make-build"
