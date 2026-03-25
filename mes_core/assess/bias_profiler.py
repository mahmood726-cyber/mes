"""Review-level publication bias profiling (detection only, not correction)."""
import numpy as np
from scipy import stats
from mes_core.models import BiasProfile


def profile_bias(yi: np.ndarray, vi: np.ndarray) -> BiasProfile:
    k = len(yi)
    egger_p = _egger_test(yi, vi) if k >= 3 else None
    begg_p = _begg_test(yi, vi) if k >= 3 else None
    excess = _excess_significance(yi, vi) if k >= 3 else 0
    return BiasProfile(egger_p=egger_p, begg_p=begg_p, excess_sig_count=excess, k=k)


def _egger_test(yi: np.ndarray, vi: np.ndarray) -> float:
    sei = np.sqrt(vi)
    x = 1.0 / sei
    y = yi / sei
    n = len(yi)
    if n < 3:
        return None
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    ss_xx = np.sum((x - x_mean) ** 2)
    if ss_xx < 1e-30:
        return 1.0
    ss_xy = np.sum((x - x_mean) * (y - y_mean))
    b = ss_xy / ss_xx
    a = y_mean - b * x_mean
    residuals = y - (a + b * x)
    mse = np.sum(residuals ** 2) / (n - 2)
    se_a = np.sqrt(mse * (1.0 / n + x_mean ** 2 / ss_xx))
    if se_a < 1e-30:
        return 1.0
    t_stat = a / se_a
    p_value = 2.0 * stats.t.sf(abs(t_stat), df=n - 2)
    return float(p_value)


def _begg_test(yi: np.ndarray, vi: np.ndarray) -> float:
    wi = 1.0 / vi
    theta_fe = np.sum(wi * yi) / np.sum(wi)
    standardized = (yi - theta_fe) / np.sqrt(vi)
    tau, p_value = stats.kendalltau(standardized, vi)
    return float(p_value)


def _excess_significance(yi: np.ndarray, vi: np.ndarray) -> int:
    sei = np.sqrt(vi)
    z = np.abs(yi / sei)
    observed_sig = int(np.sum(z > 1.96))
    wi = 1.0 / vi
    theta_fe = np.sum(wi * yi) / np.sum(wi)
    expected_sig = 0.0
    for i in range(len(yi)):
        ncp = abs(theta_fe) / sei[i]
        power = 1.0 - stats.norm.cdf(1.96 - ncp)
        expected_sig += power
    return max(0, observed_sig - int(round(expected_sig)))
