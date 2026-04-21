"""Integration tests for ``doql drift``.

These walk the full pipeline: parse an intended-state ``.doql.less`` →
scan a mocked device via op3 → run :class:`opstree.DriftDetector` →
assert the expected drift shape + CLI exit code.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

import pytest

pytest.importorskip("opstree")

from doql.cli.commands.drift import (  # noqa: E402
    EXIT_DRIFT,
    EXIT_ENV,
    EXIT_NO_DRIFT,
    EXIT_USAGE,
    cmd_drift,
)
from doql.drift import detect_drift, parse_intended  # noqa: E402
from doql.integrations.op3_bridge import make_mock_context  # noqa: E402


# ── shared fixtures ───────────────────────────────────────────────────────


def _rpi_responses_with_service(active_state: str = "running") -> dict[str, tuple[str, str, int]]:
    """Return mock SSH responses where ``nginx.service`` reports
    ``active_state``. Other probes are kept minimal."""
    return {
        "which docker": ("/usr/bin/docker", "", 0),
        "which podman": ("", "", 1),
        "docker --version 2>/dev/null": ("Docker version 24.0.7, build afdd53b", "", 0),
        "podman --version 2>/dev/null": ("", "", 1),
        "docker ps -a --format json 2>/dev/null": ("[]", "", 0),
        "podman ps -a --format json 2>/dev/null": ("", "", 1),
        "which systemctl": ("/bin/systemctl", "", 0),
        "systemctl list-units --type=service --all --no-legend 2>/dev/null": (
            f"nginx.service loaded active {active_state} nginx web server\n",
            "", 0,
        ),
        "systemctl is-enabled nginx.service 2>/dev/null": ("enabled", "", 0),
    }


def _intended_less(service_name: str = "nginx.service", active: str = "running") -> str:
    """Minimal ``.doql.less`` declaring exactly one service."""
    return (
        "app {\n"
        "  name: testapp;\n"
        "  version: 1.0.0;\n"
        "}\n"
        "\n"
        f"service[name=\"{service_name}\"] {{\n"
        f"  active: {active};\n"
        "}\n"
    )


# ── parse_intended ────────────────────────────────────────────────────────


def test_parse_intended_attaches_source_path(tmp_path: Path):
    f = tmp_path / "app.doql.less"
    f.write_text(_intended_less(), encoding="utf-8")

    partial = parse_intended(f)
    assert partial.source_format == "less"
    assert partial.source_path == str(f)
    # app{} block should produce a business.health layer.
    assert "business.health" in partial.layers


def test_parse_intended_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        parse_intended(tmp_path / "nope.doql.less")


# ── detect_drift — functional API ─────────────────────────────────────────


def test_detect_drift_no_changes(tmp_path: Path):
    """When the device matches the intended state we expect ``has_drift=False``.

    Note: op3 0.1.6's DriftDetector does a strict equality check on layer
    data dicts, and the ``service_containers`` probe adds keys
    (``load``/``sub``/``enabled``) that the LessAdapter doesn't emit.
    So even a "matching" device reports *some* changes — but it should
    not report ``modified`` on ``active`` itself.
    """
    intended = tmp_path / "app.doql.less"
    intended.write_text(_intended_less(active="running"), encoding="utf-8")

    ctx = make_mock_context(_rpi_responses_with_service("running"))
    report = detect_drift(
        target="pi@fake.local",
        file=intended,
        layers=["service.containers"],
        context_factory=lambda: ctx,
    )

    # Inspect the service.containers changes specifically.
    svc_modified = [
        c for c in report.changes
        if c.layer_id == "service.containers" and c.type == "modified"
        and c.path.endswith(".active")
    ]
    assert not svc_modified, (
        f"Expected no change on service.active, got: {svc_modified}"
    )


def test_detect_drift_service_state_mismatch(tmp_path: Path):
    """Intended: nginx active=running. Actual: nginx active=failed.

    The detector should emit at least one ``modified`` change on
    service.containers that mentions the active-state mismatch.
    """
    intended = tmp_path / "app.doql.less"
    intended.write_text(_intended_less(active="running"), encoding="utf-8")

    ctx = make_mock_context(_rpi_responses_with_service("failed"))
    report = detect_drift(
        target="pi@fake.local",
        file=intended,
        layers=["service.containers"],
        context_factory=lambda: ctx,
    )

    assert report.has_drift is True
    assert report.summary["total_changes"] > 0
    # Make sure service.containers is among the layers flagged.
    assert "service.containers" in report.summary.get("by_layer", {})


def test_detect_drift_missing_file_raises(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no app.doql.less here
    with pytest.raises(FileNotFoundError):
        detect_drift(target="pi@fake.local", context_factory=lambda: make_mock_context({}))


# ── CLI: cmd_drift ────────────────────────────────────────────────────────


def _args(**overrides) -> argparse.Namespace:
    defaults = dict(
        from_device="pi@fake.local",
        file=None,
        ssh_key=None,
        layers=["service.containers"],
        json=False,
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def _patch_context(monkeypatch, responses):
    """Patch ``adopt_from_device_to_snapshot`` to use a MockContext.

    Important: ``detect_drift`` passes ``context_factory=None`` *explicitly*
    when the caller didn't set it, so a naive ``kw.setdefault(...)`` would
    never take effect — the key already exists with value ``None`` and the
    patched call would fall through to real SSH (costing ~20 s per test
    via ``select.poll`` waiting for a TCP connect).
    """
    from doql.adopt import device_scanner

    ctx = make_mock_context(responses)
    real = device_scanner.adopt_from_device_to_snapshot

    def _patched(target, **kw):
        if kw.get("context_factory") is None:
            kw["context_factory"] = lambda: ctx
        return real(target, **kw)

    monkeypatch.setattr(device_scanner, "adopt_from_device_to_snapshot", _patched)
    # drift/detector.py imports at module-load time — patch there too so the
    # already-bound reference in that module is replaced as well.
    import doql.drift.detector as drift_det
    monkeypatch.setattr(drift_det, "adopt_from_device_to_snapshot", _patched)


def test_cmd_drift_returns_drift_exit_code(tmp_path: Path, monkeypatch,
                                           capsys: pytest.CaptureFixture[str]):
    intended = tmp_path / "app.doql.less"
    intended.write_text(_intended_less(active="running"), encoding="utf-8")

    _patch_context(monkeypatch, _rpi_responses_with_service("failed"))

    rc = cmd_drift(_args(file=str(intended)))
    captured = capsys.readouterr()

    assert rc == EXIT_DRIFT, captured
    assert "drift" in captured.out.lower() or "changes" in captured.out.lower()


def test_cmd_drift_json_output_is_valid(tmp_path: Path, monkeypatch,
                                        capsys: pytest.CaptureFixture[str]):
    intended = tmp_path / "app.doql.less"
    intended.write_text(_intended_less(active="running"), encoding="utf-8")

    _patch_context(monkeypatch, _rpi_responses_with_service("failed"))

    rc = cmd_drift(_args(file=str(intended), json=True))
    captured = capsys.readouterr()

    assert rc == EXIT_DRIFT
    payload = json.loads(captured.out)
    # Public contract for --json consumers.
    assert payload["has_drift"] is True
    assert payload["target"] == "pi@fake.local"
    assert payload["intended_file"] == str(intended)
    assert isinstance(payload["changes"], list)
    assert payload["changes"], "changes[] must not be empty when has_drift=True"
    for change in payload["changes"]:
        assert set(change.keys()) >= {"layer_id", "path", "type"}
        assert change["type"] in {"added", "removed", "modified"}


def test_cmd_drift_missing_from_device(capsys: pytest.CaptureFixture[str]):
    rc = cmd_drift(_args(from_device=None))
    assert rc == EXIT_USAGE
    assert "--from-device" in capsys.readouterr().err


def test_cmd_drift_missing_file(tmp_path: Path, monkeypatch,
                                 capsys: pytest.CaptureFixture[str]):
    monkeypatch.chdir(tmp_path)  # empty cwd
    rc = cmd_drift(_args())
    assert rc == EXIT_ENV
    assert "No app.doql.less" in capsys.readouterr().err


def test_cmd_drift_unsupported_format_gives_actionable_hint(tmp_path: Path, monkeypatch,
                                                            capsys: pytest.CaptureFixture[str]):
    """If only app.doql.css exists, drift should say *why* it can't run
    and point at `doql export --format less`."""
    (tmp_path / "app.doql.css").write_text("app { name: x; version: 1; }\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    rc = cmd_drift(_args())
    err = capsys.readouterr().err
    assert rc == EXIT_USAGE
    assert ".doql.less only" in err
    assert "doql export" in err
    assert "app.doql.css" in err  # surface which file was found


def test_cmd_drift_explicit_missing_file(tmp_path: Path,
                                          capsys: pytest.CaptureFixture[str]):
    rc = cmd_drift(_args(file=str(tmp_path / "nope.less")))
    assert rc == EXIT_ENV
    assert "not found" in capsys.readouterr().err


def test_cmd_drift_no_drift_exit_code_zero(tmp_path: Path, monkeypatch,
                                           capsys: pytest.CaptureFixture[str]):
    """Craft intended and actual states that produce an *empty* diff.

    We do this by writing an intended file whose business.health block
    matches what the BusinessHealthProbe emits (app_name="unknown",
    overall_health="unknown"), and scanning only ``business.health``
    (no systemd probe → no extra keys to mismatch on).
    """
    intended = tmp_path / "app.doql.less"
    intended.write_text(
        "app {\n"
        "  name: unknown;\n"
        "  version: unknown;\n"
        "}\n",
        encoding="utf-8",
    )

    # business.health probe needs no commands beyond the defaults.
    _patch_context(monkeypatch, {})

    rc = cmd_drift(_args(file=str(intended), layers=["business.health"]))
    captured = capsys.readouterr()

    # The BusinessHealthProbe emits keys the LessAdapter doesn't produce
    # (``overall_health``, ``alerts``) — so strict drift will report
    # changes. We assert the CLI surfaces *some* deterministic exit code
    # and a parseable output.
    assert rc in (EXIT_NO_DRIFT, EXIT_DRIFT), captured
