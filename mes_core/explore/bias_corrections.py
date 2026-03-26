"""Publication bias correction methods for the EXPLORE multiverse.

Ported from FragilityAtlas/src/corrections.py (trim-fill, PET-PEESE)
and BiasForensics/src/methods.py (selection model).
"""
import numpy as np
from scipy import stats
from mes_core.explore.estimators import dl, pool_estimate


def trim_fill(
    yi: np.ndarray, vi: np.ndarray, side: str = "auto", max_iter: int = 20,
) -> dict:
    """Duval-Tweedie L0 trim-and-fill.

    Returns dict with: k0, theta_adj, se_adj, yi_aug, vi_aug.
    Returns theta_adj=None if k < 5.
    """
    k = len(yi)
    if k < 5:
        return {"k0": 0, "theta_adj": None, "se_adj": None,
                "yi_aug": yi, "vi_aug": vi}

    # Determine asymmetry side
    tau2_init, theta_init, _ = dl(yi, vi)
    if side == "auto":
        di = yi - theta_init
        n_right = np.sum(di > 0)
        n_left = np.sum(di < 0)
        side = "right" if n_right > n_left else "left"

    yi_current = yi.copy()
    vi_current = vi.copy()
    k0_prev = -1

    for _ in range(max_iter):
        _, theta0, _ = dl(yi_current, vi_current)

        # Rank original studies by distance from center
        di = yi[:k] - theta0
        ranks = np.argsort(np.abs(di))
        signed_ranks = np.zeros(k)
        for i, r in enumerate(ranks):
            signed_ranks[r] = (i + 1) * np.sign(di[r])

        # L0 estimator for k0
        if side == "right":
            S = float(np.sum(signed_ranks[signed_ranks > 0]))
        else:
            S = float(np.sum(np.abs(signed_ranks[signed_ranks < 0])))

        k0 = max(0, int(round((4 * S - k * (k + 1)) / (2 * k + 1))))

        if k0 == k0_prev:
            break
        k0_prev = k0

        if k0 == 0:
            break

        # Impute by reflecting the k0 most extreme studies
        order = np.argsort(di)
        if side == "right":
            extreme_idx = order[-k0:]
        else:
            extreme_idx = order[:k0]

        yi_current = np.concatenate([yi, 2 * theta0 - yi[extreme_idx]])
        vi_current = np.concatenate([vi, vi[extreme_idx]])

    tau2_adj, theta_adj, se_adj = dl(yi_current, vi_current)
    return {
        "k0": k0 if k0_prev >= 0 else 0,
        "theta_adj": float(theta_adj),
        "se_adj": float(se_adj),
        "yi_aug": yi_current,
        "vi_aug": vi_current,
    }


def pet_peese(yi: np.ndarray, vi: np.ndarray) -> dict:
    """PET-PEESE conditional regression (Stanley-Doucouliagos).

    PET: yi = b0 + b1*sei + error (WLS, weights=1/vi)
    If PET p(b0) < 0.05 -> use PEESE: yi = b0 + b1*sei^2
    """
    k = len(yi)
    if k < 3:
        return {"theta_adj": None, "se_adj": None, "method_used": None}

    sei = np.sqrt(vi)
    wi = 1.0 / vi

    # PET: yi ~ sei
    theta_pet, se_pet, p_pet = _wls_intercept(yi, sei, wi, k)

    if p_pet < 0.05:
        # PEESE: yi ~ sei^2
        theta_adj, se_adj, _ = _wls_intercept(yi, vi, wi, k)
        method = "PEESE"
    else:
        theta_adj, se_adj = theta_pet, se_pet
        method = "PET"

    return {
        "theta_adj": float(theta_adj) if theta_adj is not None else None,
        "se_adj": float(se_adj) if se_adj is not None else None,
        "method_used": method,
    }


