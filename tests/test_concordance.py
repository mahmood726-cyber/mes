"""Tests for concordance analysis."""
from mes_core.models import SpecResult, ConcordanceMetrics
from mes_core.map.concordance import compute_concordance


def _make_result(theta, p, sig, direction, **overrides):
    defaults = dict(
        spec_id="test",
        estimator="DL",
        ci_method="Wald",
        bias_correction="none",
        quality_filter="all",
        design_filter="all",
        sensitivity="full",
        se=0.1,
        ci_lo=theta - 0.2,
        ci_hi=theta + 0.2,
        tau2=0.1,
        I2=0.5,
        k=10,
        pi_lo=theta - 0.5,
        pi_hi=theta + 0.5,
    )
    defaults.update(overrides)
    return SpecResult(
        theta=theta, p_value=p, significant=sig, direction=direction, **defaults
    )


def test_all_agree():
    results = [_make_result(-0.5, 0.001, True, "negative") for _ in range(100)]
    m = compute_concordance(results)
    assert m.C_dir == 1.0
    assert m.C_sig == 1.0


def test_half_disagree_on_significance():
    agree = [_make_result(-0.5, 0.001, True, "negative") for _ in range(50)]
    disagree = [_make_result(-0.1, 0.3, False, "negative") for _ in range(50)]
    m = compute_concordance(agree + disagree)
    assert m.C_dir == 1.0
    assert m.C_sig == 0.5


def test_direction_split():
    pos = [_make_result(0.5, 0.01, True, "positive") for _ in range(30)]
    neg = [_make_result(-0.5, 0.01, True, "negative") for _ in range(70)]
    m = compute_concordance(pos + neg)
    assert m.C_dir == 0.7


def test_empty_results():
    m = compute_concordance([])
    assert m.C_dir == 0
    assert m.n_specs == 0
    assert m.n_feasible == 0


def test_all_unconverged():
    results = [
        _make_result(-0.5, 0.001, True, "negative", converged=False) for _ in range(10)
    ]
    m = compute_concordance(results)
    assert m.n_specs == 10
    assert m.n_feasible == 0
    assert m.C_sig == 0


def test_mcid_concordance():
    # All significant, negative, but some below MCID threshold
    above = [_make_result(-0.5, 0.001, True, "negative") for _ in range(60)]
    below = [_make_result(-0.1, 0.04, True, "negative") for _ in range(40)]
    m = compute_concordance(above + below, mcid=0.3)
    assert m.C_dir == 1.0
    assert m.C_sig == 1.0
    assert m.C_full == 0.6  # 60/100 have |theta| >= 0.3
