"""Read Pairwise70 RDA files using pyreadr (no R subprocess needed)."""
import math
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import pyreadr
except ImportError:
    pyreadr = None


def read_rda(filepath: str) -> Optional[list[dict]]:
    """Read a Pairwise70 RDA file, extract yi and vi from the primary analysis.

    The Pairwise70 format stores Cochrane review data with columns:
    - Mean, CI.start, CI.end (study-level effect on natural/raw scale)
    - Experimental.cases, Experimental.N, Control.cases, Control.N (binary)
    - Experimental.mean, Experimental.SD (continuous)

    For ratio outcomes, Mean is on the natural scale (e.g., RR=0.85),
    so we log-transform: yi = log(Mean), sei = (log(CI.hi) - log(CI.lo)) / 3.92.

    Parameters
    ----------
    filepath : str
        Path to .rda file.

    Returns
    -------
    list[dict] or None
        List of study dicts with yi, vi, study_id, measure, design_type.
        Returns None if pyreadr unavailable, file unreadable, or < 3 valid studies.
    """
    if pyreadr is None:
        return None

    path = Path(filepath)
    review_id = path.stem.split("_")[0]

    try:
        result = pyreadr.read_r(str(path))
    except Exception:
        return None

    if not result:
        return None

    df = list(result.values())[0].copy()
    # Standardize column names (handle both dot and space separators)
    df.columns = df.columns.str.replace(" ", ".", regex=False)

    # Select primary analysis (largest k among binary outcomes, then largest k overall)
    primary = _select_primary_analysis(df)
    if primary is None or len(primary) < 3:
        return None

    # Determine scale from raw data columns
    scale = _infer_scale(primary)

    # Compute yi and sei
    studies = _compute_study_dicts(primary, scale)

    return studies if len(studies) >= 3 else None


def _select_primary_analysis(df) -> Optional[object]:
    """Select the primary analysis: largest k among binary outcomes, then largest k overall."""
    import pandas as pd

    if "Analysis.group" not in df.columns or "Analysis.number" not in df.columns:
        # Single analysis file — use entire dataframe
        return df if len(df) >= 3 else None

    groups = []
    for (grp, num), sub in df.groupby(["Analysis.group", "Analysis.number"]):
        k = len(sub)
        has_binary = False
        if "Experimental.cases" in sub.columns:
            has_binary = (
                sub["Experimental.cases"].notna() & (sub["Experimental.cases"] > 0)
            ).any()
        groups.append({"grp": grp, "num": num, "k": k, "binary": has_binary})

    if not groups:
        return None

    groups_df = pd.DataFrame(groups)

    # Prefer binary outcomes with largest k
    binary = groups_df[groups_df["binary"]]
    if len(binary) > 0:
        best = binary.loc[binary["k"].idxmax()]
    else:
        best = groups_df.loc[groups_df["k"].idxmax()]

    grp, num = int(best["grp"]), int(best["num"])
    return df[(df["Analysis.group"] == grp) & (df["Analysis.number"] == num)]


def _infer_scale(primary) -> str:
    """Infer whether the outcome is on ratio or difference scale."""
    import pandas as pd

    has_binary = False
    if "Experimental.cases" in primary.columns:
        has_binary = (
            primary["Experimental.cases"].notna()
            & (primary["Experimental.cases"] > 0)
        ).any()

    has_continuous = False
    if "Experimental.mean" in primary.columns and "Experimental.SD" in primary.columns:
        exp_mean = pd.to_numeric(primary["Experimental.mean"], errors="coerce")
        exp_sd = pd.to_numeric(primary["Experimental.SD"], errors="coerce")
        has_continuous = (exp_mean.notna() & (exp_mean != 0)).any() and (
            exp_sd.notna() & (exp_sd != 0)
        ).any()

    if has_continuous and not has_binary:
        return "difference"
    elif has_binary:
        return "ratio"
    else:
        # Fallback: infer from whether any Mean values are negative
        if "Mean" in primary.columns:
            means = primary["Mean"].dropna()
            return "ratio" if len(means) > 0 and (means > 0).all() else "difference"
        return "difference"


def _compute_study_dicts(primary, scale: str) -> list[dict]:
    """Compute yi (effect size) and vi (variance) from raw data columns."""
    import pandas as pd

    studies = []
    measure = "logOR" if scale == "ratio" else "MD"

    for idx, row in primary.iterrows():
        study_label = str(row.get("Study", f"S{idx}"))
        year = row.get("Study.year", None)
        mean_val = row.get("Mean", None)
        ci_lo = row.get("CI.start", None)
        ci_hi = row.get("CI.end", None)

        # Total sample size
        n_exp = int(row["Experimental.N"]) if pd.notna(row.get("Experimental.N")) else 0
        n_ctrl = int(row["Control.N"]) if pd.notna(row.get("Control.N")) else 0

        if pd.isna(mean_val) or pd.isna(ci_lo) or pd.isna(ci_hi):
            continue

        mean_val = float(mean_val)
        ci_lo = float(ci_lo)
        ci_hi = float(ci_hi)

        if scale == "ratio":
            # Natural-scale RR/OR -> log-transform
            if mean_val <= 0 or ci_lo <= 0 or ci_hi <= 0:
                continue
            yi = math.log(mean_val)
            se = (math.log(ci_hi) - math.log(ci_lo)) / (2 * 1.96)
        else:
            # Difference scale (MD, SMD, RD)
            yi = mean_val
            se = (ci_hi - ci_lo) / (2 * 1.96)

        if se <= 0 or not math.isfinite(se) or not math.isfinite(yi):
            continue

        vi = se ** 2

        study = {
            "study_id": study_label,
            "yi": yi,
            "vi": vi,
            "measure": measure,
            "design_type": "RCT",
        }
        if pd.notna(year):
            try:
                study["year"] = int(year)
            except (ValueError, TypeError):
                pass
        if n_exp > 0:
            study["n1"] = n_exp
        if n_ctrl > 0:
            study["n2"] = n_ctrl

        # Binary event counts
        if "Experimental.cases" in primary.columns:
            ec = row.get("Experimental.cases")
            cc = row.get("Control.cases")
            if pd.notna(ec):
                try:
                    study["events1"] = int(ec)
                except (ValueError, TypeError):
                    pass
            if pd.notna(cc):
                try:
                    study["events2"] = int(cc)
                except (ValueError, TypeError):
                    pass

        studies.append(study)

    return studies
