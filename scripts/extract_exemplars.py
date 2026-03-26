"""Extract 3 exemplar datasets from Pairwise70 RDA files for MES built-in examples."""
import json
import sys
import os
import glob

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mes_core.io.rda_reader import read_rda

PAIRWISE_DIR = r"C:\Models\Pairwise70\data"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "data", "built_in")

EXEMPLARS = {
    "robust_example":   ("CD001431", 61,   1.00),
    "fragile_example":  ("CD014040", 14,   0.59),
    "unstable_example": ("CD004871",  5,   0.33),
}


def find_rda_file(review_id: str) -> str | None:
    """Locate RDA file by review ID, trying common suffixes."""
    for ext in (".RData", ".rda"):
        path = os.path.join(PAIRWISE_DIR, review_id + ext)
        if os.path.exists(path):
            return path

    # Partial match (e.g. CD001431_pub6_data.rda)
    matches = glob.glob(os.path.join(PAIRWISE_DIR, f"*{review_id}*"))
    return matches[0] if matches else None


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    success = 0

    for out_name, (review_id, expected_k, expected_csig) in EXEMPLARS.items():
        print(f"\n--- {out_name} ({review_id}, expected k={expected_k}, C_sig={expected_csig}) ---")

        path = find_rda_file(review_id)
        if path is None:
            print(f"  ERROR: No RDA file found for {review_id} in {PAIRWISE_DIR}")
            continue

        print(f"  Reading: {path}")
        studies = read_rda(path)

        if studies is None:
            print(f"  ERROR: read_rda returned None for {path}")
            continue

        k = len(studies)
        if k < 3:
            print(f"  ERROR: Only {k} valid studies extracted (need >= 3)")
            continue

        out_path = os.path.join(OUTPUT_DIR, f"{out_name}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(studies, f, indent=2)

        print(f"  Extracted {k} studies -> {out_path}")
        if abs(k - expected_k) > 5:
            print(f"  WARNING: Expected ~{expected_k} studies, got {k} (primary analysis subset)")
        success += 1

    print(f"\n=== Done: {success}/{len(EXEMPLARS)} exemplars extracted ===")
    return 0 if success == len(EXEMPLARS) else 1


if __name__ == "__main__":
    sys.exit(main())
