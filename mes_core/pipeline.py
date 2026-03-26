"""MES end-to-end pipeline: ASSESS -> EXPLORE -> MAP -> CERTIFY."""
import hashlib
import json

from mes_core.models import MESSpec, MESVerdict
from mes_core.assess.dossier_builder import build_dossiers
from mes_core.explore.executor import execute_multiverse
from mes_core.map.landscape import synthesize_verdict
from mes_core.map.certifier import certify


def run_mes(
    studies: list[dict],
    mes_spec: MESSpec | None = None,
    include_loo: bool = True,
    mcid: float | None = None,
) -> MESVerdict:
    """Run the full MES pipeline on a list of study dicts.

    Parameters
    ----------
    studies : list[dict]
        Each dict must have study_id, yi, vi. Optional: measure, design_type, year, etc.
    mes_spec : MESSpec | None
        Multiverse specification. Uses defaults if None.
    include_loo : bool
        Whether to include leave-one-out sensitivity analyses.
    mcid : float | None
        Minimum clinically important difference for concordance (optional).

    Returns
    -------
    MESVerdict
        Full evidence landscape verdict with certification.
    """
    if mes_spec is None:
        mes_spec = MESSpec()

    # --- Provenance hashes ---
    input_hash = hashlib.sha256(
        json.dumps(studies, sort_keys=True).encode()
    ).hexdigest()[:16]
    spec_hash = hashlib.sha256(
        json.dumps(
            {
                "estimators": mes_spec.estimators,
                "ci_methods": mes_spec.ci_methods,
                "bias_corrections": mes_spec.bias_corrections,
                "quality_filters": mes_spec.quality_filters,
                "design_filters": mes_spec.design_filters,
                "alpha": mes_spec.alpha,
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()[:16]

    # --- Phase 1: ASSESS ---
    dossiers, bias_profile = build_dossiers(studies)

    # --- Phase 2: EXPLORE ---
    from mes_core.explore.spec_generator import generate_specs
    all_specs = generate_specs(mes_spec, dossiers, include_loo=include_loo)
    n_specs_generated = len(all_specs)
    results = execute_multiverse(mes_spec, dossiers, include_loo=include_loo)

    # --- Phase 3: MAP ---
    verdict = synthesize_verdict(results, mcid=mcid)

    # --- Phase 4: CERTIFY ---
    # Use generated spec count (accounts for feasibility pruning), not theoretical max
    n_errors = sum(1 for r in results if not r.converged)
    cert = certify(
        input_hash=input_hash,
        spec_hash=spec_hash,
        n_specs=n_specs_generated,
        n_feasible=len(results),
        n_errors=n_errors,
        verdict_class=verdict.overall_class,
    )
    verdict.certification = cert["certification"]

    return verdict
