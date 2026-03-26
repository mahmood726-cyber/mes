# tests/test_integration.py
"""Integration test: full pipeline -> JSON export -> verify structure."""
import json
import os
from dataclasses import asdict
from mes_core.pipeline import run_mes


def test_full_pipeline_to_json(tmp_path):
    """BCG -> run_mes -> export -> verify all fields present."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "built_in", "bcg_vaccine.json")
    with open(data_path) as f:
        studies = json.load(f)

    verdict = run_mes(studies, include_loo=False)

    # Serialize to JSON
    verdict_dict = asdict(verdict)
    out = tmp_path / "verdict.json"
    with open(out, "w") as f:
        json.dump(verdict_dict, f, default=str)

    # Reload and verify structure
    with open(out) as f:
        loaded = json.load(f)

    assert loaded["overall_class"] in ("ROBUST", "MODERATE", "FRAGILE", "UNSTABLE")
    assert 0 <= loaded["overall_c_sig"] <= 1
    assert loaded["certification"] in ("PASS", "WARN", "REJECT")
    assert "concordance" in loaded
    assert "C_sig" in loaded["concordance"]
    assert "eta2_all" in loaded
    assert len(loaded["eta2_all"]) >= 3
    assert loaded["dominant_dimension"] in loaded["eta2_all"]


def test_camel_case_export(tmp_path):
    """Verify camelCase export works end-to-end."""
    from mes_core.io.exporter import export_json_camel
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "built_in", "bcg_vaccine.json")
    with open(data_path) as f:
        studies = json.load(f)

    verdict = run_mes(studies, include_loo=False)
    verdict_dict = asdict(verdict)

    out = tmp_path / "verdict_camel.json"
    export_json_camel(verdict_dict, str(out))

    with open(out) as f:
        loaded = json.load(f)

    # Keys should be camelCase
    assert "overallClass" in loaded
    assert "overallCSig" in loaded
    assert "dominantDimension" in loaded
    assert "eta2All" in loaded
