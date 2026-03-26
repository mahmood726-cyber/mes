"""TruthCert certification for MES bundles."""
import hashlib
import json
from datetime import datetime, timezone


def certify(
    input_hash: str,
    spec_hash: str,
    n_specs: int,
    n_feasible: int,
    n_errors: int,
    verdict_class: str,
) -> dict:
    """Produce a TruthCert certification bundle.

    Returns PASS, WARN, or REJECT based on error/infeasible rates.
    """
    infeasible_rate = 1 - (n_feasible / max(1, n_specs))
    error_rate = n_errors / max(1, n_feasible)

    if error_rate > 0.05:
        status = "REJECT"
        reason = f"Error rate {error_rate:.1%} exceeds 5% threshold"
    elif infeasible_rate > 0.10:
        status = "WARN"
        reason = f"Infeasible rate {infeasible_rate:.1%} exceeds 10% (sparse data)"
    else:
        status = "PASS"
        reason = "All checks passed"

    bundle = {
        "certification": status,
        "reason": reason,
        "input_hash": input_hash,
        "spec_hash": spec_hash,
        "n_specs": n_specs,
        "n_feasible": n_feasible,
        "n_errors": n_errors,
        "verdict_class": verdict_class,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "software_version": "mes-core 0.1.0",
    }

    bundle_json = json.dumps(bundle, sort_keys=True)
    bundle["bundle_hash"] = hashlib.sha256(bundle_json.encode()).hexdigest()

    return bundle
