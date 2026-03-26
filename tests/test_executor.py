"""Tests for the multiverse executor."""
import pytest
import numpy as np
from mes_core.models import MESSpec, SpecResult
from mes_core.explore.executor import execute_multiverse


def test_execute_bcg(bcg_study_dicts):
    from mes_core.assess.dossier_builder import build_dossiers
    dossiers, bias = build_dossiers(bcg_study_dicts)
    spec = MESSpec()
    results = execute_multiverse(spec, dossiers, include_loo=False)
    assert len(results) > 0
    assert all(isinstance(r, SpecResult) for r in results)


def test_execute_returns_expected_fields(bcg_study_dicts):
    from mes_core.assess.dossier_builder import build_dossiers
    dossiers, _ = build_dossiers(bcg_study_dicts)
    spec = MESSpec(
        estimators=["DL"], ci_methods=["Wald"], bias_corrections=["none"],
        quality_filters=["all"], design_filters=["all"],
    )
    results = execute_multiverse(spec, dossiers, include_loo=False)
    assert len(results) == 1
    r = results[0]
    assert r.estimator == "DL"
    assert r.ci_method == "Wald"
    assert r.k == 13


def test_execute_dl_theta_matches_estimator(bcg_study_dicts):
    from mes_core.assess.dossier_builder import build_dossiers
    from mes_core.explore.estimators import dl
    dossiers, _ = build_dossiers(bcg_study_dicts)
    yi = np.array([d.yi for d in dossiers])
    vi = np.array([d.vi for d in dossiers])
    tau2_direct, theta_direct, _ = dl(yi, vi)
    spec = MESSpec(
        estimators=["DL"], ci_methods=["Wald"], bias_corrections=["none"],
        quality_filters=["all"], design_filters=["all"],
    )
    results = execute_multiverse(spec, dossiers, include_loo=False)
    assert abs(results[0].theta - theta_direct) < 1e-10
