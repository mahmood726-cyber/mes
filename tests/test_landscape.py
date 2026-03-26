"""Tests for evidence landscape synthesis."""
from mes_core.models import SpecResult, MESVerdict
from mes_core.map.landscape import synthesize_verdict


def _make_fragile_results():
    results = []
    for i in range(60):
        results.append(
            SpecResult(
                spec_id=f"s{i}",
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
            )
        )
    for i in range(40):
        results.append(
            SpecResult(
                spec_id=f"s{60 + i}",
                estimator="REML",
                ci_method="HKSJ",
                bias_correction="trim-fill",
                quality_filter="all",
                design_filter="all",
                sensitivity="full",
                theta=-0.1,
                se=0.15,
                ci_lo=-0.4,
                ci_hi=0.2,
                p_value=0.5,
                tau2=0.2,
                I2=0.7,
                k=10,
                pi_lo=-1.0,
                pi_hi=0.8,
                significant=False,
                direction="negative",
            )
        )
    return results


def test_synthesize_verdict_fragile():
    results = _make_fragile_results()
    verdict = synthesize_verdict(results)
    assert isinstance(verdict, MESVerdict)
    assert verdict.overall_class == "FRAGILE"
    assert 0.5 <= verdict.overall_c_sig <= 0.7


def test_verdict_has_eta2():
    results = _make_fragile_results()
    verdict = synthesize_verdict(results)
    assert len(verdict.eta2_all) > 0
    assert verdict.dominant_dimension is not None


def test_verdict_has_boundaries():
    results = _make_fragile_results()
    verdict = synthesize_verdict(results)
    # Should detect boundaries since trim-fill flips significance
    assert len(verdict.boundaries) > 0


def test_verdict_prediction_null_rate():
    results = _make_fragile_results()
    verdict = synthesize_verdict(results)
    # 40 of 100 have pi_hi=0.8 which includes 0 => pi_null > 0
    assert verdict.prediction_null_rate > 0


def test_verdict_has_concordance():
    results = _make_fragile_results()
    verdict = synthesize_verdict(results)
    assert "C_dir" in verdict.concordance
    assert "C_sig" in verdict.concordance
    assert "C_full" in verdict.concordance
    assert verdict.concordance["C_sig"] == verdict.overall_c_sig


def test_robust_verdict():
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
            pi_hi=-0.1,
            significant=True,
            direction="negative",
        )
        for i, est in enumerate(["DL", "REML", "PM"])
    ]
    verdict = synthesize_verdict(results)
    assert verdict.overall_class == "ROBUST"
    assert verdict.overall_c_sig == 1.0
    assert verdict.prediction_null_rate == 0.0
