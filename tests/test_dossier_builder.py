# tests/test_dossier_builder.py
import numpy as np
from mes_core.models import StudyDossier, BiasProfile
from mes_core.assess.dossier_builder import build_dossiers

def test_build_dossiers_basic(bcg_study_dicts):
    dossiers, bias = build_dossiers(bcg_study_dicts)
    assert len(dossiers) == 13
    assert all(isinstance(d, StudyDossier) for d in dossiers)
    assert isinstance(bias, BiasProfile)
    assert bias.k == 13

def test_dossier_preserves_effect(bcg_study_dicts):
    dossiers, _ = build_dossiers(bcg_study_dicts)
    assert dossiers[0].yi == bcg_study_dicts[0]["yi"]
    assert dossiers[0].vi == bcg_study_dicts[0]["vi"]

def test_dossier_classifies_design(bcg_study_dicts):
    dossiers, _ = build_dossiers(bcg_study_dicts)
    assert dossiers[0].design_type == "RCT"
    assert dossiers[0].design_tier == 1

def test_dossier_handles_missing_rob(bcg_study_dicts):
    dossiers, _ = build_dossiers(bcg_study_dicts)
    assert dossiers[0].rob is None

def test_dossier_with_rob():
    studies = [{
        "study_id": "Test1", "yi": -0.5, "vi": 0.04,
        "measure": "logOR", "design_type": "RCT",
        "rob_tool": "RoB2", "rob_randomization": "low", "rob_deviations": "low",
        "rob_missing": "low", "rob_measurement": "low", "rob_selection": "low",
    }]
    dossiers, _ = build_dossiers(studies)
    assert dossiers[0].rob is not None
    assert dossiers[0].rob.overall == "low"
