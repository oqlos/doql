"""Bridge between doql and op3 (opstree).

All op3 adapters go through this module so that doql remains usable when
op3 is not installed. Nothing in this file must be imported at doql import
time — it is only loaded lazily by commands that explicitly opt-in to the
op3-backed code path (currently ``doql adopt --from-device`` and the
upcoming ``doql drift``).

Design notes
------------

- ``op3_available()`` is a hard feature-detect (``import opstree``).
- ``op3_enabled()`` is a soft, environment-driven opt-in that matches the
  convention used by ``redeploy`` (``REDEPLOY_USE_OP3``) so operators can
  keep the same muscle memory across both projects.
- ``should_use_op3()`` combines both: used by legacy code paths that need
  to pick legacy-vs-op3 at runtime. Brand-new commands that only exist
  because of op3 (e.g. ``--from-device``) should call ``op3_available()``
  directly and surface a clear install hint when it is missing.
"""
from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover — import only for type checkers
    from opstree.probes.context import ProbeContext
    from opstree.snapshot.model import Snapshot

OP3_ENABLED_ENV = "DOQL_USE_OP3"


# ---------------------------------------------------------------------------
# Feature detection
# ---------------------------------------------------------------------------


def op3_enabled() -> bool:
    """Return ``True`` if the user opted into the op3 code path.

    Reads ``DOQL_USE_OP3`` and accepts the usual truthy spellings.
    """
    raw = os.environ.get(OP3_ENABLED_ENV, "0")
    return raw.strip().lower() in ("1", "true", "yes", "on")


def op3_available() -> bool:
    """Return ``True`` if ``opstree`` (the op3 package) is importable."""
    try:
        import opstree  # noqa: F401
    except ImportError:
        return False
    return True


def should_use_op3() -> bool:
    """Use op3 only when both the flag is on and the library is available."""
    return op3_enabled() and op3_available()


# ---------------------------------------------------------------------------
# Probe bootstrapping
# ---------------------------------------------------------------------------

# Layers that doql cares about when adopting a live device. These match the
# built-in op3 layers that map cleanly onto doql's ``.doql.less`` surface
# (app metadata, services, runtime, endpoints). Physical/OS layers are left
# out on purpose — they don't correspond to any doql block type.
DEFAULT_ADOPT_LAYERS: tuple[str, ...] = (
    "runtime.container",
    "service.containers",
    "endpoint.http",
    "business.health",
)


def build_layer_tree(layer_ids: "list[str] | tuple[str, ...] | None" = None):
    """Build an :class:`opstree.LayerTree` populated with the given layers.

    Thin wrapper around :func:`opstree.build_layer_tree` that applies
    doql's default set when ``layer_ids`` is omitted.
    """
    from opstree.scanner.build import build_layer_tree as _op3_build_tree

    requested = list(layer_ids) if layer_ids else list(DEFAULT_ADOPT_LAYERS)
    return _op3_build_tree(requested)


def make_scanner(layer_ids: "list[str] | tuple[str, ...] | None" = None):
    """Return an :class:`opstree.LinearScanner` wired with built-in probes.

    Since op3 0.1.8 the upstream :func:`opstree.build_scanner` handles
    both transitive dependency resolution and per-scanner probe isolation,
    so this bridge function is now a thin wrapper. It exists only to
    inject doql's default ``DEFAULT_ADOPT_LAYERS`` set when the caller
    doesn't specify layers explicitly.
    """
    from opstree.scanner.build import build_scanner as _op3_build_scanner

    requested = list(layer_ids) if layer_ids else list(DEFAULT_ADOPT_LAYERS)
    return _op3_build_scanner(requested)


# ---------------------------------------------------------------------------
# Context helpers
# ---------------------------------------------------------------------------


def make_ssh_context(target: str, ssh_key: "str | None" = None) -> "ProbeContext":
    """Build an :class:`opstree.SSHContext` from doql-style arguments."""
    from opstree.probes.context import SSHContext

    return SSHContext(target=target, ssh_key_path=ssh_key)


def make_mock_context(responses: dict[str, tuple[str, str, int]]) -> "ProbeContext":
    """Build an :class:`opstree.MockContext` used in tests.

    ``responses`` maps a command string to an ``(stdout, stderr, returncode)``
    triple; this is the same shape redeploy's tests use so fixtures can be
    shared.
    """
    from opstree.probes.context import ExecuteResult, MockContext

    normalised = {
        cmd: ExecuteResult(stdout=out, stderr=err, returncode=rc)
        for cmd, (out, err, rc) in responses.items()
    }
    return MockContext(responses=normalised)


# ---------------------------------------------------------------------------
# Snapshot ↔ doql adapters
# ---------------------------------------------------------------------------


def snapshot_to_less(snapshot: "Snapshot", scope: "list[str] | None" = None) -> str:
    """Render an op3 :class:`Snapshot` as ``.doql.less`` text.

    Delegates to :class:`opstree.formats.less.LessAdapter`. ``scope`` is
    the same list of section names the adapter understands (``service``,
    ``runtime``, ``endpoint``, ``physical``); omit for the sensible default.
    """
    from opstree.formats.less import LessAdapter

    return LessAdapter().render(snapshot, scope=scope)


def require_op3(feature: str) -> None:
    """Raise :class:`RuntimeError` with a helpful install hint.

    Use at the top of any code path that unconditionally needs op3.
    """
    if op3_available():
        return
    raise RuntimeError(
        f"{feature} requires op3. Install with: pip install 'doql[device-adopt]'"
    )
