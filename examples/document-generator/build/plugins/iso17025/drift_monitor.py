"""Drift monitoring — ISO/IEC 17025 §6.4.10 & §7.7.

Tracks reference standard behavior over time so out-of-tolerance drift triggers
an alert BEFORE it compromises measurements that depend on it.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from statistics import mean, pstdev
from typing import Optional


@dataclass
class DriftResult:
    standard_id: str
    trend_slope: float          # units per day
    residual_std: float          # dispersion around the trend line
    within_cmc: bool             # True if |slope|·period + residual_std < CMC
    action: str                  # "none" | "monitor" | "recalibrate" | "withdraw"


def evaluate_drift(
    standard_id: str,
    history: list[tuple[date, float]],     # [(measurement_date, value), ...]
    cmc: float,                             # best measurement capability
    period_days: int = 365,
) -> Optional[DriftResult]:
    """Linear-regression drift check. Returns None if fewer than 3 points."""
    if len(history) < 3:
        return None

    history_sorted = sorted(history, key=lambda p: p[0])
    t0 = history_sorted[0][0]
    xs = [(d - t0).days for d, _ in history_sorted]
    ys = [v for _, v in history_sorted]
    n = len(xs)

    # Least-squares slope
    x_mean = mean(xs)
    y_mean = mean(ys)
    num = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    den = sum((x - x_mean) ** 2 for x in xs)
    slope = num / den if den else 0.0
    intercept = y_mean - slope * x_mean

    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    residual_std = pstdev(residuals) if n >= 2 else 0.0

    projected_change = abs(slope) * period_days + residual_std
    within_cmc = projected_change < cmc

    if projected_change > cmc * 2:
        action = "withdraw"
    elif projected_change > cmc:
        action = "recalibrate"
    elif projected_change > cmc * 0.7:
        action = "monitor"
    else:
        action = "none"

    return DriftResult(
        standard_id=standard_id,
        trend_slope=slope,
        residual_std=residual_std,
        within_cmc=within_cmc,
        action=action,
    )
