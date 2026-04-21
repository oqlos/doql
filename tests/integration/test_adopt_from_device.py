"""End-to-end tests for ``doql adopt --from-device``.

We can't (and don't want to) SSH to a real device in CI. Instead we inject
an :class:`opstree.MockContext` via the ``context_factory`` hook and
verify that the full pipeline — scan → render → write — produces a usable
``.doql.less`` file.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pytest

pytest.importorskip("opstree")

from doql.adopt.device_scanner import (  # noqa: E402  (after importorskip)
    adopt_from_device,
    adopt_from_device_to_snapshot,
)
from doql.cli.commands.adopt import cmd_adopt  # noqa: E402
from doql.integrations.op3_bridge import make_mock_context  # noqa: E402


# ── fixture helpers ───────────────────────────────────────────────────────


def _healthy_rpi_responses() -> dict[str, tuple[str, str, int]]:
    """Minimal set of SSH responses to satisfy the default adopt layers.

    Covers runtime (docker present, one container), service
    (``nginx.service`` running), and leaves endpoint/business probes to
    report graceful "unknown" results.
    """
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
            "nginx.service   loaded active running nginx web server\n"
            "sshd.service    loaded active running OpenSSH server\n",
            "", 0,
        ),
        "systemctl is-enabled nginx.service 2>/dev/null": ("enabled", "", 0),
        "systemctl is-enabled sshd.service 2>/dev/null": ("enabled", "", 0),
    }


def _rpi5_podman_quadlet_responses() -> dict[str, tuple[str, str, int]]:
    """Realistic SSH responses from an RPi5 running Podman Quadlet (c2004).

    Derived from ``c2004/redeploy/pi109/`` diagnostic logs.  Covers:
    * runtime.container  → podman 4.9.4, c2004-* containers
    * service.containers → systemd user services (quadlet-generated)
    * endpoint.http      → localhost:8000 /api/v3/health (backend)
    * business.health    → same endpoint interpreted as app health

    Note: op3's ``ServiceContainersProbe`` currently uses ``systemctl
    list-units`` (root slice).  Real Quadlet services live in the user
    slice, so this fixture approximates them as root services for the
    test.  A future op3 enhancement may add ``--user`` support.
    """
    return {
        # runtime.container — podman preferred, docker absent
        "which docker": ("", "", 1),
        "which podman": ("/usr/bin/podman", "", 0),
        "docker --version 2>/dev/null": ("", "", 1),
        "podman --version 2>/dev/null": ("podman version 4.9.4", "", 0),
        "podman ps -a --format json 2>/dev/null": (
            '[{"Id":"abc123def456","Names":["c2004-backend"],'
            '"Image":"localhost/c2004-backend:latest",'
            '"State":"running","Status":"Up 2 hours",'
            '"Labels":{"io.podman.annotations.restartpolicy":"always"}},'
            '{"Id":"bcd234efg567","Names":["c2004-frontend"],'
            '"Image":"localhost/c2004-frontend:latest",'
            '"State":"running","Status":"Up 2 hours",'
            '"Labels":{"io.podman.annotations.restartpolicy":"always"}},'
            '{"Id":"cde345fgh678","Names":["c2004-firmware"],'
            '"Image":"localhost/c2004-firmware:latest",'
            '"State":"running","Status":"Up 2 hours",'
            '"Labels":{"io.podman.annotations.restartpolicy":"always"}},'
            '{"Id":"def456ghi789","Names":["c2004-reverse-proxy"],'
            '"Image":"docker.io/library/traefik:v2.11",'
            '"State":"running","Status":"Up 2 hours",'
            '"Labels":{"io.podman.annotations.restartpolicy":"always"}}]',
            "", 0,
        ),
        "docker ps -a --format json 2>/dev/null": ("", "", 1),
        # service.containers — c2004 quadlet-generated services (root approximation)
        "which systemctl": ("/bin/systemctl", "", 0),
        "systemctl list-units --type=service --all --no-legend 2>/dev/null": (
            "c2004-backend.service      loaded active running c2004 backend API\n"
            "c2004-frontend.service     loaded active running c2004 frontend nginx\n"
            "c2004-firmware.service     loaded active running c2004 firmware simulator\n"
            "c2004-reverse-proxy.service loaded active running c2004 Traefik reverse proxy\n"
            "sshd.service               loaded active running OpenSSH server\n"
            "chronyd.service            loaded active running NTP client\n",
            "", 0,
        ),
        "systemctl is-enabled c2004-backend.service 2>/dev/null": ("enabled", "", 0),
        "systemctl is-enabled c2004-frontend.service 2>/dev/null": ("enabled", "", 0),
        "systemctl is-enabled c2004-firmware.service 2>/dev/null": ("enabled", "", 0),
        "systemctl is-enabled c2004-reverse-proxy.service 2>/dev/null": ("enabled", "", 0),
        "systemctl is-enabled sshd.service 2>/dev/null": ("enabled", "", 0),
        "systemctl is-enabled chronyd.service 2>/dev/null": ("enabled", "", 0),
        # endpoint.http — curl available, backend healthy
        "which curl": ("/usr/bin/curl", "", 0),
        "curl -s -o /dev/null -w '%{http_code}' -X GET http://localhost:8000/api/v3/health 2>/dev/null": (
            "200", "", 0,
        ),
        "curl -s -o /dev/null -w '%{time_total}' -X GET http://localhost:8000/api/v3/health 2>/dev/null": (
            "0.045", "", 0,
        ),
        # business.health — same endpoint, interpreted differently
        "curl -s -o /dev/null -w '%{http_code}' -X GET http://localhost:8100/ 2>/dev/null": (
            "200", "", 0,
        ),
        "curl -s -o /dev/null -w '%{time_total}' -X GET http://localhost:8100/ 2>/dev/null": (
            "0.012", "", 0,
        ),
    }


# ── functional API ────────────────────────────────────────────────────────


def test_adopt_from_device_returns_less_text():
    ctx = make_mock_context(_healthy_rpi_responses())
    text = adopt_from_device(
        target="pi@fake.local",
        layers=["service.containers"],
        context_factory=lambda: ctx,
    )

    # Provenance header.
    assert "Auto-generated by `doql adopt --from-device`" in text
    assert "Source: pi@fake.local" in text
    assert "Scanner: op3" in text

    # Body contains the scanned service.
    assert 'service[name="nginx.service"]' in text


def test_adopt_from_device_writes_output(tmp_path: Path):
    ctx = make_mock_context(_healthy_rpi_responses())
    out = tmp_path / "generated.doql.less"

    text = adopt_from_device(
        target="pi@fake.local",
        layers=["service.containers"],
        output=out,
        context_factory=lambda: ctx,
    )

    assert out.exists()
    assert out.read_text(encoding="utf-8") == text
    assert out.stat().st_size > 0


def test_adopt_from_device_to_snapshot_contains_layer_data():
    ctx = make_mock_context(_healthy_rpi_responses())
    snapshot = adopt_from_device_to_snapshot(
        target="pi@fake.local",
        layers=["service.containers"],
        context_factory=lambda: ctx,
    )

    services = snapshot.layer("service.containers")
    assert services is not None
    names = {s["name"] for s in services.data["systemd_services"]}
    assert "nginx.service" in names
    assert "sshd.service" in names


def test_adopt_output_is_parsable_by_doql(tmp_path: Path):
    """Contract test: the LESS we emit must round-trip through doql's
    own parser without an error-level diagnostic."""
    from doql.parsers import parse_file

    ctx = make_mock_context(_healthy_rpi_responses())
    out = tmp_path / "app.doql.less"
    adopt_from_device(
        target="pi@fake.local",
        layers=["service.containers"],
        output=out,
        context_factory=lambda: ctx,
    )

    spec = parse_file(out)
    assert not [i for i in spec.parse_errors if i.severity == "error"], (
        f"doql could not parse op3-generated LESS: {spec.parse_errors}"
    )


# ── RPi5 Podman Quadlet (real-world pi109) ────────────────────────────────


def test_adopt_from_rpi5_podman_quadlet_returns_less_text():
    ctx = make_mock_context(_rpi5_podman_quadlet_responses())
    text = adopt_from_device(
        target="pi@192.168.188.109",
        layers=["service.containers", "runtime.container"],
        context_factory=lambda: ctx,
    )

    assert "Auto-generated by `doql adopt --from-device`" in text
    assert "Source: pi@192.168.188.109" in text
    assert "Scanner: op3" in text

    # Body should contain scanned podman containers
    assert 'service[name="c2004-backend"]' in text or "c2004-backend" in text


def test_adopt_from_rpi5_to_snapshot_contains_all_services():
    ctx = make_mock_context(_rpi5_podman_quadlet_responses())
    snapshot = adopt_from_device_to_snapshot(
        target="pi@192.168.188.109",
        layers=["service.containers"],
        context_factory=lambda: ctx,
    )

    services = snapshot.layer("service.containers")
    assert services is not None
    names = {s["name"] for s in services.data["systemd_services"]}
    assert "c2004-backend.service" in names
    assert "c2004-frontend.service" in names
    assert "c2004-firmware.service" in names
    assert "c2004-reverse-proxy.service" in names


def test_adopt_from_rpi5_to_snapshot_contains_all_containers():
    ctx = make_mock_context(_rpi5_podman_quadlet_responses())
    snapshot = adopt_from_device_to_snapshot(
        target="pi@192.168.188.109",
        layers=["runtime.container"],
        context_factory=lambda: ctx,
    )

    runtime = snapshot.layer("runtime.container")
    assert runtime is not None
    containers = runtime.data["containers"]
    names = {c["name"] for c in containers}
    assert "c2004-backend" in names
    assert "c2004-frontend" in names
    assert "c2004-firmware" in names
    assert "c2004-reverse-proxy" in names

    # Podman runtime detected, not docker
    assert runtime.data["runtime"] == "podman"
    assert runtime.data["version"] == "4.9.4"


def test_adopt_from_rpi5_output_is_parsable_by_doql(tmp_path: Path):
    """Contract test: the LESS we emit from RPi5 data must round-trip
    through doql's own parser without an error-level diagnostic."""
    from doql.parsers import parse_file

    ctx = make_mock_context(_rpi5_podman_quadlet_responses())
    out = tmp_path / "app.doql.less"
    adopt_from_device(
        target="pi@192.168.188.109",
        layers=["service.containers", "runtime.container"],
        output=out,
        context_factory=lambda: ctx,
    )

    spec = parse_file(out)
    assert not [i for i in spec.parse_errors if i.severity == "error"], (
        f"doql could not parse op3-generated LESS from RPi5: {spec.parse_errors}"
    )


