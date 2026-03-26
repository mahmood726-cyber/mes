"""Read study data from CSV files."""
import csv


def read_csv(filepath: str) -> list[dict]:
    """Read a CSV file and return a list of study dicts.

    Expected columns: study_id, yi, vi (required).
    Optional: measure, design_type, year, n1, n2, events1, events2, rob_tool, rob_*.
    """
    studies = []
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            study = {"study_id": row["study_id"]}
            for field in ("yi", "vi", "year", "n1", "n2", "events1", "events2"):
                if field in row and row[field].strip():
                    try:
                        study[field] = float(row[field])
                        if field in ("year", "n1", "n2", "events1", "events2"):
                            study[field] = int(study[field])
                    except ValueError:
                        pass
            for field in ("measure", "design_type", "rob_tool"):
                if field in row and row[field].strip():
                    study[field] = row[field].strip()
            for key in row:
                if key.startswith("rob_") and key != "rob_tool" and row[key].strip():
                    study[key] = row[key].strip()
            studies.append(study)
    return studies
