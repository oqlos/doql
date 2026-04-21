"""Smoke tests for :mod:`doql.integrations.op3_bridge`.

These exercise the feature-detect plumbing and the bridge's ability to
assemble an op3 scanner with mock-driven probes. They are skipped when
``opstree`` is not installed, so ``pip install doql`` without the
``device-adopt`` extra still has a green test run.
"""
from __future__ import annotations

import pytest

from doql.integrations.op3_bridge import (
    DEFAULT_ADOPT_LAYERS,
    OP3_ENABLED_ENV,
    build_layer_tree,
    make_mock_context,
    make_scanner,
    op3_available,
    op3_enabled,
    require_op3,
    should_use_op3,
    snapshot_to_less,
)

op3 = pytest.importorskip("opstree")


# ── feature-detect ────────────────────────────────────────────────────────


def test_op3_importable():
    assert op3_available() is True
    assert hasattr(op3, "LayerTree")
    assert hasattr(op3, "Snapshot")
    assert hasattr(op3, "DriftDetector")


@pytest.mark.parametrize("value,expected", [
    ("1", True), ("true", True), ("TRUE", True), ("yes", True), ("on", True),
    ("0", False), ("false", False), ("", False), ("no", False),
])
def test_op3_enabled_reads_env(monkeypatch, value, expected):
    monkeypatch.setenv(OP3_ENABLED_ENV, value)
    assert op3_enabled() is expected


def test_should_use_op3_requires_both(monkeypatch):
    monkeypatch.delenv(OP3_ENABLED_ENV, raising=False)
    assert should_use_op3() is False

    monkeypatch.setenv(OP3_ENABLED_ENV, "1")
    # op3 is importable in this test env, so combined flag is True.
    assert should_use_op3() is True


def test_require_op3_noop_when_available():
    # Must not raise.
    require_op3("test feature")


# ── layer tree assembly ───────────────────────────────────────────────────


def test_build_layer_tree_defaults():
    tree = build_layer_tree()
    order = tree.topological_order()
    # Every default leaf layer must be present…
    for leaf in DEFAULT_ADOPT_LAYERS:
        assert leaf in order
    # …plus their transitive dependencies (business.health -> endpoint.http
    # -> service.containers -> runtime.container -> os.kernel -> physical.compute).
    for dep in ("os.kernel", "runtime.container", "service.containers",
                "endpoint.http", "physical.compute"):
        assert dep in order


def test_build_layer_tree_explicit_leaf_pulls_deps():
    tree = build_layer_tree(["service.containers"])
    order = tree.topological_order()
    assert "service.containers" in order
    assert "runtime.container" in order  # transitive
    assert "os.kernel" in order          # transitive
    # Topological: deps come before dependents.
    assert order.index("runtime.container") < order.index("service.containers")


def test_build_layer_tree_rejects_unknown():
    with pytest.raises(ValueError, match="Unknown op3 layer id"):
        build_layer_tree(["not.a.real.layer"])


# ── scanner + mock context end-to-end ─────────────────────────────────────


def test_scanner_runs_against_mock_context():
    """A realistic fake device: podman running one container, one systemd
    unit. Exercises the full path: build tree → register probes →
    LinearScanner.scan → Snapshot with at least the runtime layer."""
    responses = {
        # runtime detection
        "which docker": ("", "", 1),
        "which podman": ("/usr/bin/podman", "", 0),
        "podman --version 2>/dev/null": ("podman version 4.9.4", "", 0),
        "podman ps -a --format json 2>/dev/null": (
            '[{"Id":"abc123def456","Names":["web"],"Image":"nginx:latest",'
            '"State":"running","Status":"Up 2 hours","Labels":{}}]',
            "", 0,
        ),
        # systemd
        "which systemctl": ("/bin/systemctl", "", 0),
        "systemctl list-units --type=service --all --no-legend 2>/dev/null": (
            "nginx.service loaded active running   nginx web server\n",
            "", 0,
        ),
        "systemctl is-enabled nginx.service 2>/dev/null": ("enabled", "", 0),
        # endpoint http probe — graceful failure is fine for this smoke test.
    }

    ctx = make_mock_context(responses)
    scanner = make_scanner(["runtime.container", "service.containers"])
    snapshot = scanner.scan("mock@device", ctx.execute)

    assert snapshot.target == "mock@device"
    runtime = snapshot.layer("runtime.container")
    assert runtime is not None, "runtime.container probe should have succeeded"
    assert runtime.data["runtime"] == "podman"
    assert any(c["name"] == "web" for c in runtime.data["containers"])

    services = snapshot.layer("service.containers")
    assert services is not None
    assert any(s["name"] == "nginx.service"
               for s in services.data["systemd_services"])


def test_snapshot_to_less_produces_parsable_less():
    """A snapshot rendered to LESS must be re-parsable by doql's own
    ``parse_css_text`` — that's the integration contract we actually care
    about."""
    from doql.parsers import parse_css_text

    responses = {
        "which docker": ("", "", 1),
        "which podman": ("/usr/bin/podman", "", 0),
        "podman --version 2>/dev/null": ("podman version 4.9.4", "", 0),
        "podman ps -a --format json 2>/dev/null": ("[]", "", 0),
        "which systemctl": ("/bin/systemctl", "", 0),
        "systemctl list-units --type=service --all --no-legend 2>/dev/null": (
            "nginx.service loaded active running nginx web server\n", "", 0,
        ),
        "systemctl is-enabled nginx.service 2>/dev/null": ("enabled", "", 0),
    }

    ctx = make_mock_context(responses)
    scanner = make_scanner(["service.containers"])
    snapshot = scanner.scan("mock@device", ctx.execute)

    less_text = snapshot_to_less(snapshot, scope=["service", "runtime"])
    assert "service[name=" in less_text

    spec = parse_css_text(less_text, format="less")
    assert not any(issue.severity == "error" for issue in spec.parse_errors), (
        f"doql could not parse op3-generated LESS: {spec.parse_errors}"
    )
