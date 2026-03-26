"""Tests for robustness classifier."""
from mes_core.map.classifier import classify_robustness, conditional_robustness
from mes_core.models import SpecResult


def _make_result(sig, direction, **overrides):
    defaults = dict(
        spec_id="test",
        estimator="DL",
        ci_method="Wald",
        bias_correction="none",
        quality_filter="all",
        design_filter="all",
        sensitivity="full",
        theta=-0.5,
        se=0.1,
        ci_lo=-0.7,
        ci_hi=-0.3,
        p_value=0.001 if sig else 0.3,
        tau2=0.1,
        I2=0.5,
        k=10,
        pi_lo=-1.0,
        pi_hi=0.0,
    )
    defaults.update(overrides)
    return SpecResult(significant=sig, direction=direction, **defaults)


def test_robust():
    assert classify_robustness(0.95) == "ROBUST"


def test_moderate():
    assert classify_robustness(0.75) == "MODERATE"


def test_fragile():
    assert classify_robustness(0.55) == "FRAGILE"


def test_unstable():
    assert classify_robustness(0.40) == "UNSTABLE"


def test_boundary_values():
    assert classify_robustness(0.90) == "ROBUST"
    assert classify_robustness(0.70) == "MODERATE"
    assert classify_robustness(0.50) == "FRAGILE"
    assert classify_robustness(0.49) == "UNSTABLE"


def test_conditional_robustness():
    all_specs = (
        [_make_result(True, "negative", quality_filter="all") for _ in range(50)]
        + [_make_result(False, "negative", quality_filter="all") for _ in range(50)]
        + [
            _make_result(True, "negative", quality_filter="low-rob-only")
            for _ in range(45)
        ]
        + [
            _make_result(False, "negative", quality_filter="low-rob-only")
            for _ in range(5)
        ]
    )
    cond = conditional_robustness(all_specs)
    assert "low-rob-only" in cond
    assert cond["low-rob-only"]["c_sig"] > 0.8


def test_conditional_with_design_filters():
    specs = (
        [_make_result(True, "negative", design_filter="all") for _ in range(40)]
        + [_make_result(False, "negative", design_filter="all") for _ in range(10)]
        + [_make_result(True, "negative", design_filter="rct-only") for _ in range(30)]
        + [_make_result(False, "negative", design_filter="rct-only") for _ in range(20)]
    )
    cond = conditional_robustness(specs)
    assert "all" in cond
    assert "rct-only" in cond
    assert cond["all"]["c_sig"] > cond["rct-only"]["c_sig"]
