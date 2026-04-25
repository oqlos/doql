"""Drift report JSON export."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from opstree.drift.detector import DriftReport


def _report_to_json(report: "DriftReport", intended_file: Path, target: str) -> dict:
    """Serialise a :class:`DriftReport` to plain dicts.

    ``DriftReport`` is a ``@dataclass``; ``Change`` is a frozen dataclass.
    ``dataclasses.asdict`` would work but we spell it out so the shape is
    stable and documented as the public contract for ``--json`` consumers.
    """
    return {
        "intended_file": str(intended_file),
        "target": target,
        "intended_source": report.intended_source,
        "actual_target": report.actual_target,
        "has_drift": report.has_drift,
        "summary": report.summary,
        "changes": [
            {
                "layer_id": c.layer_id,
                "path": c.path,
                "type": c.type,
                "old_value": c.old_value,
                "new_value": c.new_value,
            }
            for c in report.changes
        ],
    }
