"""Doctor report dataclasses and formatting."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Check:
    name: str
    status: str = "ok"          # ok | warn | fail | skip
    message: str = ""


@dataclass
class DoctorReport:
    checks: list[Check] = field(default_factory=list)

    def add(self, name: str, status: str, message: str = "") -> None:
        self.checks.append(Check(name, status, message))

    @property
    def ok(self) -> int:
        return sum(1 for c in self.checks if c.status == "ok")

    @property
    def warnings(self) -> int:
        return sum(1 for c in self.checks if c.status == "warn")

    @property
    def failures(self) -> int:
        return sum(1 for c in self.checks if c.status == "fail")


ICONS = {"ok": "✅", "warn": "⚠️ ", "fail": "❌", "skip": "⏭️ "}


def _print_report(report: DoctorReport) -> None:
    """Print the doctor report."""
    for c in report.checks:
        icon = ICONS.get(c.status, "?")
        msg = f"  {icon} {c.name}"
        if c.message:
            msg += f" — {c.message}"
        print(msg)
