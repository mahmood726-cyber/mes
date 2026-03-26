"""Tests for influence decomposition."""
from mes_core.models import SpecResult
from mes_core.map.influence import decompose_influence


def _make_results_with_variance():
    results = []
    for est in ["DL", "REML"]:
        for bc in ["none", "trim-fill", "PET-PEESE"]:
            theta = -0.5 if bc == "none" else -0.1
            theta += 0.02 if est == "REML" else 0
            results.append(
                SpecResult(
                    spec_id=f"{est}_{bc}",
                    estimator=est,
                    ci_method="Wald",
                    bias_correction=bc,
                    quality_filter="all",
                    design_filter="all",
                    sensitivity="full",
                    theta=theta,
                    se=0.1,
                    ci_lo=theta - 0.2,
                    ci_hi=theta + 0.2,
                    p_value=0.01,
                    tau2=0.1,
                    I2=0.5,
                    k=10,
                    pi_lo=-1.0,
                    pi_hi=0.0,
                    significant=True,
                    direction="negative",
                )
            )
    return results


def test_influence_returns_all_dimensions():
    results = _make_results_with_variance()
    eta2 = decompose_influence(results)
    assert "estimator" in eta2
    assert "bias_correction" in eta2
    assert all(0 <= v <= 1 for v in eta2.values())


def test_bias_correction_dominant():
    results = _make_results_with_variance()
    eta2 = decompose_influence(results)
    assert eta2["bias_correction"] > eta2["estimator"]


def test_empty_results():
    eta2 = decompose_influence([])
    assert all(v == 0.0 for v in eta2.values())


def test_uniform_theta():
    """All same theta => zero variance => all eta2 = 0."""
    results = [
        SpecResult(
            spec_id=f"s{i}",
            estimator=est,
            ci_method="Wald",
            bias_correction="none",
            quality_filter="all",
            design_filter="all",
            sensitivity="full",
            theta=-0.5,
            se=0.1,
            ci_lo=-0.7,
            ci_hi=-0.3,
            p_value=0.01,
            tau2=0.1,
            I2=0.5,
            k=10,
            pi_lo=-1.0,
            pi_hi=0.0,
            significant=True,
            direction="negative",
        )
        for i, est in enumerate(["DL", "REML", "PM"])
    ]
    eta2 = decompose_influence(results)
    assert all(v == 0.0 for v in eta2.values())


def test_custom_dimensions():
    results = _make_results_with_variance()
    eta2 = decompose_influence(results, dimensions=["estimator"])
    assert "estimator" in eta2
    assert "bias_correction" not in eta2
