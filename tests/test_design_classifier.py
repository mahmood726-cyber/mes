# tests/test_design_classifier.py
from mes_core.assess.design_classifier import classify_design


def test_rct_tier1():
    assert classify_design("RCT") == ("RCT", 1)


def test_quasi_tier2():
    assert classify_design("quasi-experimental") == ("quasi-experimental", 2)


def test_mr_tier2():
    assert classify_design("MR") == ("MR", 2)


def test_cohort_tier3():
    assert classify_design("cohort") == ("cohort", 3)


def test_case_control_tier3():
    assert classify_design("case-control") == ("case-control", 3)


def test_cross_sectional_tier3():
    assert classify_design("cross-sectional") == ("cross-sectional", 3)


def test_unknown_defaults_rct():
    assert classify_design(None) == ("RCT", 1)


def test_case_insensitive():
    assert classify_design("rct") == ("RCT", 1)
