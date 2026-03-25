# tests/test_bias_profiler.py
import numpy as np
from mes_core.models import BiasProfile
from mes_core.assess.bias_profiler import profile_bias


def test_profile_bias_bcg(bcg_studies):
    result = profile_bias(bcg_studies["yi"], bcg_studies["vi"])
    assert isinstance(result, BiasProfile)
    assert result.egger_p is not None
    assert 0 < result.egger_p < 1  # valid p-value (BCG heterogeneity is latitude-driven, not bias)
    assert result.k == 13


def test_profile_bias_symmetric():
    yi = np.array([-0.5, -0.3, -0.7, -0.4, -0.6])
    vi = np.array([0.04, 0.04, 0.04, 0.04, 0.04])
    result = profile_bias(yi, vi)
    assert result.egger_p > 0.10


def test_profile_bias_too_few():
    yi = np.array([-0.5, -0.3])
    vi = np.array([0.04, 0.06])
    result = profile_bias(yi, vi)
    assert result.egger_p is None
    assert result.k == 2
