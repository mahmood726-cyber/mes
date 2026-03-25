"""ASSESS phase orchestrator — builds StudyDossier list from raw study dicts."""
import numpy as np
from mes_core.models import StudyDossier, BiasProfile
from mes_core.assess.design_classifier import classify_design
from mes_core.assess.rob_scorer import parse_rob_from_dict
from mes_core.assess.bias_profiler import profile_bias


def build_dossiers(studies: list[dict]) -> tuple[list[StudyDossier], BiasProfile]:
    dossiers = []
    for s in studies:
        design_type, design_tier = classify_design(s.get("design_type"))
        rob = parse_rob_from_dict(s)
        dossier = StudyDossier(
            study_id=s["study_id"], yi=s["yi"], vi=s["vi"],
            measure=s.get("measure", "logOR"),
            design_type=design_type, design_tier=design_tier, rob=rob,
            year=s.get("year"), n1=s.get("n1"), n2=s.get("n2"),
            events1=s.get("events1"), events2=s.get("events2"),
        )
        dossiers.append(dossier)
    yi = np.array([d.yi for d in dossiers])
    vi = np.array([d.vi for d in dossiers])
    bias = profile_bias(yi, vi)
    return dossiers, bias
