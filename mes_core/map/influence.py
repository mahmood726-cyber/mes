"""Influence decomposition — ANOVA eta-squared per multiverse dimension."""
import numpy as np

from mes_core.models import SpecResult

DIMENSIONS = [
    "estimator",
    "ci_method",
    "bias_correction",
    "quality_filter",
    "design_filter",
]


def decompose_influence(
    results: list[SpecResult], dimensions: list[str] | None = None
) -> dict[str, float]:
    """Compute eta-squared for each multiverse dimension via one-way ANOVA."""
    if dimensions is None:
        dimensions = DIMENSIONS
    if not results:
        return {d: 0.0 for d in dimensions}

    thetas = np.array([r.theta for r in results])
    ss_total = float(np.sum((thetas - np.mean(thetas)) ** 2))

    if ss_total < 1e-30:
        return {d: 0.0 for d in dimensions}

    eta2 = {}
    for dim in dimensions:
        groups: dict[str, list[float]] = {}
        for r in results:
            level = getattr(r, dim)
            groups.setdefault(level, []).append(r.theta)

        if len(groups) < 2:
            eta2[dim] = 0.0
            continue

        grand_mean = np.mean(thetas)
        ss_between = 0.0
        for level, vals in groups.items():
            group_mean = np.mean(vals)
            ss_between += len(vals) * (group_mean - grand_mean) ** 2

        eta2[dim] = round(ss_between / ss_total, 4)

    return eta2
