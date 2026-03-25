"""Tests for tau-squared estimators — R parity targets from metafor::rma on BCG dataset.

Canonical BCG dataset (Colditz et al., 1994) with logRR.
R parity (metafor::rma):
    FE:   theta ~ -0.4303, tau2 = 0
    DL:   theta ~ -0.7141, tau2 ~ 0.3088
    REML: theta ~ -0.7145, tau2 ~ 0.3132
"""
import numpy as np
import pytest
from mes_core.explore.estimators import fe, dl, reml, pm, sj, ml, pool_estimate


class TestFixedEffect:
    def test_fe_theta(self, bcg_studies):
        tau2, theta, se = fe(bcg_studies["yi"], bcg_studies["vi"])
        assert tau2 == 0.0
        assert abs(theta - (-0.4303)) < 0.01

    def test_fe_small(self, small_studies):
        tau2, theta, se = fe(small_studies["yi"], small_studies["vi"])
        assert tau2 == 0.0
        assert theta < 0


class TestDerSimonianLaird:
    def test_dl_theta(self, bcg_studies):
        tau2, theta, se = dl(bcg_studies["yi"], bcg_studies["vi"])
        assert abs(theta - (-0.7141)) < 0.01
        assert abs(tau2 - 0.3088) < 0.01

    def test_dl_homogeneous(self):
        yi = np.array([-0.5, -0.5, -0.5])
        vi = np.array([0.04, 0.04, 0.04])
        tau2, theta, se = dl(yi, vi)
        assert tau2 == 0.0


class TestREML:
    def test_reml_theta(self, bcg_studies):
        tau2, theta, se = reml(bcg_studies["yi"], bcg_studies["vi"])
        assert abs(theta - (-0.7145)) < 0.02
        assert abs(tau2 - 0.3132) < 0.02

    def test_reml_converges(self, bcg_studies):
        tau2, theta, se = reml(bcg_studies["yi"], bcg_studies["vi"])
        assert se > 0


class TestPauleMandel:
    def test_pm_theta(self, bcg_studies):
        tau2, theta, se = pm(bcg_studies["yi"], bcg_studies["vi"])
        assert abs(theta - (-0.7141)) < 0.02
        assert tau2 > 0


class TestSidikJonkman:
    def test_sj_theta(self, bcg_studies):
        tau2, theta, se = sj(bcg_studies["yi"], bcg_studies["vi"])
        assert theta < 0
        assert tau2 > 0


class TestML:
    def test_ml_theta(self, bcg_studies):
        tau2, theta, se = ml(bcg_studies["yi"], bcg_studies["vi"])
        assert abs(theta - (-0.7141)) < 0.02
        assert tau2 > 0


class TestPoolEstimate:
    def test_pool_with_tau2(self, bcg_studies):
        tau2 = 0.3088
        theta, se = pool_estimate(bcg_studies["yi"], bcg_studies["vi"], tau2)
        assert abs(theta - (-0.7141)) < 0.01
        assert se > 0

    def test_pool_k1(self):
        yi = np.array([-0.5])
        vi = np.array([0.04])
        theta, se = pool_estimate(yi, vi, 0.0)
        assert theta == -0.5
        assert abs(se - 0.2) < 0.001
