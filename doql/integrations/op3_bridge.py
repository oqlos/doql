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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover — import only for type checkers
    from opstree.probes.base import Probe
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


def _builtin_layer(layer_id: str) -> Any:
    """Look up a built-in op3 :class:`LayerDefinition` by id.

    Raises :class:`KeyError` if the layer id is not one of the built-ins.
    """
    from opstree.layers import builtin as L

    table = {
        "physical.display": L.PHYSICAL_DISPLAY,
        "physical.network": L.PHYSICAL_NETWORK,
        "physical.compute": L.PHYSICAL_COMPUTE,
        "os.kernel": L.OS_KERNEL,
        "os.config": L.OS_CONFIG,
        "runtime.container": L.RUNTIME_CONTAINER,
        "runtime.compositor": L.RUNTIME_COMPOSITOR,
        "service.containers": L.SERVICE_CONTAINERS,
        "service.systemd": L.SERVICE_SYSTEMD,
        "endpoint.http": L.ENDPOINT_HTTP,
        "endpoint.tcp": L.ENDPOINT_TCP,
        "business.health": L.BUSINESS_HEALTH,
    }
    if layer_id not in table:
        raise KeyError(f"Unknown op3 layer id: {layer_id!r}")
    return table[layer_id]


def _builtin_probes(layer_id: str) -> list["Probe"]:
    """Return a fresh list of built-in probe instances for ``layer_id``.

    op3 ships per-layer probe classes but doesn't auto-register them. We
    do the mapping here so that ``doql adopt --from-device`` is a single
    call for the user.
    """
    from opstree.probes.builtin.business_health import BusinessHealthProbe
    from opstree.probes.builtin.endpoint_http import EndpointHttpProbe
    from opstree.probes.builtin.os_linux import OsKernelProbe, OsConfigProbe
    from opstree.probes.builtin.physical_rpi import RpiPhysicalDisplayProbe
    from opstree.probes.builtin.runtime_container import RuntimeContainerProbe
    from opstree.probes.builtin.service_containers import ServiceContainersProbe

    table: dict[str, list[Any]] = {
        "physical.display": [RpiPhysicalDisplayProbe()],
        "os.kernel": [OsKernelProbe()],
        "os.config": [OsConfigProbe()],
        "runtime.container": [RuntimeContainerProbe()],
        "service.containers": [ServiceContainersProbe()],
        "endpoint.http": [EndpointHttpProbe()],
        "business.health": [BusinessHealthProbe()],
    }
    return table.get(layer_id, [])


def _resolve_dependencies(layer_ids: "list[str] | tuple[str, ...]") -> list[str]:
    """Expand ``layer_ids`` to include all transitive ``depends_on``.

    op3's :class:`LayerTree` raises ``"Cycle detected"`` when a registered
    layer references a dependency that is not itself registered (Kahn's
    algorithm stalls because the in-degree never drops to zero). Callers
    therefore want "give me endpoint.http" to transparently pull in the
    ``service.containers -> runtime.container -> os.kernel ->
    physical.compute`` chain.
    """
    resolved: list[str] = []
    seen: set[str] = set()

    def _visit(lid: str) -> None:
        if lid in seen:
            return
        seen.add(lid)
        layer = _builtin_layer(lid)  # raises KeyError for unknown ids
        for dep in layer.depends_on:
            _visit(dep)
        resolved.append(lid)

    for lid in layer_ids:
        _visit(lid)
    return resolved


def build_layer_tree(layer_ids: "list[str] | tuple[str, ...] | None" = None):
    """Build an :class:`opstree.LayerTree` populated with the given layers.

    Transitive dependencies are registered automatically — callers only
    need to list the "leaf" layers they care about. Unknown layer ids
    raise :class:`ValueError` so the caller can surface a helpful error
    instead of silently producing an empty snapshot.
    """
    from opstree.layers.tree import LayerTree

    tree = LayerTree()
    requested = list(layer_ids) if layer_ids else list(DEFAULT_ADOPT_LAYERS)
    try:
        ordered = _resolve_dependencies(requested)
    except KeyError as exc:
        raise ValueError(str(exc)) from exc
    for lid in ordered:
        tree.register(_builtin_layer(lid))
    return tree


def make_scanner(layer_ids: "list[str] | tuple[str, ...] | None" = None):
    """Return an :class:`opstree.LinearScanner` wired with built-in probes.

    op3 0.1.6 exposes :class:`ProbeRegistry` as class-level state (its
    ``register`` and ``get`` are both classmethods). To keep this function
    deterministic across calls we **reset** that class-level dict and then
    re-populate it with the probes that match ``layer_ids``. Callers that
    need isolation from this global state should build their own registry
    and assign it to ``scanner.probe_registry`` themselves.
    """
    from opstree.probes.registry import ProbeRegistry
    from opstree.scanner.linear import LinearScanner

    tree = build_layer_tree(layer_ids)
    scanner = LinearScanner(tree)

    # Reset the class-level singleton so repeated make_scanner() calls
    # don't accumulate probe instances from previous invocations.
    ProbeRegistry._probes = {}  # type: ignore[attr-defined]
    for lid in tree.topological_order():
        for probe in _builtin_probes(lid):
            ProbeRegistry.register(probe)
    return scanner


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
