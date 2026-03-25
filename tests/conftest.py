import pytest
import numpy as np


@pytest.fixture
def bcg_studies():
    """BCG vaccine dataset — 13 RCTs, logRR scale."""
    yi = np.array([
        -0.8893, -1.5856, -1.3481, -1.4416, -0.2175,
        -0.7861, -1.6209, 0.0120, -0.4717, 0.0459,
        -0.0173, -0.4340, -1.4564
    ])
    vi = np.array([
        0.0355, 0.0248, 0.0292, 0.0175, 0.0300,
        0.0116, 0.0206, 0.0470, 0.0124, 0.0616,
        0.2355, 0.0200, 0.0384
    ])
    labels = [
        "Aronson1948", "Ferguson1949", "Rosenthal1960", "Hart1977",
        "Frimodt1973", "Stein1953", "Vandiviere1973", "TPT_Madras1980",
        "Coetzee1968", "Comstock1974", "Comstock1976", "Comstock_etal1976",
        "Shapiro1998"
    ]
    return {"yi": yi, "vi": vi, "labels": labels, "k": 13, "measure": "logRR"}


@pytest.fixture
def bcg_study_dicts(bcg_studies):
    """BCG as list of study dicts (input format for ASSESS)."""
    studies = []
    for i in range(bcg_studies["k"]):
        studies.append({
            "study_id": bcg_studies["labels"][i],
            "yi": float(bcg_studies["yi"][i]),
            "vi": float(bcg_studies["vi"][i]),
            "measure": "logRR",
            "design_type": "RCT",
            "year": 1948 + i * 3,
        })
    return studies


@pytest.fixture
def small_studies():
    """Minimal 3-study dataset for edge case testing."""
    return {
        "yi": np.array([-0.5, -0.3, -0.8]),
        "vi": np.array([0.04, 0.06, 0.03]),
        "labels": ["A", "B", "C"],
        "k": 3,
        "measure": "logOR",
    }
