# tests/test_r_parity.py
"""R parity gate -- compare MES Python against metafor.

Requires: R 4.5.2 with metafor and jsonlite packages installed.
Skip if R not available.
"""
import subprocess
import csv
import os
import pytest
import numpy as np

RSCRIPT = r"C:\Program Files\R\R-4.5.2\bin\Rscript.exe"
R_SCRIPT = os.path.join(os.path.dirname(__file__), "..", "validation", "r_parity", "validate.R")
R_RESULTS = os.path.join(os.path.dirname(__file__), "..", "validation", "r_parity", "bcg_r_results.csv")

pytestmark = pytest.mark.skipif(
    not os.path.exists(RSCRIPT), reason="R not installed"
)


@pytest.fixture(scope="module")
def r_results():
    """Run R script and load results."""
    subprocess.run(
        [RSCRIPT, R_SCRIPT],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
        check=True, capture_output=True, text=True,
    )
    results = {}
    with open(R_RESULTS) as f:
        for row in csv.DictReader(f):
            results[row["method"]] = {
                "theta": float(row["theta"]),
                "se": float(row["se"]),
                "tau2": float(row["tau2"]),
            }
    return results


@pytest.fixture(scope="module")
def python_results():
    """Run MES Python estimators on BCG."""
    from mes_core.explore.estimators import fe, dl, reml, pm, sj, ml
    import json
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "built_in", "bcg_vaccine.json")
    with open(data_path) as f:
        studies = json.load(f)
    yi = np.array([s["yi"] for s in studies])
    vi = np.array([s["vi"] for s in studies])
    return {
        "FE": fe(yi, vi), "DL": dl(yi, vi), "REML": reml(yi, vi),
        "PM": pm(yi, vi), "SJ": sj(yi, vi), "ML": ml(yi, vi),
    }


TOL = 1e-4  # Tolerance for R parity (tighten to 1e-6 once all match)


@pytest.mark.parametrize("method", ["FE", "DL", "REML", "PM", "SJ", "ML"])
def test_theta_parity(method, r_results, python_results):
    r_theta = r_results[method]["theta"]
    py_tau2, py_theta, py_se = python_results[method]
    assert abs(py_theta - r_theta) < TOL, (
        f"{method}: Python theta={py_theta:.10f}, R theta={r_theta:.10f}, "
        f"diff={abs(py_theta - r_theta):.2e}"
    )


@pytest.mark.parametrize("method", ["FE", "DL", "REML", "PM", "SJ", "ML"])
def test_se_parity(method, r_results, python_results):
    r_se = r_results[method]["se"]
    py_tau2, py_theta, py_se = python_results[method]
    assert abs(py_se - r_se) < TOL, (
        f"{method}: Python se={py_se:.10f}, R se={r_se:.10f}, "
        f"diff={abs(py_se - r_se):.2e}"
    )


@pytest.mark.parametrize("method", ["FE", "DL", "REML", "PM", "SJ", "ML"])
def test_tau2_parity(method, r_results, python_results):
    r_tau2 = r_results[method]["tau2"]
    py_tau2, _, _ = python_results[method]
    assert abs(py_tau2 - r_tau2) < TOL, (
        f"{method}: Python tau2={py_tau2:.10f}, R tau2={r_tau2:.10f}, "
        f"diff={abs(py_tau2 - r_tau2):.2e}"
    )
