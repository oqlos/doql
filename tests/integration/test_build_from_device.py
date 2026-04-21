"""End-to-end tests for ``doql build --from-device``.

The flag chains two existing code paths that are already well-tested:

1. :func:`doql.adopt.device_scanner.adopt_from_device` — Sprint 1
2. :func:`doql.cli.build.cmd_build` — pre-existing

So the tests here are focused on the **wiring**:

- The scan happens *before* the build (and therefore *before* ``load_spec``).
- The resulting file lands at the expected path and is picked up by
  :class:`BuildContext`.
- Overwrite safety: the build refuses to trample an existing
  ``app.doql.less`` unless ``--force`` is set — the same switch the build
  command already uses for validation bypass.
- Error handling from Sprint 1 (op3 missing, scan failure) is preserved.

We inject an :class:`opstree.MockContext` via ``context_factory`` to
avoid any real SSH activity.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

pytest.importorskip("opstree")

from doql.cli.build import _scan_device_for_build, cmd_build  # noqa: E402
from doql.cli.context import BuildContext  # noqa: E402
from doql.integrations.op3_bridge import make_mock_context  # noqa: E402


# ── fixtures ──────────────────────────────────────────────────────────────


def _healthy_rpi_responses() -> dict[str, tuple[str, str, int]]:
    """Minimal mock responses that let the service + runtime probes
    succeed. Mirrors the shape used in ``tests/integration/test_adopt_from_device.py``."""
    return {
        # runtime.container
        "which docker": ("/usr/bin/docker", "", 0),
        "which podman": ("", "", 1),
        "docker --version 2>/dev/null": ("Docker version 24.0.7, build afdd53b", "", 0),
        "podman --version 2>/dev/null": ("", "", 1),
        "docker ps -a --format json 2>/dev/null": (
            '[{"ID":"deadbeef1234","Names":"web","Image":"nginx:1.25",'
            '"State":"running","Status":"Up 3 hours","Labels":{}}]',
            "", 0,
        ),
        "podman ps -a --format json 2>/dev/null": ("", "", 1),
        # service.containers
        "which systemctl": ("/bin/systemctl", "", 0),
        "systemctl list-units --type=service --all --no-legend 2>/dev/null": (
            "nginx.service loaded active running nginx web server\n",
            "", 0,
        ),
        "systemctl is-enabled nginx.service 2>/dev/null": ("enabled", "", 0),
    }


def _build_args(root: Path, **overrides) -> argparse.Namespace:
    """Build a namespace matching what ``create_parser`` emits for
    ``doql build``.  Global flags (``dir`` / ``file``) are included
    because ``build_context`` reads them via ``getattr``."""
    defaults = dict(
        dir=str(root),
        file=None,
        # build subparser flags:
        force=False,
        no_overwrite=False,
        from_device="pi@fake.local",
        ssh_key=None,
        layers=["service.containers"],
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _patch_context_factory(monkeypatch, responses):
    """Install a MockContext-based ``adopt_from_device`` so no real SSH
    happens. The patch is applied at the ``device_scanner`` module so both
    the direct import inside :func:`_scan_device_for_build` and other
    call sites pick it up.
    """
    from doql.adopt import device_scanner

    ctx = make_mock_context(responses)
    real = device_scanner.adopt_from_device

    def _patched(**kw):
        if kw.get("context_factory") is None:
            kw["context_factory"] = lambda: ctx
        return real(**kw)

    monkeypatch.setattr(device_scanner, "adopt_from_device", _patched)


# ── _scan_device_for_build — unit-level wiring ────────────────────────────


def test_scan_device_writes_app_doql_less_in_root(tmp_path, monkeypatch,
                                                   capsys):
    _patch_context_factory(monkeypatch, _healthy_rpi_responses())

    ctx = BuildContext(
        root=tmp_path,
        doql_file=tmp_path / "app.doql",   # intentionally *not* what we'll use
        env_file=tmp_path / ".env",
        build_dir=tmp_path / "build",
    )

    args = _build_args(tmp_path)
    new_ctx = _scan_device_for_build(ctx, args)

    scanned = tmp_path / "app.doql.less"
    assert scanned.exists(), "scan must land at <root>/app.doql.less"
    assert new_ctx.doql_file == scanned.resolve(), (
        "returned BuildContext must pin doql_file at the scanned path "
        "so downstream load_spec doesn't re-auto-detect and pick .css"
    )
    # Non-doql-file attrs preserved.
    assert new_ctx.root == ctx.root
    assert new_ctx.env_file == ctx.env_file
    assert new_ctx.build_dir == ctx.build_dir

    captured = capsys.readouterr()
    assert "Scanning device pi@fake.local" in captured.out
    assert "Wrote" in captured.out


def test_scan_device_honours_global_file_flag(tmp_path, monkeypatch):
    """When ``-f/--file`` is passed at the top level, the scan output
    goes there instead of the default name."""
    _patch_context_factory(monkeypatch, _healthy_rpi_responses())

    ctx = BuildContext(
        root=tmp_path,
        doql_file=tmp_path / "custom.less",
        env_file=tmp_path / ".env",
        build_dir=tmp_path / "build",
    )
    args = _build_args(tmp_path, file="custom.less")

    new_ctx = _scan_device_for_build(ctx, args)
    assert new_ctx.doql_file == (tmp_path / "custom.less").resolve()
    assert (tmp_path / "custom.less").exists()


def test_scan_device_refuses_to_overwrite_without_force(tmp_path, monkeypatch,
                                                        capsys):
    _patch_context_factory(monkeypatch, _healthy_rpi_responses())

    existing = tmp_path / "app.doql.less"
    existing.write_text("// hand-written spec\n", encoding="utf-8")

    ctx = BuildContext(
        root=tmp_path,
        doql_file=existing,
        env_file=tmp_path / ".env",
        build_dir=tmp_path / "build",
    )
    args = _build_args(tmp_path, force=False)

    with pytest.raises(SystemExit) as exc_info:
        _scan_device_for_build(ctx, args)
    assert exc_info.value.code == 1

    err = capsys.readouterr().err
    assert "already exists" in err
    assert "--force" in err

    # The original content must be untouched.
    assert existing.read_text(encoding="utf-8") == "// hand-written spec\n"


def test_scan_device_force_overwrites(tmp_path, monkeypatch):
    _patch_context_factory(monkeypatch, _healthy_rpi_responses())

    existing = tmp_path / "app.doql.less"
    existing.write_text("// pre-existing\n", encoding="utf-8")

    ctx = BuildContext(
        root=tmp_path,
        doql_file=existing,
        env_file=tmp_path / ".env",
        build_dir=tmp_path / "build",
    )
    args = _build_args(tmp_path, force=True)

    _scan_device_for_build(ctx, args)
    content = existing.read_text(encoding="utf-8")
    assert "// pre-existing" not in content
    assert "Auto-generated by `doql adopt --from-device`" in content


# ── cmd_build — full integration ──────────────────────────────────────────


def _minimal_env_file(root: Path) -> None:
    (root / ".env").write_text("", encoding="utf-8")


def test_cmd_build_from_device_runs_full_pipeline(tmp_path, monkeypatch,
                                                   capsys):
    """End-to-end: ``cmd_build`` with ``--from-device`` must scan first,
    then run the generators. Success is defined as exit code 0 and the
    scanned file being present afterwards.

    ``--force`` is the realistic usage pattern when chaining scan+build:
    a device snapshot is unlikely to satisfy every validation rule that
    a hand-authored spec does (e.g. op3's default render scope doesn't
    emit an ``app{}`` block), so the user either authors a spec first
    or accepts that the scanned state is best-effort and bypasses the
    validator.
    """
    _patch_context_factory(monkeypatch, _healthy_rpi_responses())
    _minimal_env_file(tmp_path)

    args = _build_args(tmp_path, force=True)
    rc = cmd_build(args)

    # Capture so failure diagnostics are informative.
    captured = capsys.readouterr()
    assert rc == 0, (
        f"cmd_build exited {rc}\nstdout:\n{captured.out}\nstderr:\n{captured.err}"
    )

    # The scan ran.
    assert (tmp_path / "app.doql.less").exists()
    assert "Scanning device pi@fake.local" in captured.out

    # A build directory was created by the generator pipeline.
    assert (tmp_path / "build").is_dir(), (
        "cmd_build should create <root>/build; got:\n"
        f"stdout:\n{captured.out}\nstderr:\n{captured.err}"
    )


def test_cmd_build_refuses_to_clobber_without_force(tmp_path, monkeypatch,
                                                    capsys):
    _patch_context_factory(monkeypatch, _healthy_rpi_responses())
    _minimal_env_file(tmp_path)
    (tmp_path / "app.doql.less").write_text("// manual\n", encoding="utf-8")

    args = _build_args(tmp_path, force=False)
    rc = cmd_build(args)

    assert rc == 1
    err = capsys.readouterr().err
    assert "already exists" in err
    # Original file untouched.
    assert (tmp_path / "app.doql.less").read_text(encoding="utf-8") == "// manual\n"


def test_cmd_build_without_from_device_skips_scan(tmp_path, monkeypatch):
    """Regression guard: plain ``doql build`` must not touch op3 at all.

    If ``--from-device`` is None, the scan helper is never called, so we
    don't even need to patch the context factory. We verify that by
    setting a poisoned ``adopt_from_device`` that would raise if invoked.
    """
    from doql.adopt import device_scanner

    def _poisoned(**_):
        raise AssertionError(
            "adopt_from_device must NOT be called when --from-device is None"
        )

    monkeypatch.setattr(device_scanner, "adopt_from_device", _poisoned)

    # Provide a minimal valid spec so the rest of the build works.
    (tmp_path / "app.doql.less").write_text(
        "app {\n  name: noop;\n  version: 0.0.0;\n}\n",
        encoding="utf-8",
    )
    _minimal_env_file(tmp_path)

    args = _build_args(tmp_path, from_device=None, layers=None)
    rc = cmd_build(args)
    assert rc == 0
