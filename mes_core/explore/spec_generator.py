"""Generate the multiverse specification grid."""
from itertools import product
from mes_core.models import MESSpec, StudyDossier


def generate_specs(
    mes_spec: MESSpec,
    dossiers: list[StudyDossier],
    include_loo: bool = True,
    loo_cap: int = 30,
) -> list[dict]:
    """Generate all feasible spec dicts from a MESSpec + dossiers.

    Cartesian product of (estimators x ci_methods x bias_corrections
    x quality_filters x design_filters) with feasibility pruning.

    Returns list of spec dicts, each with:
        spec_id, estimator, ci_method, bias_correction, quality_filter,
        design_filter, sensitivity, study_indices.
    """
    k_total = len(dossiers)
    filter_subsets = _compute_filter_subsets(dossiers, mes_spec)

    # Build sensitivity levels
    sensitivity_levels = ["full"]
    if include_loo and "loo" in mes_spec.sensitivity:
        if k_total <= loo_cap:
            for i in range(k_total):
                sensitivity_levels.append(f"loo_{dossiers[i].study_id}")
        else:
            import random
            rng = random.Random(42)
            indices = rng.sample(range(k_total), min(loo_cap, k_total))
            for i in indices:
                sensitivity_levels.append(f"loo_{dossiers[i].study_id}")

    specs = []
    for est, ci, bc, qf, df in product(
        mes_spec.estimators,
        mes_spec.ci_methods,
        mes_spec.bias_corrections,
        mes_spec.quality_filters,
        mes_spec.design_filters,
    ):
        idx_key = (qf, df)
        if idx_key not in filter_subsets:
            continue
        base_indices = filter_subsets[idx_key]

        for sens in sensitivity_levels:
            indices = base_indices.copy()
            if sens.startswith("loo_"):
                loo_id = sens[4:]
                indices = [i for i in indices if dossiers[i].study_id != loo_id]

            k = len(indices)
            if k < 2:
                continue
            # FE + trim-fill is redundant
            if bc == "trim-fill" and (k < 5 or est == "FE"):
                continue
            if bc == "selection-model" and k < 10:
                continue

            spec_id = f"{est}_{ci}_{bc}_{qf}_{df}_{sens}"
            specs.append({
                "spec_id": spec_id,
                "estimator": est,
                "ci_method": ci,
                "bias_correction": bc,
                "quality_filter": qf,
                "design_filter": df,
                "sensitivity": sens,
                "study_indices": indices,
            })
    return specs


def _compute_filter_subsets(
    dossiers: list[StudyDossier], mes_spec: MESSpec,
) -> dict[tuple[str, str], list[int]]:
    """Pre-compute study index subsets for each (quality_filter, design_filter) pair."""
    subsets = {}
    for qf in mes_spec.quality_filters:
        for df in mes_spec.design_filters:
            indices = []
            for i, d in enumerate(dossiers):
                if not _passes_quality(d, qf):
                    continue
                if not _passes_design(d, df):
                    continue
                indices.append(i)
            if len(indices) >= 2:
                subsets[(qf, df)] = indices
    return subsets


def _passes_quality(d: StudyDossier, qf: str) -> bool:
    """Check if a study passes a quality filter."""
    if qf == "all":
        return True
    if d.rob is None:
        return False
    if qf == "exclude-high-rob":
        return d.rob.overall != "high"
    if qf == "low-rob-only":
        return d.rob.overall == "low"
    return True


def _passes_design(d: StudyDossier, df: str) -> bool:
    """Check if a study passes a design filter."""
    if df == "all":
        return True
    if df == "rct-quasi":
        return d.design_tier <= 2
    if df == "rct-only":
        return d.design_tier == 1
    return True
