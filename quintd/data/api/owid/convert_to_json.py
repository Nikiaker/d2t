#!/usr/bin/env python3
"""Convert OWID CSV instances to the bare-list JSON layout used by other datasets.

Reads quintd/data/quintd-1/data/owid/{dev,test}/*.csv (100 CSVs per split) and
writes quintd/data/quintd-1/data/owid/{dev,test}.json, each a bare JSON list of
100 instance objects:
  {
    "id": 0,
    "country": "Ethiopia",
    "metric": "life_expectancy_0",
    "title": "Life expectancy at birth",
    "description": "...",
    "unit": "years",
    "data": [{"date": "1950", "value": 36.3529}, ...]
  }

The existing dev/ and test/ CSV directories and metadata/ are left untouched.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

EXPECTED_METADATA_KEYS = ["country", "title", "description", "unit"]
INSTANCE_KEYS = ["id", "country", "metric", "title", "description", "unit", "data"]


def parse_filename(path: Path) -> tuple[int, str, str]:
    stem = path.stem
    first_dash = stem.find("-")
    if first_dash == -1:
        raise ValueError(f"Filename {path.name} has no '-' separator for id")
    id_str = stem[:first_dash]
    rest = stem[first_dash + 1:]
    second_dash = rest.find("-")
    if second_dash == -1:
        raise ValueError(f"Filename {path.name} has no '-' separator for metric/country")
    metric = rest[:second_dash]
    country = rest[second_dash + 1:]
    try:
        instance_id = int(id_str)
    except ValueError as exc:
        raise ValueError(f"Filename {path.name} has non-integer id '{id_str}'") from exc
    return instance_id, metric, country


def parse_csv(path: Path) -> dict[str, Any]:
    instance_id, metric, country_from_name = parse_filename(path)
    lines = path.read_text(encoding="utf-8").splitlines()

    metadata: dict[str, str] = {}
    for line in lines:
        if not line.startswith("#"):
            break
        body = line[1:].strip()
        if ": " in body:
            key, value = body.split(": ", 1)
            metadata[key] = value
        elif ":" in body:
            key, value = body.split(":", 1)
            metadata[key] = value.strip()

    for key in EXPECTED_METADATA_KEYS:
        if key not in metadata:
            logger.warning("CSV %s missing metadata key '%s'", path.name, key)

    data: list[dict[str, Any]] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == "date,value":
            continue
        parts = stripped.split(",")
        if len(parts) != 2:
            logger.warning("Skipping malformed row in %s: %r", path.name, stripped)
            continue
        date_str, value_str = parts[0].strip(), parts[1].strip()
        try:
            value = float(value_str)
        except ValueError:
            logger.warning("Non-numeric value in %s row %r; storing as string", path.name, stripped)
            value = value_str
        data.append({"date": date_str, "value": value})

    if not data:
        logger.warning("CSV %s has no data rows", path.name)

    return {
        "id": instance_id,
        "country": metadata.get("country", country_from_name),
        "metric": metric,
        "title": metadata.get("title", ""),
        "description": metadata.get("description", ""),
        "unit": metadata.get("unit", ""),
        "data": data,
    }


def convert_split(owid_dir: Path, split: str) -> list[dict[str, Any]]:
    split_dir = owid_dir / split
    if not split_dir.is_dir():
        raise FileNotFoundError(f"Split directory not found: {split_dir}")

    csv_paths = sorted(
        split_dir.glob("*.csv"),
        key=lambda p: int(p.stem.split("-")[0]),
    )
    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {split_dir}")

    instances: list[dict[str, Any]] = []
    for path in csv_paths:
        try:
            instances.append(parse_csv(path))
        except Exception as exc:
            logger.warning("Failed to parse %s: %s", path, exc)

    instances.sort(key=lambda inst: inst["id"])
    return instances


def write_json(path: Path, instances: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(instances, f, ensure_ascii=False, indent=2)
        f.write("\n")


def verify(path: Path, expected_count: int) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise AssertionError(f"{path} is not a JSON list")
    if len(data) != expected_count:
        logger.warning("%s has %d instances, expected %d", path.name, len(data), expected_count)
    ids = [inst.get("id") for inst in data]
    if ids != list(range(len(data))):
        logger.warning("%s ids are not [0..%d): %s", path.name, len(data) - 1, ids[:5])
    for inst in data:
        if list(inst.keys()) != INSTANCE_KEYS:
            logger.warning("%s instance id=%s has unexpected keys: %s",
                           path.name, inst.get("id"), list(inst.keys()))
            break
        if not inst["data"]:
            logger.warning("%s instance id=%s has empty data", path.name, inst.get("id"))
            break


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owid-dir", default="quintd/data/quintd-1/data/owid",
                        help="Directory containing dev/, test/, and metadata/ for OWID.")
    parser.add_argument("--splits", default="dev,test", help="Comma-separated split names to convert.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output JSON files.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    owid_dir = Path(args.owid_dir)
    if not owid_dir.is_dir():
        raise SystemExit(f"OWID directory not found: {owid_dir}")

    splits = [s.strip() for s in args.splits.split(",") if s.strip()]
    if not splits:
        raise SystemExit("No splits specified.")

    for split in splits:
        out_path = owid_dir / f"{split}.json"
        if out_path.exists() and not args.overwrite:
            print(f"[skip] {out_path} already exists (use --overwrite to replace)")
            continue

        split_dir = owid_dir / split
        expected_count = len(list(split_dir.glob("*.csv"))) if split_dir.is_dir() else 0

        instances = convert_split(owid_dir, split)
        write_json(out_path, instances)
        verify(out_path, expected_count)
        print(f"[ok] {out_path} ({len(instances)} instances)")


if __name__ == "__main__":
    main()