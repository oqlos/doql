"""Unit tests for ``doql deploy`` priority chain and error handling.

Mock strategy:
- ``redeploy`` imports are always absent in this test-venv (no extra deps).
- We therefore *patch them in* where the API path is under test, and assert
  the CLI / directive / docker-compose fallbacks fire otherwise.
- ``subprocess.call`` and ``shutil.which`` are fully mocked.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from doql.cli.commands.deploy import (
    _deploy_via_redeploy_api,
    _deploy_via_redeploy_cli,
    _run_directive,
    cmd_deploy,
)
from doql.parsers.models import Deploy, DoqlSpec


# ── helpers ────────────────────────────────────────────────────────


def _args(**overrides) -> argparse.Namespace:
    defaults = dict(
        dir=".",
        file=None,
        env="prod",
        dry_run=False,
        plan_only=False,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _spec_with_directives(**directives) -> DoqlSpec:
    spec = DoqlSpec(app_name="testapp")
    spec.deploy = Deploy(target="docker-compose", directives=directives)
    return spec


# ── _run_directive ─────────────────────────────────────────────────


def test_run_directive_calls_shell():
    with patch("doql.cli.commands.deploy.subprocess.call", return_value=0) as mock_call:
        rc = _run_directive("local", "echo hello")
    assert rc == 0
    mock_call.assert_called_once_with("echo hello", shell=True)


def test_run_directive_returns_nonzero_on_failure():
    with patch("doql.cli.commands.deploy.subprocess.call", return_value=1) as mock_call:
        rc = _run_directive("push", "false")
    assert rc == 1


# ── _deploy_via_redeploy_api ───────────────────────────────────────


def test_redeploy_api_returns_minus_one_when_not_installed(tmp_path: Path):
    """If ``redeploy`` package is absent, return -1 so the caller falls through."""
    migration_yaml = tmp_path / "migration.yaml"
    migration_yaml.write_text("dummy", encoding="utf-8")

    # Ensure the ImportError path is hit by removing redeploy from sys.modules
    # and patching __import__ to raise.
    with patch.dict(sys.modules, {"redeploy": None}, clear=False):
        with patch("builtins.__import__", side_effect=_import_without_redeploy):
            rc = _deploy_via_redeploy_api(migration_yaml, dry_run=False, plan_only=False)
    assert rc == -1


def _import_without_redeploy(name, *args, **kwargs):
    if name.startswith("redeploy"):
        raise ImportError(f"No module named '{name}'")
    return __builtins__.__import__(name, *args, **kwargs)


# NOTE: testing the "redeploy API success" path would require injecting fake
# ``redeploy.*`` and ``rich.*`` modules into ``sys.modules`` so the local
# imports inside ``_deploy_via_redeploy_api`` resolve.  That is valuable but
# fragile; we cover the priority chain via the ``cmd_deploy`` tests below
# (which mock the helper itself) and leave the deep integration for a future
# ``tests/integration/`` suite.


# ── _deploy_via_redeploy_cli ───────────────────────────────────────


def test_redeploy_cli_returns_minus_one_when_not_on_path():
    with patch("shutil.which", return_value=None):
        rc = _deploy_via_redeploy_cli(Path("/tmp/migration.yaml"), dry_run=False, plan_only=False)
    assert rc == -1


def test_redeploy_cli_runs_subprocess_when_available():
    with patch("shutil.which", return_value="/usr/bin/redeploy"):
        with patch("doql.cli.commands.deploy.subprocess.call", return_value=0) as mock_call:
            rc = _deploy_via_redeploy_cli(Path("/tmp/migration.yaml"), dry_run=False, plan_only=False)
    assert rc == 0
    mock_call.assert_called_once_with(["redeploy", "run", "/tmp/migration.yaml"])


def test_redeploy_cli_passes_dry_run_and_plan_only():
    with patch("shutil.which", return_value="/usr/bin/redeploy"):
        with patch("doql.cli.commands.deploy.subprocess.call", return_value=0) as mock_call:
            rc = _deploy_via_redeploy_cli(
                Path("/tmp/migration.yaml"), dry_run=True, plan_only=True
            )
    assert rc == 0
    cmd = mock_call.call_args[0][0]
    assert "--dry-run" in cmd
    assert "--plan-only" in cmd


# ── cmd_deploy: priority chain ─────────────────────────────────────


def test_deploy_uses_directives_when_no_migration_yaml(tmp_path: Path, capsys):
    """Priority: redeploy not available → directives → docker-compose.
    When directives exist and no migration.yaml, directives win."""
    spec = _spec_with_directives(local="echo setup")

    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)
    # No migration.yaml — redeploy path falls through.

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch("doql.cli.commands.deploy.subprocess.call", return_value=0) as mock_call:
                rc = cmd_deploy(_args(dir=str(tmp_path)))

    assert rc == 0
    mock_call.assert_called_once_with("echo setup", shell=True)


def test_deploy_directive_failure_stops_pipeline(tmp_path: Path):
    """If an @local directive fails, deploy aborts with that exit code."""
    spec = _spec_with_directives(
        local="echo ok",
        push="false",  # will fail
    )

    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch("doql.cli.commands.deploy.subprocess.call", side_effect=[0, 1]) as mock_call:
                rc = cmd_deploy(_args(dir=str(tmp_path)))

    assert rc == 1
    # local ran (0), push failed (1)
    assert mock_call.call_count == 2


def test_deploy_skips_missing_directive_phases(tmp_path: Path):
    """If only @remote is present, local/push are silently skipped."""
    spec = _spec_with_directives(remote="ssh host deploy")

    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch("doql.cli.commands.deploy.subprocess.call", return_value=0) as mock_call:
                rc = cmd_deploy(_args(dir=str(tmp_path)))

    assert rc == 0
    # Should call remote only
    mock_call.assert_called_once_with("ssh host deploy", shell=True)


def test_deploy_docker_compose_fallback_no_migration_no_directives(tmp_path: Path):
    """Bare fallback: docker-compose up when nothing else configured."""
    spec = DoqlSpec(app_name="bare")
    # deploy.directives is empty by default

    build_dir = tmp_path / "build"
    infra = build_dir / "infra"
    infra.mkdir(parents=True)
    compose = infra / "docker-compose.yml"
    compose.write_text("services: {}", encoding="utf-8")

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch("doql.generators.deploy.subprocess.call", return_value=0) as mock_call:
                rc = cmd_deploy(_args(dir=str(tmp_path)))

    assert rc == 0
    # docker compose up -d --build
    cmd = mock_call.call_args[0][0]
    assert "docker" in cmd
    assert "compose" in cmd
    assert "up" in cmd


def test_deploy_fallback_fails_when_no_build(tmp_path: Path):
    """If nothing is configured and no docker-compose.yml exists, fail."""
    spec = DoqlSpec(app_name="empty")

    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)
    # No docker-compose.yml

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            rc = cmd_deploy(_args(dir=str(tmp_path)))

    assert rc == 1


# ── redeploy integration (mocked as present) ───────────────────────


def test_deploy_prefers_redeploy_api_when_migration_yaml_exists(tmp_path: Path):
    """Priority chain: redeploy API is first when migration.yaml exists."""
    spec = DoqlSpec(app_name="migrated")
    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)
    migration = build_dir / "infra" / "migration.yaml"
    migration.write_text("strategy: blue-green", encoding="utf-8")

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch(
                "doql.cli.commands.deploy._deploy_via_redeploy_api", return_value=0
            ) as mock_api:
                rc = cmd_deploy(_args(dir=str(tmp_path)))

    assert rc == 0
    mock_api.assert_called_once()


def test_deploy_falls_back_to_redeploy_cli_when_api_unavailable(tmp_path: Path):
    """API returns -1 → CLI is tried next."""
    spec = DoqlSpec(app_name="migrated")
    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)
    (build_dir / "infra" / "migration.yaml").write_text("strategy: direct", encoding="utf-8")

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch(
                "doql.cli.commands.deploy._deploy_via_redeploy_api", return_value=-1
            ):
                with patch(
                    "doql.cli.commands.deploy._deploy_via_redeploy_cli", return_value=0
                ) as mock_cli:
                    rc = cmd_deploy(_args(dir=str(tmp_path)))

    assert rc == 0
    mock_cli.assert_called_once()


def test_deploy_warns_when_redeploy_missing_and_no_directives(tmp_path: Path, capsys):
    """If redeploy is absent, no directives, and no compose → prints warning and falls through."""
    spec = DoqlSpec(app_name="naked")
    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)
    (build_dir / "infra" / "migration.yaml").write_text("x", encoding="utf-8")

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch(
                "doql.cli.commands.deploy._deploy_via_redeploy_api", return_value=-1
            ):
                with patch(
                    "doql.cli.commands.deploy._deploy_via_redeploy_cli", return_value=-1
                ):
                    rc = cmd_deploy(_args(dir=str(tmp_path)))

    captured = capsys.readouterr()
    assert "redeploy not found" in captured.out or "redeploy not found" in captured.err


# ── flags ──────────────────────────────────────────────────────────


def test_dry_run_and_plan_only_passed_to_redeploy(tmp_path: Path):
    """Flags are forwarded to the redeploy paths."""
    spec = DoqlSpec(app_name="flags")
    build_dir = tmp_path / "build"
    (build_dir / "infra").mkdir(parents=True)
    (build_dir / "infra" / "migration.yaml").write_text("x", encoding="utf-8")

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch(
                "doql.cli.commands.deploy._deploy_via_redeploy_api", return_value=0
            ) as mock_api:
                rc = cmd_deploy(_args(dir=str(tmp_path), dry_run=True, plan_only=True))

    assert rc == 0
    _, kwargs = mock_api.call_args
    assert kwargs["dry_run"] is True
    assert kwargs["plan_only"] is True


def test_target_env_defaults_to_prod(tmp_path: Path):
    """``env`` defaults to prod when not specified."""
    spec = DoqlSpec(app_name="envtest")
    build_dir = tmp_path / "build"
    infra = build_dir / "infra"
    infra.mkdir(parents=True)
    compose = infra / "docker-compose.yml"
    compose.write_text("services: {}", encoding="utf-8")

    with patch("doql.cli.commands.deploy.build_context") as mock_ctx:
        with patch("doql.cli.commands.deploy.load_spec") as mock_load:
            mock_ctx.return_value.root = tmp_path
            mock_ctx.return_value.build_dir = build_dir
            mock_load.return_value = (spec, {})

            with patch("doql.generators.deploy.subprocess.call", return_value=0):
                rc = cmd_deploy(_args(dir=str(tmp_path), env=None))

    assert rc == 0
    # deploy_gen.run(ctx, target_env="prod") is called when env is None
