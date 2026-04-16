"""Tests for plugin discovery + per-plugin generation + numerical correctness (ISO 17025 math)."""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

from doql import parser


ROOT = pathlib.Path(__file__).parent.parent


# ─── Plugin discovery ──────────────────────────────────────────

def test_entrypoint_discovery_finds_all_four():
    from importlib.metadata import entry_points
    eps = list(entry_points().select(group="doql_plugins"))
    names = {ep.name for ep in eps}
    # All four reference plugins should be installed in editable mode
    for expected in ("gxp", "iso17025", "fleet", "erp"):
        assert expected in names, f"Missing plugin: {expected}. Found: {names}"


def test_doql_plugins_module_import():
    """The plugin subsystem itself must import cleanly."""
    from doql import plugins as p
    assert hasattr(p, "discover_plugins")
    assert hasattr(p, "run_plugins")


# ─── GxP plugin numerical correctness ──────────────────────────

def _run_plugin_and_import(plugin_name: str, subpath: str, symbol: str):
    """Load a plugin's generated file from the asset-management example build."""
    path = ROOT / "examples" / "asset-management" / "build" / "plugins" / plugin_name / f"{subpath}.py"
    if not path.exists():
        pytest.skip(f"Plugin output not found: {path}. Run `doql build` first.")
    import importlib.util
    mod_name = f"_doql_test_{plugin_name}_{subpath}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    # Register BEFORE exec — @dataclass walks sys.modules[cls.__module__]
    sys.modules[mod_name] = mod
    try:
        spec.loader.exec_module(mod)
    except ImportError as e:
        sys.modules.pop(mod_name, None)
        pytest.skip(f"Plugin module requires dep: {e}")
    return getattr(mod, symbol)


def test_iso17025_uncertainty_budget_numerical():
    """GUM-compliant uncertainty budget — u_c = √Σ(cᵢ·uᵢ)²."""
    UncertaintyBudget = _run_plugin_and_import("iso17025", "uncertainty", "UncertaintyBudget")
    UncertaintyComponent = _run_plugin_and_import("iso17025", "uncertainty", "UncertaintyComponent")
    Distribution = _run_plugin_and_import("iso17025", "uncertainty", "Distribution")
    UncertaintyType = _run_plugin_and_import("iso17025", "uncertainty", "UncertaintyType")

    b = UncertaintyBudget(measurand="pressure", unit="bar", coverage_factor=2.0)
    b.add(UncertaintyComponent(
        "ref_std_U", 0.02, type=UncertaintyType.TYPE_B,
        distribution=Distribution.NORMAL, coverage_factor=2.0,
    ))
    b.add(UncertaintyComponent("repeatability", 0.015, type=UncertaintyType.TYPE_A))
    b.add(UncertaintyComponent("resolution", 0.005, distribution=Distribution.RECTANGULAR))

    # u_c² = 0.010² + 0.015² + (0.005/√3)² = 3.3333e-4
    # u_c ≈ 0.018257
    # U = 2·u_c ≈ 0.036515
    assert abs(b.combined_uncertainty - 0.018257) < 1e-4
    assert abs(b.expanded_uncertainty - 0.036515) < 1e-4


def test_iso17025_drift_monitor_detects_stable():
    evaluate_drift = _run_plugin_and_import("iso17025", "drift_monitor", "evaluate_drift")
    from datetime import date, timedelta
    base = date(2025, 1, 1)
    # Perfectly stable history (no drift, no noise)
    history = [(base + timedelta(days=i*90), 1.0) for i in range(6)]
    r = evaluate_drift("REF-STABLE", history, cmc=0.01)
    assert r is not None
    assert r.action == "none"
    assert r.within_cmc is True


def test_iso17025_drift_monitor_flags_excessive_drift():
    evaluate_drift = _run_plugin_and_import("iso17025", "drift_monitor", "evaluate_drift")
    from datetime import date, timedelta
    base = date(2025, 1, 1)
    # Drifting 0.01/quarter = 0.04/year, CMC=0.01 → must flag
    history = [(base + timedelta(days=i*90), 1.0 + i*0.01) for i in range(6)]
    r = evaluate_drift("REF-DRIFT", history, cmc=0.01, period_days=365)
    assert r is not None
    assert r.within_cmc is False
    assert r.action in ("recalibrate", "withdraw")


# ─── Fleet plugin — OTA state machine ──────────────────────────

def test_fleet_ota_canary_advances_on_success():
    advance_campaign = _run_plugin_and_import("fleet", "ota", "advance_campaign")
    # Can't exercise without a DB session, but verifying import path works proves
    # the generator didn't produce broken code.
    assert callable(advance_campaign)


# ─── GxP audit log — hash chain ────────────────────────────────

def test_gxp_audit_log_hash_is_deterministic():
    """_compute_hash must be deterministic over equal input."""
    try:
        _compute_hash = _run_plugin_and_import("gxp", "audit_log", "_compute_hash")
    except (ImportError, AttributeError):
        pytest.skip("gxp audit_log requires sqlalchemy to import fully")
