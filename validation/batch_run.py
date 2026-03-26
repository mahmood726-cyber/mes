"""Batch MES pipeline across Pairwise70 Cochrane reviews.

Usage:
    python validation/batch_run.py                    # auto-find data, run all
    python validation/batch_run.py --max 10           # first 10 reviews
    python validation/batch_run.py --dir C:/path/data # explicit directory
"""
import os
import sys
import csv
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from mes_core.pipeline import run_mes
from mes_core.models import MESSpec
from mes_core.io.rda_reader import read_rda


# Candidate directories for Pairwise70 RDA files
_DATA_CANDIDATES = [
    r"C:\Models\Pairwise70\data",
    r"C:\FragilityAtlas\data",
    r"C:\Users\user\OneDrive - NHS\Documents\Pairwise70\data",
]


def find_data_dir() -> str | None:
    """Auto-detect Pairwise70 data directory."""
    for c in _DATA_CANDIDATES:
        if os.path.isdir(c):
            # Verify it has RDA files
            rda_count = sum(
                1 for f in os.listdir(c) if f.endswith((".rda", ".RData"))
            )
            if rda_count > 0:
                return c
    return None


def main(rda_dir: str | None = None, max_reviews: int | None = None):
    """Run the MES pipeline on all Pairwise70 reviews.

    Parameters
    ----------
    rda_dir : str | None
        Path to directory with .rda files. Auto-detected if None.
    max_reviews : int | None
        Maximum number of reviews to process. None = all.
    """
    if rda_dir is None:
        rda_dir = find_data_dir()
        if rda_dir is None:
            print("ERROR: Cannot find Pairwise70 RDA directory.")
            print("Searched:", _DATA_CANDIDATES)
            sys.exit(1)

    output_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(output_dir, exist_ok=True)

    spec = MESSpec()

    # Find RDA files
    rda_files = sorted(
        f for f in os.listdir(rda_dir) if f.endswith((".rda", ".RData"))
    )
    if max_reviews is not None:
        rda_files = rda_files[:max_reviews]

    print(f"MES Batch Validation")
    print(f"  Data directory: {rda_dir}")
    print(f"  RDA files: {len(rda_files)}")
    print(f"  Spec count (base): {spec.base_spec_count}")
    print(f"  LOO: disabled (batch mode)")
    print()

    results_summary: list[dict] = []
    t0 = time.time()

    for i, fname in enumerate(rda_files):
        filepath = os.path.join(rda_dir, fname)
        review_id = os.path.splitext(fname)[0].split("_")[0]

        # Load studies from RDA
        studies = read_rda(filepath)
        if studies is None or len(studies) < 3:
            results_summary.append({
                "review_id": review_id,
                "file": fname,
                "status": "SKIP",
                "reason": "insufficient studies" if studies is not None else "unreadable",
                "k": len(studies) if studies is not None else 0,
            })
            continue

        try:
            verdict = run_mes(studies, mes_spec=spec, include_loo=False)
            results_summary.append({
                "review_id": review_id,
                "file": fname,
                "status": "OK",
                "k": len(studies),
                "overall_class": verdict.overall_class,
                "c_sig": round(verdict.overall_c_sig, 4),
                "dominant_dim": verdict.dominant_dimension,
                "dominant_eta2": round(verdict.dominant_eta2, 4),
                "certification": verdict.certification,
                "pi_null_rate": round(verdict.prediction_null_rate, 4),
            })
        except Exception as e:
            results_summary.append({
                "review_id": review_id,
                "file": fname,
                "status": "ERROR",
                "reason": str(e)[:200],
                "k": len(studies),
            })

        if (i + 1) % 50 == 0:
            elapsed = time.time() - t0
            ok_so_far = sum(1 for r in results_summary if r["status"] == "OK")
            err_so_far = sum(1 for r in results_summary if r["status"] == "ERROR")
            print(
                f"  [{i+1}/{len(rda_files)}] "
                f"OK={ok_so_far} ERR={err_so_far} ({elapsed:.0f}s)"
            )

    elapsed = time.time() - t0

    # Write full results CSV
    out_csv = os.path.join(output_dir, "batch_results.csv")
    if results_summary:
        keys: set[str] = set()
        for row in results_summary:
            keys.update(row.keys())
        fieldnames = sorted(keys)
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results_summary)

    # --- Summary ---
    ok_results = [r for r in results_summary if r["status"] == "OK"]
    skip_count = sum(1 for r in results_summary if r["status"] == "SKIP")
    err_count = sum(1 for r in results_summary if r["status"] == "ERROR")

    print(f"\n{'=' * 50}")
    print(f"MES Batch Validation Results")
    print(f"{'=' * 50}")
    print(f"Total RDA files:  {len(rda_files)}")
    print(f"Processed (OK):   {len(ok_results)}")
    print(f"Skipped:          {skip_count}")
    print(f"Errors:           {err_count}")
    print(f"Time:             {elapsed:.1f}s ({elapsed/max(len(rda_files),1):.2f}s/review)")
    print()

    if ok_results:
        # Robustness distribution
        classes: dict[str, int] = {}
        for r in ok_results:
            c = r["overall_class"]
            classes[c] = classes.get(c, 0) + 1

        print("Robustness Distribution:")
        for cls in ("ROBUST", "MODERATE", "FRAGILE", "UNSTABLE"):
            n = classes.get(cls, 0)
            pct = 100 * n / len(ok_results)
            bar = "#" * int(pct / 2)
            print(f"  {cls:10s}  {n:4d}  ({pct:5.1f}%)  {bar}")

        # Certification breakdown
        certs: dict[str, int] = {}
        for r in ok_results:
            c = r.get("certification", "UNKNOWN")
            certs[c] = certs.get(c, 0) + 1
        print()
        print("Certification:")
        for cert_label in ("PASS", "WARN", "REJECT"):
            n = certs.get(cert_label, 0)
            pct = 100 * n / len(ok_results)
            print(f"  {cert_label:10s}  {n:4d}  ({pct:5.1f}%)")

        # C_sig statistics
        c_sigs = [r["c_sig"] for r in ok_results]
        c_sigs.sort()
        median_idx = len(c_sigs) // 2
        median_csig = c_sigs[median_idx]
        mean_csig = sum(c_sigs) / len(c_sigs)
        print()
        print(f"C_sig: mean={mean_csig:.3f}, median={median_csig:.3f}, "
              f"min={min(c_sigs):.3f}, max={max(c_sigs):.3f}")

        # Dominant dimension distribution
        dims: dict[str, int] = {}
        for r in ok_results:
            d = r.get("dominant_dim", "unknown")
            dims[d] = dims.get(d, 0) + 1
        print()
        print("Dominant Dimension:")
        for dim, n in sorted(dims.items(), key=lambda x: -x[1]):
            pct = 100 * n / len(ok_results)
            print(f"  {dim:22s}  {n:4d}  ({pct:5.1f}%)")

    if err_count > 0:
        print()
        print("Errors (first 10):")
        for r in [r for r in results_summary if r["status"] == "ERROR"][:10]:
            print(f"  {r['review_id']} (k={r['k']}): {r.get('reason', '?')}")

    print(f"\nResults saved to: {out_csv}")
    return results_summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MES Batch Validation")
    parser.add_argument("--dir", help="Path to RDA directory")
    parser.add_argument("--max", type=int, help="Max reviews to process")
    args = parser.parse_args()
    main(rda_dir=args.dir, max_reviews=args.max)
