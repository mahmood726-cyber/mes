"""Tests for fragility boundary detection."""
from mes_core.models import SpecResult
from mes_core.map.boundaries import find_boundaries


def _make_mixed_results():
    results = []
    for bc in ["none", "trim-fill"]:
        sig = bc == "none"
        results.append(
            SpecResult(
                spec_id=f"DL_Wald_{bc}",
                estimator="DL",
                ci_method="Wald",
                bias_correction=bc,
                quality_filter="all",
                design_filter="all",
                sensitivity="full",
                theta=-0.5 if sig else -0.1,
                se=0.1,
                ci_lo=-0.7,
                ci_hi=-0.3 if sig else 0.1,
                p_value=0.001 if sig else 0.3,
                tau2=0.1,
                I2=0.5,
                k=10,
                pi_lo=-1.0,
                pi_hi=0.0,
                significant=sig,
                direction="negative",
            )
        )
    return results


def test_find_boundaries_detects_flip():
    results = _make_mixed_results()
    bounds = find_boundaries(results)
    assert "bias_correction" in bounds
    bc_bound = bounds["bias_correction"]
    assert "trim-fill" in str(bc_bound)


def test_no_boundaries_when_all_agree():
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
            p_value=0.001,
            tau2=0.1,
            I2=0.5,
            k=10,
            pi_lo=-1.0,
            pi_hi=0.0,
            significant=True,
            direction="negative",
        )
        for i, est in enumerate(["DL", "REML"])
    ]
    bounds = find_boundaries(results)
    assert len(bounds) == 0


def test_empty_results():
    assert find_boundaries([]) == {}


def test_direction_flip():
    """Detect when a dimension level flips direction."""
    results = [
        SpecResult(
            spec_id="neg",
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
            p_value=0.001,
            tau2=0.1,
            I2=0.5,
            k=10,
            pi_lo=-1.0,
            pi_hi=0.0,
            significant=True,
            direction="negative",
        ),
        SpecResult(
            spec_id="pos",
            estimator="REML",
            ci_method="Wald",
            bias_correction="none",
            quality_filter="all",
            design_filter="all",
            sensitivity="full",
            theta=0.5,
            se=0.1,
            ci_lo=0.3,
            ci_hi=0.7,
            p_value=0.001,
            tau2=0.1,
            I2=0.5,
            k=10,
            pi_lo=0.0,
            pi_hi=1.0,
            significant=True,
            direction="positive",
        ),
    ]
    bounds = find_boundaries(results)
    # One of the estimators should be flagged as a flipper
    assert "estimator" in bounds
