"""Tests for the multiverse spec generator."""
from mes_core.models import MESSpec, StudyDossier
from mes_core.explore.spec_generator import generate_specs


def test_default_spec_count():
    """No RoB data -> quality filters collapse to 'all' only."""
    dossiers = [
        StudyDossier(study_id=f"S{i}", yi=-0.5, vi=0.04, measure="logOR")
        for i in range(10)
    ]
    specs = generate_specs(MESSpec(), dossiers, include_loo=False)
    assert len(specs) > 0
    assert all(s["quality_filter"] == "all" for s in specs)


def test_with_loo():
    dossiers = [
        StudyDossier(study_id=f"S{i}", yi=-0.5, vi=0.04, measure="logOR")
        for i in range(5)
    ]
    specs_no_loo = generate_specs(MESSpec(), dossiers, include_loo=False)
    specs_loo = generate_specs(MESSpec(), dossiers, include_loo=True)
    assert len(specs_loo) > len(specs_no_loo)


def test_feasibility_pruning_k_threshold():
    dossiers = [
        StudyDossier(study_id="S0", yi=-0.5, vi=0.04, measure="logOR", rob=None),
        StudyDossier(study_id="S1", yi=-0.3, vi=0.06, measure="logOR", rob=None),
    ]
    specs = generate_specs(MESSpec(), dossiers, include_loo=False)
    # No RoB -> quality filters collapse; k=2 -> no sel-model, no TF
    assert all(s["bias_correction"] not in ("trim-fill", "selection-model") for s in specs)


def test_spec_has_required_fields():
    dossiers = [
        StudyDossier(study_id=f"S{i}", yi=-0.5, vi=0.04, measure="logOR")
        for i in range(5)
    ]
    specs = generate_specs(MESSpec(), dossiers, include_loo=False)
    s = specs[0]
    for field in ("estimator", "ci_method", "bias_correction", "quality_filter",
                  "design_filter", "sensitivity", "spec_id"):
        assert field in s
