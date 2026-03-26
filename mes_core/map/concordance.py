"""Concordance analysis — what fraction of specs agree?"""
from collections import Counter

from mes_core.models import SpecResult, ConcordanceMetrics


def compute_concordance(
    results: list[SpecResult], mcid: float | None = None
) -> ConcordanceMetrics:
    n = len(results)
    if n == 0:
        return ConcordanceMetrics(C_dir=0, C_sig=0, C_full=0, n_specs=0, n_feasible=0)

    feasible = [r for r in results if r.converged]
    n_f = len(feasible)
    if n_f == 0:
        return ConcordanceMetrics(C_dir=0, C_sig=0, C_full=0, n_specs=n, n_feasible=0)

    # Direction concordance
    dir_counts = Counter(r.direction for r in feasible)
    majority_dir = dir_counts.most_common(1)[0][0]
    C_dir = sum(1 for r in feasible if r.direction == majority_dir) / n_f

    # Significance concordance (direction + significance)
    sig_combo = Counter((r.direction, r.significant) for r in feasible)
    majority_combo = sig_combo.most_common(1)[0][0]
    C_sig = sum(
        1 for r in feasible if (r.direction, r.significant) == majority_combo
    ) / n_f

    # Full concordance (direction + significance + MCID)
    if mcid is not None:
        full_combo = Counter(
            (r.direction, r.significant, abs(r.theta) >= mcid) for r in feasible
        )
        majority_full = full_combo.most_common(1)[0][0]
        C_full = sum(
            1
            for r in feasible
            if (r.direction, r.significant, abs(r.theta) >= mcid) == majority_full
        ) / n_f
    else:
        C_full = C_sig

    return ConcordanceMetrics(
        C_dir=round(C_dir, 4),
        C_sig=round(C_sig, 4),
        C_full=round(C_full, 4),
        n_specs=n,
        n_feasible=n_f,
    )
