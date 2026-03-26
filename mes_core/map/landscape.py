"""Evidence landscape synthesis — combines all MAP modules."""
from mes_core.models import SpecResult, MESVerdict
from mes_core.map.concordance import compute_concordance
from mes_core.map.classifier import classify_robustness, conditional_robustness
from mes_core.map.influence import decompose_influence
from mes_core.map.boundaries import find_boundaries


def synthesize_verdict(
    results: list[SpecResult], mcid: float | None = None
) -> MESVerdict:
    """Produce a full MES verdict from specification results."""
    conc = compute_concordance(results, mcid=mcid)
    overall_class = classify_robustness(conc.C_sig)
    cond = conditional_robustness(results)
    eta2 = decompose_influence(results)

    dominant_dim = max(eta2, key=eta2.get) if eta2 else "none"
    dominant_eta2 = eta2.get(dominant_dim, 0.0)

    bounds = find_boundaries(results)

    feasible = [r for r in results if r.converged]
    pi_null = (
        sum(1 for r in feasible if r.pi_lo <= 0 <= r.pi_hi) / max(1, len(feasible))
    )

    return MESVerdict(
        overall_class=overall_class,
        overall_c_sig=conc.C_sig,
        conditional=cond,
        dominant_dimension=dominant_dim,
        dominant_eta2=dominant_eta2,
        certification="PENDING",
        eta2_all=eta2,
        boundaries=bounds,
        prediction_null_rate=round(pi_null, 4),
        concordance={
            "C_dir": conc.C_dir,
            "C_sig": conc.C_sig,
            "C_full": conc.C_full,
            "n_feasible": conc.n_feasible,
        },
    )