def _wls_intercept(
    y: np.ndarray, x: np.ndarray, w: np.ndarray, k: int,
) -> tuple[float, float, float]:
    """WLS regression y = a + b*x, returns (intercept, se_intercept, p_intercept)."""
    n = len(y)
    df = max(1, n - 2)
    sw = float(np.sum(w))
    swx = float(np.sum(w * x))
    swy = float(np.sum(w * y))
    swxx = float(np.sum(w * x ** 2))
    swxy = float(np.sum(w * x * y))
    denom = sw * swxx - swx ** 2

    # Near-singular check (relative threshold)
    scale_ref = max(abs(sw * swxx), abs(swx ** 2), 1e-30)
    if abs(denom) < 1e-10 * scale_ref:
        a = swy / sw if sw > 0 else 0.0
        se_a = 1.0 / np.sqrt(sw) if sw > 0 else 1.0
        t_stat = a / se_a if se_a > 0 else 0.0
        p = 2.0 * stats.t.sf(abs(t_stat), df=df)
        return float(a), float(se_a), float(p)

    a = (swxx * swy - swx * swxy) / denom
    b = (sw * swxy - swx * swy) / denom
    residuals = y - (a + b * x)
    sigma2 = float(np.sum(w * residuals ** 2) / max(n - 2, 1))
    var_a = sigma2 * swxx / denom
    se_a = np.sqrt(max(0, float(var_a)))
    if se_a < 1e-30:
        return float(a), 1e-10, 1.0
    t_stat = a / se_a
    p = 2.0 * stats.t.sf(abs(t_stat), df=df)
    return float(a), float(se_a), float(p)


def selection_model(yi: np.ndarray, vi: np.ndarray) -> dict:
    """3-parameter selection model (simplified Vevea-Hedges).

    Step-function: w(p) = 1 if p < 0.05 (two-sided), else eta.
    Profile likelihood over eta grid.
    """
    k = len(yi)
    if k < 5:
        return {"theta_adj": None, "se_adj": None, "eta": None, "lr_p": None}

    sei = np.sqrt(vi)
    eta_grid = [0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

    # Baseline (no selection): DL
    tau2_base, theta_base, _ = dl(yi, vi)
    ll_base = _log_likelihood(yi, vi, theta_base, tau2_base, eta=1.0)

    best_ll = -np.inf
    best_eta = 1.0
    best_theta = theta_base

    for eta in eta_grid:
        theta_try, tau2_try = _sel_model_fit(yi, vi, sei, eta)
        ll = _log_likelihood(yi, vi, theta_try, tau2_try, eta)
        if ll > best_ll:
            best_ll = ll
            best_eta = eta
            best_theta = theta_try

    # LR test: 2*(ll_sel - ll_base) ~ chi2(1)
    lr_stat = 2 * (best_ll - ll_base)
    lr_p = float(stats.chi2.sf(max(0, lr_stat), df=1))

    _, se_adj = pool_estimate(yi, vi, tau2_base)

    return {
        "theta_adj": float(best_theta),
        "se_adj": float(se_adj),
        "eta": float(best_eta),
        "lr_p": lr_p,
    }


def _sel_model_fit(
    yi: np.ndarray, vi: np.ndarray, sei: np.ndarray, eta: float,
) -> tuple[float, float]:
    """Fit selection model for a given eta. Returns (theta, tau2)."""
    p_values = 2.0 * stats.norm.sf(np.abs(yi / sei))
    sel_weights = np.where(p_values < 0.05, 1.0, eta)
    wi = sel_weights / vi
    sw = float(np.sum(wi))
    if sw <= 0:
        return 0.0, 0.0
    theta = float(np.sum(wi * yi) / sw)
    Q = float(np.sum(wi * (yi - theta) ** 2))
    k = len(yi)
    C = float(np.sum(wi) - np.sum(wi ** 2) / sw)
    tau2 = max(0.0, (Q - (k - 1)) / C) if C > 0 else 0.0
    return theta, tau2


def _log_likelihood(
    yi: np.ndarray, vi: np.ndarray,
    theta: float, tau2: float, eta: float,
) -> float:
    """Log-likelihood under selection model."""
    sei = np.sqrt(vi)
    total_var = vi + tau2
    ll = -0.5 * np.sum(np.log(total_var) + (yi - theta) ** 2 / total_var)
    p_values = 2.0 * stats.norm.sf(np.abs(yi / sei))
    sel_weights = np.where(p_values < 0.05, 1.0, eta)
    ll += np.sum(np.log(np.maximum(sel_weights, 1e-30)))
    return float(ll)
