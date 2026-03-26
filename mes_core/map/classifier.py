"""Robustness classification — 4-tier + conditional."""
from mes_core.models import SpecResult
from mes_core.map.concordance import compute_concordance


def classify_robustness(c_sig: float) -> str:
    """Classify robustness based on significance concordance."""
    if c_sig >= 0.90:
        return "ROBUST"
    elif c_sig >= 0.70:
        return "MODERATE"
    elif c_sig >= 0.50:
        return "FRAGILE"
    else:
        return "UNSTABLE"


def conditional_robustness(results: list[SpecResult]) -> dict[str, dict]:
    """Compute robustness conditional on quality/design filters."""
    conditions = {}

    # Quality filter conditions
    for qf in ("all", "exclude-high-rob", "low-rob-only"):
        subset = [r for r in results if r.quality_filter == qf]
        if len(subset) >= 2:
            conc = compute_concordance(subset)
            conditions[qf] = {
                "c_sig": conc.C_sig,
                "class": classify_robustness(conc.C_sig),
                "n": len(subset),
            }

    # Design filter conditions
    for df in ("all", "rct-quasi", "rct-only"):
        subset = [r for r in results if r.design_filter == df]
        if len(subset) >= 2:
            conc = compute_concordance(subset)
            conditions[df] = {
                "c_sig": conc.C_sig,
                "class": classify_robustness(conc.C_sig),
                "n": len(subset),
            }

    # Combined condition
    combined = [
        r
        for r in results
        if r.quality_filter == "low-rob-only" and r.design_filter == "rct-only"
    ]
    if len(combined) >= 2:
        conc = compute_concordance(combined)
        conditions["low-rob_rct-only"] = {
            "c_sig": conc.C_sig,
            "class": classify_robustness(conc.C_sig),
            "n": len(combined),
        }

    return conditions
