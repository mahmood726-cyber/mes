# tests/test_rob_scorer.py
from mes_core.models import RoBAssessment
from mes_core.assess.rob_scorer import score_rob2_overall, score_robins_i_overall, parse_rob_from_dict


def test_rob2_all_low():
    domains = {"randomization": "low", "deviations": "low", "missing": "low", "measurement": "low", "selection": "low"}
    assert score_rob2_overall(domains) == "low"


def test_rob2_one_some_concerns():
    domains = {"randomization": "low", "deviations": "some_concerns", "missing": "low", "measurement": "low", "selection": "low"}
    assert score_rob2_overall(domains) == "some_concerns"


def test_rob2_any_high():
    domains = {"randomization": "high", "deviations": "low", "missing": "low", "measurement": "low", "selection": "low"}
    assert score_rob2_overall(domains) == "high"


def test_rob2_multiple_some_concerns_is_high():
    domains = {"randomization": "some_concerns", "deviations": "some_concerns", "missing": "some_concerns", "measurement": "low", "selection": "low"}
    assert score_rob2_overall(domains) == "high"


def test_robins_i_all_low():
    domains = {"confounding": "low", "selection_participants": "low", "classification_interventions": "low",
               "deviations": "low", "missing_data": "low", "measurement": "low", "selection_reported_result": "low"}
    assert score_robins_i_overall(domains) == "low"


def test_robins_i_any_serious():
    domains = {"confounding": "serious", "selection_participants": "low", "classification_interventions": "low",
               "deviations": "low", "missing_data": "low", "measurement": "low", "selection_reported_result": "low"}
    assert score_robins_i_overall(domains) == "high"


def test_robins_i_moderate():
    domains = {"confounding": "moderate", "selection_participants": "low", "classification_interventions": "low",
               "deviations": "low", "missing_data": "low", "measurement": "low", "selection_reported_result": "low"}
    assert score_robins_i_overall(domains) == "some_concerns"


def test_parse_rob_from_dict_rob2():
    data = {"rob_tool": "RoB2", "rob_randomization": "low", "rob_deviations": "some_concerns",
            "rob_missing": "low", "rob_measurement": "low", "rob_selection": "low"}
    result = parse_rob_from_dict(data)
    assert isinstance(result, RoBAssessment)
    assert result.tool == "RoB2"
    assert result.overall == "some_concerns"


def test_parse_rob_from_dict_none():
    assert parse_rob_from_dict({}) is None
