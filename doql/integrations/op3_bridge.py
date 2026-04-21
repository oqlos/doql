"""Bridge between doql and op3 (opstree).

All op3 adapters go through this module so that doql remains usable when
op3 is not installed.  Nothing in this file is imported at doql import
time — it is loaded lazily by commands that opt-in to the op3-backed
code path (``doql adopt --from-device``, ``doql drift``).

Feature detection, env-var opt-in, context and scanner factories are
produced by :func:`opstree.integrations.make_compat_helpers` so we don't
duplicate what ``redeploy`` already uses.  Only the doql-specific
``snapshot_to_less`` adapter lives here.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from opstree.integrations import make_compat_helpers

if TYPE_CHECKING:  # pragma: no cover — import only for type checkers
    from opstree.snapshot.model import Snapshot

OP3_ENABLED_ENV = "DOQL_USE_OP3"

# Layers that doql cares about when adopting a live device. These match
# the built-in op3 layers that map cleanly onto doql's ``.doql.less``
# surface (app metadata, services, runtime, endpoints). Physical/OS
# layers are left out on purpose — they don't correspond to any doql
# block type.
DEFAULT_ADOPT_LAYERS: tuple[str, ...] = (
    "runtime.container",
    "service.containers",
    "endpoint.http",
    "business.health",
)


# ── feature detection + factory helpers (shared via op3) ────────────────

_H = make_compat_helpers(
    env_var=OP3_ENABLED_ENV,
    default_layers=DEFAULT_ADOPT_LAYERS,
    install_hint="pip install 'doql[device-adopt]'",
)

op3_available = _H.op3_available
op3_enabled = _H.op3_enabled
should_use_op3 = _H.should_use_op3
require_op3 = _H.require_op3
make_ssh_context = _H.make_ssh_context
make_mock_context = _H.make_mock_context
make_scanner = _H.make_scanner


def build_layer_tree(layer_ids: "list[str] | tuple[str, ...] | None" = None):
    """Build an :class:`opstree.LayerTree` populated with the given layers."""
    from opstree.scanner.build import build_layer_tree as _op3_build_tree

    requested = list(layer_ids) if layer_ids else list(DEFAULT_ADOPT_LAYERS)
    return _op3_build_tree(requested)


# ── snapshot ↔ doql adapters (doql-specific) ───────────────────────────


def snapshot_to_less(snapshot: "Snapshot", scope: "list[str] | None" = None) -> str:
    """Render an op3 :class:`Snapshot` as ``.doql.less`` text.

    Delegates to :class:`opstree.formats.less.LessAdapter`. ``scope`` is
    the same list of section names the adapter understands (``service``,
    ``runtime``, ``endpoint``, ``physical``); omit for the sensible default.
    """
    from opstree.formats.less import LessAdapter

    return LessAdapter().render(snapshot, scope=scope)
