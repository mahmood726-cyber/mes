"""Tests for IO — CSV reader and JSON/CSV exporter."""
import json

from mes_core.io.csv_reader import read_csv
from mes_core.io.exporter import export_json, export_csv


def test_read_csv(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text(
        "study_id,yi,vi,measure,design_type\n"
        "A,-0.5,0.04,logOR,RCT\n"
        "B,-0.3,0.06,logOR,RCT\n"
        "C,-0.8,0.03,logOR,cohort\n"
    )
    studies = read_csv(str(csv_file))
    assert len(studies) == 3
    assert studies[0]["study_id"] == "A"
    assert studies[0]["yi"] == -0.5
    assert studies[2]["design_type"] == "cohort"


def test_read_csv_with_rob(tmp_path):
    csv_file = tmp_path / "rob.csv"
    csv_file.write_text(
        "study_id,yi,vi,rob_tool,rob_D1,rob_D2,rob_overall\n"
        "X,0.1,0.02,RoB2,low,some_concerns,some_concerns\n"
    )
    studies = read_csv(str(csv_file))
    assert studies[0]["rob_tool"] == "RoB2"
    assert studies[0]["rob_D1"] == "low"
    assert studies[0]["rob_overall"] == "some_concerns"


def test_read_csv_int_fields(tmp_path):
    csv_file = tmp_path / "ints.csv"
    csv_file.write_text(
        "study_id,yi,vi,year,n1,n2,events1,events2\n"
        "S1,-0.2,0.05,2020,100,100,20,30\n"
    )
    studies = read_csv(str(csv_file))
    assert studies[0]["year"] == 2020
    assert isinstance(studies[0]["year"], int)
    assert studies[0]["n1"] == 100
    assert isinstance(studies[0]["n1"], int)


def test_export_json(tmp_path):
    data = {"overall_class": "FRAGILE", "c_sig": 0.62}
    out = tmp_path / "result.json"
    export_json(data, str(out))
    loaded = json.loads(out.read_text())
    assert loaded["overall_class"] == "FRAGILE"


def test_export_csv_results(tmp_path):
    from mes_core.models import SpecResult

    results = [
        SpecResult(
            spec_id="DL_Wald_none_all_all_full",
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
    ]
    out = tmp_path / "specs.csv"
    export_csv(results, str(out))
    content = out.read_text()
    assert "DL_Wald_none_all_all_full" in content
    assert "theta" in content.split("\n")[0]


def test_export_csv_empty(tmp_path):
    out = tmp_path / "empty.csv"
    export_csv([], str(out))
    assert not out.exists()  # No file created for empty results
