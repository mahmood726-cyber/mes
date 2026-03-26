"""Confidence interval methods for pooled meta-analysis estimates."""
import numpy as np
from scipy import stats


def wald_ci(theta: float, se: float, alpha: float = 0.05) -> tuple[float, float, float]:
    """Normal-approximation (Wald) confidence interval.

    Returns (ci_lo, ci_hi, p_value).
    """
    z_crit = stats.norm.ppf(1 - alpha / 2)
    ci_lo = theta - z_crit * se
    ci_hi = theta + z_crit * se
    z = theta / se if se > 1e-30 else 0.0
    p = 2.0 * stats.norm.sf(abs(z))
    return float(ci_lo), float(ci_hi), float(p)


def hksj_ci(theta: float, se: float, yi: np.ndarray, vi: np.ndarray,
            tau2: float, k: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """Hartung-Knapp-Sidik-Jonkman (HKSJ) confidence interval.

    Adjusts the standard error by the q-hat correction factor
    and uses t-distribution with k-1 degrees of freedom.
    The q-hat correction is floored at 1.0 so the HKSJ interval
    is always at least as wide as the t-distribution interval.

    Returns (ci_lo, ci_hi, p_value).
    """
    if k < 2:
        return wald_ci(theta, se, alpha)

    wi = 1.0 / (vi + tau2)
    resid_sq = wi * (yi - theta) ** 2
    q_hat = float(np.sum(resid_sq)) / (k - 1)
    q_hat = max(q_hat, 1.0)  # floor at 1

    se_adj = se * np.sqrt(q_hat)
    t_crit = stats.t.ppf(1 - alpha / 2, df=k - 1)
    ci_lo = theta - t_crit * se_adj
    ci_hi = theta + t_crit * se_adj
    t_stat = theta / se_adj if se_adj > 1e-30 else 0.0
    p = 2.0 * stats.t.sf(abs(t_stat), df=k - 1)
    return float(ci_lo), float(ci_hi), float(p)


def tdist_ci(theta: float, se: float, k: int, alpha: float = 0.05) -> tuple[float, float, float]:
    """t-distribution confidence interval with k-1 degrees of freedom.

    Like Wald but uses t-distribution instead of normal, producing
    wider intervals especially for small k.

    Returns (ci_lo, ci_hi, p_value).
    """
    if k < 2:
        return wald_ci(theta, se, alpha)

    t_crit = stats.t.ppf(1 - alpha / 2, df=k - 1)
    ci_lo = theta - t_crit * se
    ci_hi = theta + t_crit * se
    t_stat = theta / se if se > 1e-30 else 0.0
    p = 2.0 * stats.t.sf(abs(t_stat), df=k - 1)
    return float(ci_lo), float(ci_hi), float(p)
