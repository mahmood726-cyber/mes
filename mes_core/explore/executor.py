"""Execute the multiverse of specifications."""
import numpy as np
from scipy import stats
from mes_core.models import MESSpec, SpecResult, StudyDossier
from mes_core.explore import estimators as est_mod
from mes_core.explore.ci_methods import wald_ci, hksj_ci, tdist_ci
from mes_core.explore.bias_corrections import trim_fill, pet_peese, selection_model
from mes_core.explore.spec_generator import generate_specs

_ESTIMATORS = {
    "FE": est_mod.fe,
    "DL": est_mod.dl,
    "REML": est_mod.reml,
    "PM": est_mod.pm,
    "SJ": est_mod.sj,
    "ML": est_mod.ml,
}


def execute_multiverse(
    mes_spec: MESSpec,
    dossiers: list[StudyDossier],
    include_loo: bool = True,
) -> list[SpecResult]:
    """Run every feasible spec and collect results.

    Returns list of SpecResult (one per successfully executed spec).
    """
    specs = generate_specs(mes_spec, dossiers, include_loo=include_loo)
    results = []
    for spec in specs:
        result = _run_single_spec(spec, dossiers, mes_spec.alpha)
        if result is not None:
            results.append(result)
    return results


def _run_single_spec(spec: dict, dossiers: list[StudyDossier], alpha: float):
    """Execute a single specification dict and return a SpecResult (or None)."""
    indices = spec["study_indices"]
    yi = np.array([dossiers[i].yi for i in indices])
    vi = np.array([dossiers[i].vi for i in indices])
    k = len(yi)

    try:
        bc = spec["bias_correction"]
        bc_result = None

        # --- Bias correction (pre-estimation adjustments) ---
        if bc == "trim-fill":
            bc_result = trim_fill(yi, vi)
            if bc_result["theta_adj"] is None:
                return None
            yi = bc_result["yi_aug"]
            vi = bc_result["vi_aug"]
            k = len(yi)
        elif bc == "PET-PEESE":
            bc_result = pet_peese(yi, vi)
        elif bc == "selection-model":
            bc_result = selection_model(yi, vi)

        # --- Estimate tau2 + theta ---
        est_fn = _ESTIMATORS.get(spec["estimator"])
        if est_fn is None:
            return None
        tau2, theta, se = est_fn(yi, vi)

        # --- Apply post-estimation bias adjustments ---
        if bc in ("PET-PEESE", "selection-model") and bc_result and bc_result["theta_adj"] is not None:
            theta = bc_result["theta_adj"]
            if bc_result.get("se_adj") is not None:
                se = bc_result["se_adj"]

        # --- Confidence interval ---
        ci_method = spec["ci_method"]
        if ci_method == "Wald":
            ci_lo, ci_hi, p_value = wald_ci(theta, se, alpha)
        elif ci_method == "HKSJ":
            ci_lo, ci_hi, p_value = hksj_ci(theta, se, yi, vi, tau2, k, alpha)
        elif ci_method == "t-dist":
            ci_lo, ci_hi, p_value = tdist_ci(theta, se, k, alpha)
        else:
            return None

        # --- Prediction interval ---
        if k >= 3 and tau2 > 0:
            t_crit_pi = stats.t.ppf(1 - alpha / 2, df=k - 2)
            pi_se = np.sqrt(tau2 + se ** 2)
            pi_lo = theta - t_crit_pi * pi_se
            pi_hi = theta + t_crit_pi * pi_se
        else:
            pi_lo, pi_hi = ci_lo, ci_hi

        # --- Heterogeneity (I-squared) ---
        I2 = max(0.0, 1.0 - (k - 1) / max(1e-30, _cochran_q(yi, vi))) if k >= 2 else 0.0

        # --- Significance + direction ---
        significant = p_value < alpha
        if abs(theta) < 1e-10:
            direction = "null"
        elif theta > 0:
            direction = "positive"
        else:
            direction = "negative"

        return SpecResult(
            spec_id=spec["spec_id"],
            estimator=spec["estimator"],
            ci_method=ci_method,
            bias_correction=bc,
            quality_filter=spec["quality_filter"],
            design_filter=spec["design_filter"],
            sensitivity=spec["sensitivity"],
            theta=float(theta),
            se=float(se),
            ci_lo=float(ci_lo),
            ci_hi=float(ci_hi),
            p_value=float(p_value),
            tau2=float(tau2),
            I2=float(I2),
            k=k,
            pi_lo=float(pi_lo),
            pi_hi=float(pi_hi),
            significant=significant,
            direction=direction,
        )
    except (ValueError, FloatingPointError, ZeroDivisionError) as e:
        return SpecResult(
            spec_id=spec["spec_id"],
            estimator=spec["estimator"],
            ci_method=spec["ci_method"],
            bias_correction=spec["bias_correction"],
            quality_filter=spec["quality_filter"],
            design_filter=spec["design_filter"],
            sensitivity=spec["sensitivity"],
            theta=0.0,
            se=0.0,
            ci_lo=0.0,
            ci_hi=0.0,
            p_value=1.0,
            tau2=0.0,
            I2=0.0,
            k=0,
            pi_lo=0.0,
            pi_hi=0.0,
            significant=False,
            direction="null",
            converged=False,
            error=str(e),
        )


def _cochran_q(yi: np.ndarray, vi: np.ndarray) -> float:
    """Compute Cochran's Q statistic (FE weights)."""
    wi = 1.0 / vi
    theta = np.sum(wi * yi) / np.sum(wi)
    return float(np.sum(wi * (yi - theta) ** 2))
