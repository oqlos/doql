"""End-to-end tests: doql build on every example + every scaffold template."""
from __future__ import annotations

import pathlib
import py_compile
import shutil
import subprocess

import pytest


ROOT = pathlib.Path(__file__).parent.parent
DOQL_BIN = ROOT / "venv" / "bin" / "doql"
EXAMPLES = [
    "asset-management",
    "calibration-lab",
    "document-generator",
    "iot-fleet",
    "kiosk-station",
]
TEMPLATES = ["minimal", "saas-multi-tenant", "calibration-lab", "iot-fleet"]


def _run_doql(*args: str) -> subprocess.CompletedProcess:
    """Run the doql CLI and return the completed process."""
    bin_path = DOQL_BIN if DOQL_BIN.exists() else "doql"
    return subprocess.run(
        [str(bin_path), *args],
        capture_output=True, text=True, cwd=ROOT,
    )


def _compile_all_py(root: pathlib.Path) -> int:
    """Compile every .py file under *root*. Returns count. Raises on syntax error."""
    count = 0
    for py in root.rglob("*.py"):
        py_compile.compile(str(py), doraise=True)
        count += 1
    return count


# ─── Build every example ───────────────────────────────────────

@pytest.mark.parametrize("example", EXAMPLES)
def test_build_example(example, tmp_path):
    src_example = ROOT / "examples" / example
    if not src_example.exists():
        pytest.skip(f"Example not found: {example}")

    # Copy to tmp_path so parallel runs don't collide
    work = tmp_path / example
    shutil.copytree(src_example, work, ignore=shutil.ignore_patterns("build", ".github"))

    result = _run_doql("-d", str(work), "build", "--force")
    assert result.returncode == 0, f"build failed: {result.stderr}"
    build_dir = work / "build"
    assert build_dir.is_dir()

    api_dir = build_dir / "api"
    if (api_dir / "models.py").exists():
        count = _compile_all_py(api_dir)
        assert count > 0, "expected at least one .py to compile"


# ─── Scaffold + build every template ───────────────────────────

@pytest.mark.parametrize("template", TEMPLATES)
def test_init_and_build_template(template, tmp_path):
    project = tmp_path / f"proj-{template}"

    init = _run_doql("init", "--template", template, str(project))
    assert init.returncode == 0, f"init failed: {init.stderr}"
    assert project.is_dir()
    assert (project / "app.doql").exists()

    # Use the .env.example as .env for the build
    env_example = project / ".env.example"
    if env_example.exists():
        (project / ".env").write_text(env_example.read_text())

    build = _run_doql("-d", str(project), "build", "--force")
    assert build.returncode == 0, f"build failed: {build.stderr}"

    api_dir = project / "build" / "api"
    if (api_dir / "models.py").exists():
        _compile_all_py(api_dir)


# ─── doql sync — lockfile diff detection ────────────────────────

def test_sync_no_changes_is_noop(tmp_path):
    """Two consecutive builds with identical spec → sync reports no changes."""
    project = tmp_path / "sync-test"
    _run_doql("init", "--template", "minimal", str(project))
    shutil.copy(project / ".env.example", project / ".env")
    _run_doql("-d", str(project), "build", "--force")

    lock = project / "doql.lock"
    assert lock.exists()
    import json
    lock_data = json.loads(lock.read_text())
    assert lock_data["version"] == "2"
    assert "sections" in lock_data

    sync = _run_doql("-d", str(project), "sync")
    assert sync.returncode == 0
    assert "No changes detected" in sync.stdout


# ─── List templates ────────────────────────────────────────────

def test_list_templates_includes_all():
    result = _run_doql("init", "-", "--list-templates")
    assert result.returncode == 0
    for t in TEMPLATES:
        assert t in result.stdout