# ── CLI wiring ────────────────────────────────────────────────────────────


def _make_cli_args(**overrides) -> argparse.Namespace:
    """Build a namespace that matches what ``create_parser`` produces."""
    defaults = dict(
        target=None,
        output=None,
        format="less",
        force=False,
        from_device="pi@fake.local",
        ssh_key=None,
        layers=["service.containers"],
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


def test_cmd_adopt_from_device_writes_file(tmp_path: Path, monkeypatch,
                                           capsys: pytest.CaptureFixture[str]):
    """``cmd_adopt`` should delegate to the device scanner and return 0."""
    out = tmp_path / "app.doql.less"
    ctx = make_mock_context(_healthy_rpi_responses())

    # Inject our MockContext by patching the ``adopt_from_device`` symbol
    # that the CLI command imports. We import it *inside* the function
    # under test (``_cmd_adopt_from_device``), so patching the source
    # module is enough.
    from doql.adopt import device_scanner

    real = device_scanner.adopt_from_device

    def _patched(**kw):
        kw.setdefault("context_factory", lambda: ctx)
        return real(**kw)

    monkeypatch.setattr(device_scanner, "adopt_from_device", _patched)

    args = _make_cli_args(output=str(out))
    rc = cmd_adopt(args)

    captured = capsys.readouterr()
    assert rc == 0, captured
    assert out.exists()
    assert "Scanning device pi@fake.local" in captured.out
    assert "Written" in captured.out


def test_cmd_adopt_rejects_non_less_format(capsys: pytest.CaptureFixture[str]):
    args = _make_cli_args(format="css")
    rc = cmd_adopt(args)
    assert rc == 2
    err = capsys.readouterr().err
    assert "--format less only" in err


def test_cmd_adopt_without_target_or_device_errors(capsys):
    args = _make_cli_args(from_device=None, target=None)
    rc = cmd_adopt(args)
    assert rc == 2
    assert "target directory or --from-device" in capsys.readouterr().err


def test_cmd_adopt_refuses_to_overwrite(tmp_path: Path, monkeypatch,
                                        capsys: pytest.CaptureFixture[str]):
    out = tmp_path / "app.doql.less"
    out.write_text("// pre-existing", encoding="utf-8")

    args = _make_cli_args(output=str(out), force=False)
    rc = cmd_adopt(args)

    assert rc == 1
    assert "already exists" in capsys.readouterr().out
