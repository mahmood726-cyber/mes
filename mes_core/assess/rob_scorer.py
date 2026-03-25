"""Risk of Bias scoring — RoB 2 (RCTs) and ROBINS-I (non-RCTs)."""
from mes_core.models import RoBAssessment

ROB2_DOMAINS = ["randomization", "deviations", "missing", "measurement", "selection"]


def score_rob2_overall(domains: dict[str, str]) -> str:
    values = [domains.get(d, "low") for d in ROB2_DOMAINS]
    if any(v == "high" for v in values):
        return "high"
    n_concerns = sum(1 for v in values if v == "some_concerns")
    if n_concerns >= 2:
        return "high"
    if n_concerns == 1:
        return "some_concerns"
    return "low"


ROBINS_I_DOMAINS = [
    "confounding", "selection_participants", "classification_interventions",
    "deviations", "missing_data", "measurement", "selection_reported_result",
]
_ROBINS_SEVERITY = {"low": 0, "moderate": 1, "serious": 2, "critical": 3}


def score_robins_i_overall(domains: dict[str, str]) -> str:
    severities = [_ROBINS_SEVERITY.get(domains.get(d, "low"), 0) for d in ROBINS_I_DOMAINS]
    worst = max(severities)
    if worst >= 2:
        return "high"
    if worst == 1:
        return "some_concerns"
    return "low"


def parse_rob_from_dict(data: dict) -> RoBAssessment | None:
    tool = data.get("rob_tool")
    if not tool:
        return None
    if tool == "RoB2":
        domains = {d: data[f"rob_{d}"] for d in ROB2_DOMAINS if f"rob_{d}" in data}
        overall = score_rob2_overall(domains)
    elif tool == "ROBINS-I":
        domains = {d: data[f"rob_{d}"] for d in ROBINS_I_DOMAINS if f"rob_{d}" in data}
        overall = score_robins_i_overall(domains)
    else:
        return None
    return RoBAssessment(tool=tool, overall=overall, domains=domains)
