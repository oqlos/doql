"""Thin wrapper that wires doql's inputs to op3's :class:`DriftDetector`.

Design notes
------------

- The *intended* state comes from a ``.doql.less`` file. We delegate
  parsing to :class:`opstree.formats.less.LessAdapter` because it already
  yields a :class:`opstree.PartialSnapshot` in exactly the shape
  :class:`opstree.DriftDetector` consumes. A future Sprint 3 will replace
  this with doql's own parser once it learns to emit PartialSnapshot.

- The *actual* state comes from :func:`doql.adopt.device_scanner.
  adopt_from_device_to_snapshot`, which is already covered by the Sprint 1
  tests. We reuse it verbatim so drift and adopt never fall out of sync.

- The *comparison* is op3's :class:`DriftDetector`. We deliberately do not
  transform the :class:`DriftReport` into a doql-specific type: doing so
  would mean re-implementing the change/summary model for no gain. The
  CLI layer is responsible for pretty-printing.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

from ..adopt.device_scanner import adopt_from_device_to_snapshot
from ..integrations.op3_bridge import require_op3

if TYPE_CHECKING:  # pragma: no cover
    from opstree.drift.detector import DriftReport
    from opstree.probes.context import ProbeContext
    from opstree.snapshot.model import PartialSnapshot


# File names considered canonical intended-state sources, in priority order.
# Only ``.doql.less`` is currently understood by the op3 adapter; the
# others are listed so we can surface a clear error rather than silently
# picking a file that can't be parsed.
_SUPPORTED_INTENDED = ("app.doql.less",)
_UNSUPPORTED_INTENDED = ("app.doql.css", "app.doql.sass", "app.doql")


def find_intended_file(directory: Path | None = None) -> Path | None:
    """Locate the canonical ``.doql.less`` under ``directory``.

    Returns ``None`` if no recognised file is present. Files whose format
    isn't yet supported by the drift detector (``.doql.css`` / ``.sass`` /
    legacy ``.doql``) are **not** returned — the CLI is expected to look
    at them separately to produce a helpful error.
    """
    base = directory or Path.cwd()
    for name in _SUPPORTED_INTENDED:
        candidate = base / name
        if candidate.is_file():
            return candidate
    return None


def _has_unsupported_intended(directory: Path) -> Path | None:
    """Return the first unsupported intended-state file, if any."""
    for name in _UNSUPPORTED_INTENDED:
        candidate = directory / name
        if candidate.is_file():
            return candidate
    return None


def parse_intended(path: Path) -> "PartialSnapshot":
    """Parse a ``.doql.less`` file into an :class:`opstree.PartialSnapshot`.

    Raises :class:`FileNotFoundError` if the file is missing,
    :class:`ValueError` for any other parse failure.
    """
    require_op3("doql drift")
    from opstree.formats.less import LessAdapter

    if not path.is_file():
        raise FileNotFoundError(f"Intended-state file not found: {path}")

    text = path.read_text(encoding="utf-8")
    try:
        partial = LessAdapter().parse(text)
    except Exception as exc:  # LessAdapter raises various exc types
        raise ValueError(f"Failed to parse {path.name}: {exc}") from exc

    # LessAdapter sets source_path=None — attach ours so the report knows
    # where the intended state came from.
    return partial.model_copy(update={"source_path": str(path)})


def detect_drift(
    target: str,
    *,
    file: Path | None = None,
    layers: list[str] | tuple[str, ...] | None = None,
    ssh_key: str | None = None,
    context_factory: Callable[[], "ProbeContext"] | None = None,
) -> "DriftReport":
    """Compare ``file`` (or auto-detected ``app.doql.less``) against ``target``.

    Parameters mirror :func:`doql.adopt.device_scanner.adopt_from_device`
    so callers can share wiring. ``context_factory`` is the same test
    seam, letting tests inject an :class:`opstree.MockContext`.

    The return type is op3's :class:`DriftReport` — doql doesn't wrap it
    because there is nothing to add.
    """
    require_op3("doql drift")
    from opstree.drift.detector import DriftDetector

    intended_path = Path(file) if file is not None else find_intended_file()
    if intended_path is None:
        raise FileNotFoundError(
            "No app.doql.less found — pass --file PATH or run in a project "
            "directory that contains one."
        )

    intended = parse_intended(intended_path)
    actual = adopt_from_device_to_snapshot(
        target,
        ssh_key=ssh_key,
        layers=layers,
        context_factory=context_factory,
    )
    return DriftDetector().detect(intended, actual)
