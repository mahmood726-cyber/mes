"""Six tau-squared estimators + pooling utility.

Ported from FragilityAtlas (validated against metafor::rma in R).

Each estimator function takes:
    yi : np.ndarray  — effect sizes
    vi : np.ndarray  — sampling variances (sei²)
and returns:
    (tau2, theta, se) — between-study variance, pooled estimate, standard error

R parity targets (BCG dataset, 13 studies, logRR):
    FE:   theta ≈ -0.4361, tau2 = 0
    DL:   theta ≈ -0.7145, tau2 ≈ 0.3132
    REML: theta ≈ -0.7141, tau2 ≈ 0.3088
"""

import math
import numpy as np


# ---------------------------------------------------------------------------
# Pooling helper
# ---------------------------------------------------------------------------

def pool_estimate(yi: np.ndarray, vi: np.ndarray, tau2: float) -> tuple[float, float]:
    """Compute pooled theta and SE given tau2.

    Returns (theta, se).
    """
    wi = 1.0 / (vi + tau2)
    theta = float(np.sum(wi * yi) / np.sum(wi))
    se = float(1.0 / math.sqrt(np.sum(wi)))
    return theta, se


# ---------------------------------------------------------------------------
# Fixed Effect (FE)
# ---------------------------------------------------------------------------

def fe(yi: np.ndarray, vi: np.ndarray) -> tuple[float, float, float]:
    """Fixed-effect model (tau2 = 0)."""
    theta, se = pool_estimate(yi, vi, 0.0)
    return 0.0, theta, se


# ---------------------------------------------------------------------------
# DerSimonian-Laird (DL)
# ---------------------------------------------------------------------------

def dl(yi: np.ndarray, vi: np.ndarray) -> tuple[float, float, float]:
    """DerSimonian-Laird moment estimator (1986)."""
    k = len(yi)
    wi = 1.0 / vi

    # FE pooled estimate
    theta_fe = float(np.sum(wi * yi) / np.sum(wi))

    # Cochran's Q
    Q = float(np.sum(wi * (yi - theta_fe) ** 2))

    # DL constant
    C = float(np.sum(wi) - np.sum(wi ** 2) / np.sum(wi))

    if C <= 0:
        tau2 = 0.0
    else:
        tau2 = max(0.0, (Q - (k - 1)) / C)

    theta, se = pool_estimate(yi, vi, tau2)
    return tau2, theta, se


# ---------------------------------------------------------------------------
# Internal DL tau2 (used as starting value for iterative methods)
# ---------------------------------------------------------------------------

def _dl_tau2(yi: np.ndarray, vi: np.ndarray) -> float:
    """Compute DL tau2 estimate (internal helper)."""
    k = len(yi)
    wi = 1.0 / vi
    theta_fe = float(np.sum(wi * yi) / np.sum(wi))
    Q = float(np.sum(wi * (yi - theta_fe) ** 2))
    C = float(np.sum(wi) - np.sum(wi ** 2) / np.sum(wi))
    if C <= 0:
        return 0.0
    return max(0.0, (Q - (k - 1)) / C)


# ---------------------------------------------------------------------------
# REML — Restricted Maximum Likelihood (Fisher scoring)
# ---------------------------------------------------------------------------

def reml(yi: np.ndarray, vi: np.ndarray,
         max_iter: int = 100, tol: float = 1e-8) -> tuple[float, float, float]:
    """Restricted Maximum Likelihood via Fisher scoring (Viechtbauer 2005).

    Falls back to DL on non-convergence.
    """
    k = len(yi)
    tau2 = max(0.0, _dl_tau2(yi, vi))
    converged = False

    for _ in range(max_iter):
        wi = 1.0 / (vi + tau2)
        theta = float(np.sum(wi * yi) / np.sum(wi))
        resid = yi - theta

        # REML gradient (score)
        gradient = (-0.5 * np.sum(wi)
                    + 0.5 * np.sum(wi ** 2 * resid ** 2)
                    + 0.5 * np.sum(wi ** 2) / np.sum(wi))

        # Fisher information
        fisher_info = (0.5 * np.sum(wi ** 2)
                       - 2.0 * 0.5 * np.sum(wi ** 3) / np.sum(wi)
                       + 0.5 * (np.sum(wi ** 2) / np.sum(wi)) ** 2)

        if fisher_info <= 0:
            break

        tau2_new = tau2 + float(gradient) / float(fisher_info)
        tau2_new = max(0.0, tau2_new)

        if abs(tau2_new - tau2) < tol:
            tau2 = tau2_new
            converged = True
            break
        tau2 = tau2_new
    else:
        # max_iter exhausted without convergence — fall back to DL
        import sys
        print(f"Warning: REML did not converge in {max_iter} iterations "
              f"(tau2={tau2:.6f}), falling back to DL", file=sys.stderr)
        tau2 = _dl_tau2(yi, vi)

    theta, se = pool_estimate(yi, vi, tau2)
    return tau2, theta, se


