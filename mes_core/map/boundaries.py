"""Fragility boundary detection — where does the conclusion flip?"""
from collections import defaultdict

from mes_core.models import SpecResult

DIMENSIONS = [
    "estimator",
    "ci_method",
    "bias_correction",
    "quality_filter",
    "design_filter",
]


def find_boundaries(
    results: list[SpecResult], dimensions: list[str] | None = None
) -> dict[str, dict]:
    """Identify dimension levels that flip the majority conclusion."""
    if dimensions is None:
        dimensions = DIMENSIONS
    if not results:
        return {}

    feasible = [r for r in results if r.converged]
    if not feasible:
        return {}

    # Determine majority conclusion
    n_sig_neg = sum(1 for r in feasible if r.significant and r.direction == "negative")
    n_sig_pos = sum(1 for r in feasible if r.significant and r.direction == "positive")
    n_nonsig = sum(1 for r in feasible if not r.significant)
    majority_sig = n_sig_neg >= n_sig_pos and n_sig_neg >= n_nonsig
    majority_dir = "negative" if n_sig_neg >= n_sig_pos else "positive"

    boundaries = {}
    for dim in dimensions:
        groups: dict[str, list[SpecResult]] = defaultdict(list)
        for r in feasible:
            groups[getattr(r, dim)].append(r)

        if len(groups) < 2:
            continue

        flippers = {}
        for level, level_results in groups.items():
            n_agree = sum(
                1
                for r in level_results
                if r.significant == majority_sig and r.direction == majority_dir
            )
            agree_rate = n_agree / len(level_results)
            if agree_rate < 0.5:
                flippers[level] = {
                    "agree_rate": round(agree_rate, 3),
                    "n": len(level_results),
                    "flips_significance": sum(
                        1 for r in level_results if r.significant != majority_sig
                    ),
                    "flips_direction": sum(
                        1 for r in level_results if r.direction != majority_dir
                    ),
                }

        if flippers:
            boundaries[dim] = flippers

    return boundaries
