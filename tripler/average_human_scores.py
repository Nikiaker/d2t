#!/usr/bin/env python3
"""Compute per-domain averages from human scoring CSVs.

Reads ``human_*_scoring.csv`` files under a test output directory and writes
one ``human_*_averages.csv`` per method. Only rows with all four human scores
are included; by default exactly the first 10 complete scored instances are
used. Descriptive statistics are averaged over those same instances.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any


logger = logging.getLogger(__name__)

CRITERIA = [
    "text_summary",
    "text_faithfulness",
    "triples_additions",
    "triples_omissions",
]
TEXT_CRITERIA = ["text_summary", "text_faithfulness"]
TRIPLES_CRITERIA = ["triples_additions", "triples_omissions"]
STAT_COLUMNS = [
    "json_elements",
    "ref_words",
    "ref_sentences",
    "ref_subsentences",
    "num_triples",
    "unique_predicates",
]


def to_float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
        try:
            return float(value)
        except ValueError:
            return None
    return None


def instance_sort_key(row: dict[str, str]) -> tuple[int, Any]:
    instance_id = (row.get("instance_id") or "").strip()
    return (0, int(instance_id)) if instance_id.isdigit() else (1, instance_id)


def method_name(scoring_path: Path) -> str:
    return scoring_path.stem.removesuffix("_scoring").removeprefix("human_")


def read_pipeline_predicate_count(scoring_path: Path) -> int:
    method = method_name(scoring_path)
    output_path = scoring_path.with_name(f"{method}.json")
    data = json.loads(output_path.read_text(encoding="utf-8"))

    rules_final = data.get("rules_final")
    if isinstance(rules_final, dict) and "predicates" in rules_final:
        predicates = rules_final["predicates"]
    else:
        predicates = data.get("unique_predicates")
    if not isinstance(predicates, list):
        raise ValueError(f"Predicate list not found in {output_path}")
    return len(predicates)


def read_human_csv(
    path: Path,
    expected_rows: int,
) -> tuple[str, dict[str, list[float]], int, list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)

    required = {"instance_id", "domain", *CRITERIA, *STAT_COLUMNS}
    missing = sorted(required - set(reader.fieldnames or []))
    if missing:
        raise ValueError(f"{path}: missing columns: {', '.join(missing)}")

    complete_rows = [
        row
        for row in sorted(rows, key=instance_sort_key)
        if all(to_float_or_none(row.get(column)) is not None for column in CRITERIA)
    ]
    if len(complete_rows) < expected_rows:
        raise ValueError(
            f"{path}: found {len(complete_rows)} complete scored rows; "
            f"expected at least {expected_rows}"
        )
    selected_rows = complete_rows[:expected_rows]

    domain = (selected_rows[0].get("domain") or "").strip() if selected_rows else ""
    if not domain:
        domain = path.parent.name

    values: dict[str, list[float]] = {column: [] for column in CRITERIA + STAT_COLUMNS}
    selected_ids: list[str] = []
    for row in selected_rows:
        selected_ids.append((row.get("instance_id") or "").strip())
        for column in CRITERIA + STAT_COLUMNS:
            value = to_float_or_none(row.get(column))
            if value is not None:
                values[column].append(value)

    return domain, values, read_pipeline_predicate_count(path), selected_ids


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def build_output_row(
    domain: str,
    values: dict[str, list[float]],
    predicate_count: int,
) -> list[str]:
    row = [domain]
    for column in CRITERIA:
        row.append(f"{average(values[column]):.2f}")

    text_values = [value for column in TEXT_CRITERIA for value in values[column]]
    triple_values = [value for column in TRIPLES_CRITERIA for value in values[column]]
    row.append(f"{average(text_values):.2f}")
    row.append(f"{average(triple_values):.2f}")

    for column in STAT_COLUMNS[:-1]:
        row.append(f"{average(values[column]):.2f}")
    row.append(str(predicate_count))
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--test-dir",
        default="tripler/outputs/test10_re",
        help="Directory containing per-domain human scoring files.",
    )
    parser.add_argument(
        "--score-rows",
        type=int,
        default=10,
        help="Number of complete scored instances to average per file.",
    )
    args = parser.parse_args()

    if args.score_rows < 1:
        raise SystemExit("--score-rows must be positive")

    test_dir = Path(args.test_dir)
    if not test_dir.is_dir():
        raise SystemExit(f"Test directory not found: {test_dir}")

    scoring_paths = sorted(test_dir.glob("*/human_*_scoring.csv"))
    if not scoring_paths:
        raise SystemExit(f"No human_*_scoring.csv files found under {test_dir}")

    by_method: dict[str, list[tuple[str, dict[str, list[float]], int, list[str]]]] = defaultdict(list)
    for path in scoring_paths:
        domain, values, predicate_count, selected_ids = read_human_csv(
            path, args.score_rows
        )
        method = method_name(path)
        by_method[method].append((domain, values, predicate_count, selected_ids))
        logger.info(
            "read %s: domain=%s, method=%s, instances=%s",
            path.name,
            domain,
            method,
            ",".join(selected_ids),
        )

    fieldnames = ["domain"] + CRITERIA + ["text_overall", "triples_overall"] + STAT_COLUMNS
    for method, entries in sorted(by_method.items()):
        out_path = test_dir / f"human_{method}_averages.csv"
        with out_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(fieldnames)
            for domain, values, predicate_count, _ in sorted(entries, key=lambda entry: entry[0]):
                writer.writerow(build_output_row(domain, values, predicate_count))
        print(f"[ok] {out_path} ({len(entries)} domains)")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    main()
