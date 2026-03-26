"""Tests for CI methods (Wald, HKSJ, t-distribution)."""
import numpy as np
from mes_core.explore.ci_methods import wald_ci, hksj_ci, tdist_ci


def test_wald_ci_basic():
    ci_lo, ci_hi, p = wald_ci(theta=-0.5, se=0.1, alpha=0.05)
    assert abs(ci_lo - (-0.696)) < 0.01
    assert abs(ci_hi - (-0.304)) < 0.01
    assert p < 0.001


def test_wald_ci_nonsig():
    ci_lo, ci_hi, p = wald_ci(theta=-0.1, se=0.2, alpha=0.05)
    assert ci_lo < 0 < ci_hi
    assert p > 0.05


def test_hksj_ci_wider(bcg_studies):
    from mes_core.explore.estimators import dl
    tau2, theta, se = dl(bcg_studies["yi"], bcg_studies["vi"])
    k = bcg_studies["k"]
    wald_lo, wald_hi, _ = wald_ci(theta, se, 0.05)
    hksj_lo, hksj_hi, _ = hksj_ci(theta, se, bcg_studies["yi"], bcg_studies["vi"], tau2, k, 0.05)
    assert (hksj_hi - hksj_lo) >= (wald_hi - wald_lo)


def test_tdist_ci_wider_than_wald():
    ci_wald_lo, ci_wald_hi, _ = wald_ci(-0.5, 0.15, 0.05)
    ci_t_lo, ci_t_hi, _ = tdist_ci(-0.5, 0.15, k=5, alpha=0.05)
    assert (ci_t_hi - ci_t_lo) > (ci_wald_hi - ci_wald_lo)


def test_hksj_q_hat_floor():
    yi = np.array([-0.5, -0.5, -0.5, -0.5, -0.5])
    vi = np.array([0.04, 0.04, 0.04, 0.04, 0.04])
    tau2, theta, se = 0.0, -0.5, 0.0894
    lo, hi, _ = hksj_ci(theta, se, yi, vi, tau2, 5, 0.05)
    t_lo, t_hi, _ = tdist_ci(theta, se, k=5, alpha=0.05)
    assert (hi - lo) >= (t_hi - t_lo) * 0.99
