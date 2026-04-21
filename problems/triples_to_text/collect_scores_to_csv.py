import argparse
import csv
import json
from pathlib import Path
from typing import Any


def _relative_depth(root: Path, current: Path) -> int:
    rel = current.relative_to(root)
    if rel == Path("."):
        return 0
    return len(rel.parts)


def find_score_files(root: Path, max_depth: int, filename: str = "scores.json") -> list[Path]:
    matches: list[Path] = []

    for current in root.rglob(filename):
        if _relative_depth(root, current.parent) <= max_depth:
            matches.append(current)

    return sorted(matches)


def normalize_score_json(data: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {}

    for key, value in data.items():
        if key == "metrics" and isinstance(value, dict):
            for metric_key, metric_value in value.items():
                row[metric_key] = metric_value
            continue

        if isinstance(value, (str, int, float, bool)) or value is None:
            row[key] = value

    return row


def collect_rows(files: list[Path], root: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows: list[dict[str, Any]] = []
    all_columns: set[str] = set()

    for file_path in files:
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        if not isinstance(data, dict):
            continue

        normalized = normalize_score_json(data)
        normalized["path"] = str(file_path.relative_to(root))

        all_columns.update(k for k in normalized.keys() if k != "path")
        rows.append(normalized)

    ordered_columns = ["path"] + sorted(all_columns)
    return rows, ordered_columns


def write_csv(rows: list[dict[str, Any]], columns: list[str], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    with output_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()

        for row in rows:
            writer.writerow(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Recursively scan for scores.json files up to a max depth and create a combined CSV."
        )
    )
    parser.add_argument("folder", help="Root folder to start searching from")
    parser.add_argument(
        "max_depth",
        type=int,
        help="Maximum directory depth to search (0 means only the root folder)",
    )
    parser.add_argument(
        "--output",
        default="scores_aggregate.csv",
        help="Output CSV file path (default: scores_aggregate.csv)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.folder).resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Invalid folder: {root}")

    if args.max_depth < 0:
        raise SystemExit("max_depth must be >= 0")

    score_files = find_score_files(root, args.max_depth)
    rows, columns = collect_rows(score_files, root)

    output_csv = Path(args.output).resolve()
    write_csv(rows, columns, output_csv)

    print(f"Found {len(score_files)} scores.json file(s).")
    print(f"Wrote CSV with {len(rows)} row(s) to: {output_csv}")


if __name__ == "__main__":
    main()
