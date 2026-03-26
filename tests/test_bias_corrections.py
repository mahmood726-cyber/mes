# tests/test_bias_corrections.py
import numpy as np
import pytest
from mes_core.explore.bias_corrections import trim_fill, pet_peese, selection_model


class TestTrimFill:
    def test_bcg_adjusts(self, bcg_studies):
        result = trim_fill(bcg_studies["yi"], bcg_studies["vi"])
        assert result["k0"] >= 0
        assert result["theta_adj"] is not None
        assert len(result["yi_aug"]) >= len(bcg_studies["yi"])

    def test_symmetric_no_fill(self):
        yi = np.array([-0.5, -0.3, -0.7, -0.4, -0.6])
        vi = np.array([0.04, 0.04, 0.04, 0.04, 0.04])
        result = trim_fill(yi, vi)
        assert result["k0"] == 0

    def test_too_few_studies(self):
        yi = np.array([-0.5, -0.3])
        vi = np.array([0.04, 0.06])
        result = trim_fill(yi, vi)
        assert result["theta_adj"] is None


class TestPETPEESE:
    def test_bcg(self, bcg_studies):
        result = pet_peese(bcg_studies["yi"], bcg_studies["vi"])
        assert "theta_adj" in result
        assert "method_used" in result
        assert result["method_used"] in ("PET", "PEESE")

    def test_too_few(self):
        yi = np.array([-0.5, -0.3])
        vi = np.array([0.04, 0.06])
        result = pet_peese(yi, vi)
        assert result["theta_adj"] is None


class TestSelectionModel:
    def test_bcg(self, bcg_studies):
        result = selection_model(bcg_studies["yi"], bcg_studies["vi"])
        assert "theta_adj" in result
        assert "eta" in result

    def test_too_few(self):
        yi = np.array([-0.5] * 5)
        vi = np.array([0.04] * 5)
        result = selection_model(yi, vi)
        assert "theta_adj" in result
