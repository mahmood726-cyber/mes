"""Export MES results to JSON and CSV."""
import csv
import json
import re
from dataclasses import asdict

from mes_core.models import SpecResult


def export_json(data: dict, filepath: str) -> None:
    """Export a dictionary to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)


def _to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    components = name.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def _convert_keys(obj):
    """Recursively convert dict keys from snake_case to camelCase."""
    if isinstance(obj, dict):
        return {_to_camel(k): _convert_keys(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_keys(i) for i in obj]
    return obj


def export_json_camel(data: dict, filepath: str) -> None:
    """Export dict to JSON with camelCase keys (for browser app interop)."""
    converted = _convert_keys(data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2, default=str)


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
