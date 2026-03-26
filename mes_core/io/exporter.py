"""Export MES results to JSON and CSV."""
import csv
import json
from dataclasses import asdict

from mes_core.models import SpecResult


def export_json(data: dict, filepath: str) -> None:
    """Export a dictionary to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def export_csv(results: list[SpecResult], filepath: str) -> None:
    """Export a list of SpecResult to a CSV file."""
    if not results:
        return
    fieldnames = list(asdict(results[0]).keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(asdict(r))