# ---------------------------------------------------------------------------
# Paule-Mandel (PM)
# ---------------------------------------------------------------------------

def pm(yi: np.ndarray, vi: np.ndarray,
       max_iter: int = 100, tol: float = 1e-8) -> tuple[float, float, float]:
    """Paule-Mandel iterative estimator (1982).

    Solves Q*(tau2) = k - 1. Falls back to DL on non-convergence.
    """
    k = len(yi)
    tau2 = max(0.0, _dl_tau2(yi, vi))

    for _ in range(max_iter):
        wi = 1.0 / (vi + tau2)
        theta = float(np.sum(wi * yi) / np.sum(wi))
        Q_star = float(np.sum(wi * (yi - theta) ** 2))

        # PM criterion: Q*(tau2) = k - 1
        if abs(Q_star - (k - 1)) < tol:
            break

        # Generalized DL-type update
        C = float(np.sum(wi) - np.sum(wi ** 2) / np.sum(wi))
        if C <= 0:
            break

        tau2_new = tau2 + (Q_star - (k - 1)) / C
        tau2_new = max(0.0, tau2_new)

        if abs(tau2_new - tau2) < tol:
            tau2 = tau2_new
            break
        tau2 = tau2_new
    else:
        # Fall back to DL
        import sys
        print(f"Warning: PM did not converge in {max_iter} iterations "
              f"(tau2={tau2:.6f}), falling back to DL", file=sys.stderr)
        tau2 = _dl_tau2(yi, vi)

    theta, se = pool_estimate(yi, vi, tau2)
    return tau2, theta, se


# ---------------------------------------------------------------------------
# Sidik-Jonkman (SJ)
# ---------------------------------------------------------------------------

def sj(yi: np.ndarray, vi: np.ndarray) -> tuple[float, float, float]:
    """Sidik-Jonkman one-step estimator (2005).

    Uses the multiplicative update: tau2 = tau2_0 * Q/(k-1),
    matching metafor::rma(method='SJ').
    """
    k = len(yi)
    if k < 2:
        theta, se = pool_estimate(yi, vi, 0.0)
        return 0.0, theta, se

    # Initial tau2 from unweighted residual variance
    theta_uw = float(np.mean(yi))
    tau2_0 = float(np.sum((yi - theta_uw) ** 2) / (k - 1))

    # Compute Q with weights based on tau2_0
    wi = 1.0 / (vi + tau2_0)
    theta_tmp = float(np.sum(wi * yi) / np.sum(wi))
    Q = float(np.sum(wi * (yi - theta_tmp) ** 2))

    # Multiplicative one-step update (metafor formula)
    tau2 = max(0.0, tau2_0 * Q / (k - 1))

    theta, se = pool_estimate(yi, vi, tau2)
    return tau2, theta, se


# ---------------------------------------------------------------------------
# ML — Maximum Likelihood (Newton-Raphson)
# ---------------------------------------------------------------------------

def ml(yi: np.ndarray, vi: np.ndarray,
       max_iter: int = 100, tol: float = 1e-8) -> tuple[float, float, float]:
    """Maximum Likelihood via Newton-Raphson (profile log-likelihood).

    Unlike REML, ML does not include the REML correction term.
    Falls back to DL on non-convergence.
    """
    k = len(yi)
    tau2 = max(0.0, _dl_tau2(yi, vi))

    for _ in range(max_iter):
        wi = 1.0 / (vi + tau2)
        theta = float(np.sum(wi * yi) / np.sum(wi))
        resid = yi - theta

        # ML gradient (score) — no REML correction
        # d(ll)/d(tau2) = -0.5 * sum(wi) + 0.5 * sum(wi^2 * resid^2)
        gradient = float(-0.5 * np.sum(wi)
                         + 0.5 * np.sum(wi ** 2 * resid ** 2))

        # Fisher information (expected)
        # I(tau2) = 0.5 * sum(wi^2)
        fisher_info = float(0.5 * np.sum(wi ** 2))

        if fisher_info <= 0:
            break

        tau2_new = tau2 + gradient / fisher_info
        tau2_new = max(0.0, tau2_new)

        if abs(tau2_new - tau2) < tol:
            tau2 = tau2_new
            break
        tau2 = tau2_new
    else:
        import sys
        print(f"Warning: ML did not converge in {max_iter} iterations "
              f"(tau2={tau2:.6f}), falling back to DL", file=sys.stderr)
        tau2 = _dl_tau2(yi, vi)

    theta, se = pool_estimate(yi, vi, tau2)
    return tau2, theta, se
