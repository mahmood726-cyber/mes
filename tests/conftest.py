import pytest
import numpy as np


@pytest.fixture
def bcg_studies():
    """BCG vaccine dataset — 13 RCTs, logRR scale.

    Canonical data from metafor::dat.bcg (Colditz et al., 1994).
    Computed via escalc(measure='RR', ai=tpos, bi=tneg, ci=cpos, di=cneg).
    R parity: FE theta ~ -0.4303, DL theta ~ -0.7141, DL tau2 ~ 0.3088.
    """
    yi = np.array([
        -0.8893, -1.5854, -1.3481, -1.4416, -0.2175,
        -0.7861, -1.6209,  0.0120, -0.4694, -1.3713,
        -0.3394,  0.4459, -0.0173,
    ])
    vi = np.array([
        0.3256, 0.1946, 0.4154, 0.0200, 0.0512,
        0.0069, 0.2230, 0.0040, 0.0564, 0.0730,
        0.0124, 0.5325, 0.0714,
    ])
    labels = [
        "Aronson1948", "Ferguson1949", "Rosenthal1960", "Hart1977",
        "Frimodt1973", "Stein1953", "Vandiviere1973", "TPT_Madras1980",
        "Coetzee1968", "Comstock1974", "Comstock1976", "Comstock_etal1976",
        "Shapiro1998",
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
