"""Classify study design type and assign evidence tier."""

DESIGN_TIERS = {
    "RCT": 1, "quasi-experimental": 2, "MR": 2,
    "cohort": 3, "case-control": 3, "cross-sectional": 3, "ecological": 3,
}

_ALIASES = {
    "rct": "RCT", "randomized": "RCT", "randomised": "RCT",
    "quasi": "quasi-experimental", "quasi-experimental": "quasi-experimental",
    "mendelian randomization": "MR", "mendelian randomisation": "MR", "mr": "MR",
    "cohort": "cohort", "case-control": "case-control", "case control": "case-control",
    "cross-sectional": "cross-sectional", "cross sectional": "cross-sectional",
    "ecological": "ecological",
}


def classify_design(design_type: str | None) -> tuple[str, int]:
    if design_type is None:
        return ("RCT", 1)
    canonical = _ALIASES.get(design_type.strip().lower())
    if canonical is None:
        return ("RCT", 1)
    return (canonical, DESIGN_TIERS[canonical])
