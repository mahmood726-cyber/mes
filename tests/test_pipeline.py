"""Tests for end-to-end MES pipeline."""
import json
import os

from mes_core.pipeline import run_mes
from mes_core.models import MESVerdict


def test_run_mes_bcg():
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "built_in", "bcg_vaccine.json"
    )
    with open(data_path) as f:
        studies = json.load(f)
    verdict = run_mes(studies, include_loo=False)
    assert isinstance(verdict, MESVerdict)
    assert verdict.overall_class in ("ROBUST", "MODERATE", "FRAGILE", "UNSTABLE")
    assert 0 <= verdict.overall_c_sig <= 1
    assert verdict.certification in ("PASS", "WARN", "REJECT")
    assert len(verdict.eta2_all) > 0


def test_run_mes_with_loo():
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "built_in", "bcg_vaccine.json"
    )
    with open(data_path) as f:
        studies = json.load(f)
    verdict = run_mes(studies, include_loo=True)
    assert isinstance(verdict, MESVerdict)
    assert verdict.overall_c_sig > 0


def test_run_mes_small():
    studies = [
        {"study_id": "A", "yi": -0.5, "vi": 0.04, "measure": "logOR"},
        {"study_id": "B", "yi": -0.3, "vi": 0.06, "measure": "logOR"},
        {"study_id": "C", "yi": -0.8, "vi": 0.03, "measure": "logOR"},
    ]
    verdict = run_mes(studies, include_loo=False)
    assert isinstance(verdict, MESVerdict)
    assert verdict.overall_class in ("ROBUST", "MODERATE", "FRAGILE", "UNSTABLE")
