import numpy as np
import pytest
from mes_core.models import (
    StudyDossier, RoBAssessment, BiasProfile,
    MESSpec, SpecResult, ConcordanceMetrics, MESVerdict,
)


def test_study_dossier_creation():
    d = StudyDossier(
        study_id="Smith2019",
        yi=-0.42, vi=0.031, measure="logOR",
        design_type="RCT", design_tier=1,
    )
    assert d.study_id == "Smith2019"
    assert d.design_tier == 1
    assert d.rob is None  # optional


def test_study_dossier_with_rob():
    rob = RoBAssessment(
        tool="RoB2",
        overall="some_concerns",
        domains={"randomization": "low", "deviations": "some_concerns",
                 "missing": "low", "measurement": "low", "selection": "low"},
    )
    d = StudyDossier(
        study_id="Smith2019",
        yi=-0.42, vi=0.031, measure="logOR",
        design_type="RCT", design_tier=1,
        rob=rob,
    )
    assert d.rob.overall == "some_concerns"


def test_mes_spec_defaults():
    spec = MESSpec()
    assert "DL" in spec.estimators
    assert "HKSJ" in spec.ci_methods
    assert spec.alpha == 0.05
    assert len(spec.estimators) == 6
    assert len(spec.ci_methods) == 3
    assert len(spec.bias_corrections) == 4
    assert len(spec.quality_filters) == 3
    assert len(spec.design_filters) == 3


def test_mes_spec_base_count():
    spec = MESSpec()
    # 6 * 3 * 4 * 3 * 3 = 648
    assert spec.base_spec_count == 648


def test_spec_result_creation():
    r = SpecResult(
        spec_id="DL_Wald_none_all_all_full",
        estimator="DL", ci_method="Wald", bias_correction="none",
        quality_filter="all", design_filter="all", sensitivity="full",
        theta=-0.38, se=0.12, ci_lo=-0.61, ci_hi=-0.15,
        p_value=0.0012, tau2=0.045, I2=0.62, k=8,
        pi_lo=-0.89, pi_hi=0.13,
        significant=True, direction="negative",
    )
    assert r.significant is True
    assert r.direction == "negative"


def test_concordance_metrics():
    m = ConcordanceMetrics(
        C_dir=0.95, C_sig=0.72, C_full=0.68,
        n_specs=648, n_feasible=612,
    )
    assert m.C_sig == 0.72


def test_mes_verdict_classification():
    v = MESVerdict(
        overall_class="FRAGILE",
        overall_c_sig=0.623,
        conditional={
            "low-rob-only": {"class": "ROBUST", "c_sig": 0.941},
            "rct-only": {"class": "MODERATE", "c_sig": 0.85},
        },
        dominant_dimension="bias_correction",
        dominant_eta2=0.36,
        certification="PASS",
    )
    assert v.overall_class == "FRAGILE"
    assert v.conditional["low-rob-only"]["class"] == "ROBUST"
