#!/usr/bin/env python3
"""Compute per-domain average scores for each method/pipeline.

Reads every *_scored.csv under a test output directory, groups them by method
(extracted from the filename stem), and writes one CSV per method with one
row per domain containing the average of each criterion across all instances.

Output columns: domain, summary, completeness, faithfulness, omissions
Output file:  <test_dir>/<method>_averages.csv
"""

import argparse
import csv
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CRITERIA = ["summary", "completeness", "faithfulness", "omissions"]


def to_float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return float(s)
        except ValueError:
            return None
    return None


def read_scored_csv(path: Path) -> tuple[str, dict[str, list[float]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    domain = ""
    values: dict[str, list[float]] = {c: [] for c in CRITERIA}

    for row in rows:
        if not domain:
            domain = (row.get("domain") or "").strip()
        for c in CRITERIA:
            v = to_float_or_none(row.get(c))
            if v is not None:
                values[c].append(v)

    if not domain:
        domain = path.parent.name

    return domain, values


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", default="tripler/outputs/test10",
                        help="Directory containing per-domain output folders with *_scored.csv files.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    test_dir = Path(args.test_dir)
    if not test_dir.is_dir():
        raise SystemExit(f"Test directory not found: {test_dir}")

    scored_csvs = sorted(test_dir.glob("*/*_scored.csv"))
    if not scored_csvs:
        raise SystemExit(f"No *_scored.csv files found under {test_dir}")

    by_method: dict[str, list[tuple[str, dict[str, list[float]]]]] = defaultdict(list)

    for path in scored_csvs:
        method = path.stem.removesuffix("_scored")
        domain, values = read_scored_csv(path)
        by_method[method].append((domain, values))
        logger.info("read %s: domain=%s, method=%s", path.name, domain, method)

    for method, entries in sorted(by_method.items()):
        out_path = test_dir / f"{method}_averages.csv"
        with out_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["domain"] + CRITERIA)
            for domain, values in sorted(entries, key=lambda e: e[0]):
                row = [domain]
                for c in CRITERIA:
                    vals = values[c]
                    avg = sum(vals) / len(vals) if vals else float("nan")
                    row.append(f"{avg:.2f}")
                writer.writerow(row)
        print(f"[ok] {out_path} ({len(entries)} domains)")


if __name__ == "__main__":
    main()