#!/usr/bin/env python3
"""Compute no-LLM descriptive statistics for scoring CSV rows.

Reads *_scoring.csv files (or one CSV) and fills the trailing statistic columns:
  - json_elements      : number of leaf/primitive values in the input_data JSON
  - ref_words          : number of words in the generated reference text
  - ref_sentences      : number of sentences in the reference text
  - ref_subsentences   : number of comma/semicolon/colon/dash-separated segments
  - num_triples        : number of extracted triples
  - unique_predicates  : number of distinct predicate labels in the triples

The script modifies the CSV in place by default; it can also write to a new file
via --output. It is called automatically by judge_scoring_batch.py before the
LLM batch is submitted.
"""

import argparse
import csv
import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

STAT_COLUMNS = [
    "json_elements",
    "ref_words",
    "ref_sentences",
    "ref_subsentences",
    "num_triples",
    "unique_predicates",
]
TRIPLE_SEP = " ; "
TRIPLE_ARROW = " --"
TRIPLE_ARROW_END = "-> "


def count_json_elements(obj: Any) -> int:
    if isinstance(obj, dict):
        return sum(count_json_elements(v) for v in obj.values())
    if isinstance(obj, list):
        return sum(count_json_elements(v) for v in obj)
    return 1


def count_words(text: str) -> int:
    tokens = re.findall(r"\b\w+\b", text)
    return len(tokens)


def count_sentences(text: str) -> int:
    if not text.strip():
        return 0
    return len(re.findall(r"[.!?]+(?:\s|$)", text))


def count_subsentences(text: str) -> int:
    if not text.strip():
        return 0
    parts = re.split(r"[,;:\u2013\u2014\-]", text)
    return len([p for p in parts if p.strip()])


def parse_triples(triples_str: str) -> list[dict[str, str]]:
    triples: list[dict[str, str]] = []
    if not triples_str.strip():
        return triples
    for triple_str in triples_str.split(TRIPLE_SEP):
        triple_str = triple_str.strip()
        if not triple_str:
            continue
        arrow_pos = triple_str.find(TRIPLE_ARROW)
        end_pos = triple_str.find(TRIPLE_ARROW_END)
        if arrow_pos == -1 or end_pos == -1 or end_pos <= arrow_pos:
            logger.warning("Skipping malformed triple: %r", triple_str)
            continue
        subject = triple_str[:arrow_pos].strip()
        predicate = triple_str[arrow_pos + len(TRIPLE_ARROW):end_pos].strip()
        obj = triple_str[end_pos + len(TRIPLE_ARROW_END):].strip()
        triples.append({"subject": subject, "predicate": predicate, "object": obj})
    return triples


def compute_stats(row: dict[str, str]) -> dict[str, int]:
    stats: dict[str, int] = {}

    input_data = row.get("input_data", "")
    try:
        parsed = json.loads(input_data)
        stats["json_elements"] = count_json_elements(parsed)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Could not parse input_data JSON for instance %s", row.get("instance_id"))
        stats["json_elements"] = 0

    text = row.get("generated_text", "")
    stats["ref_words"] = count_words(text)
    stats["ref_sentences"] = count_sentences(text)
    stats["ref_subsentences"] = count_subsentences(text)

    triples = parse_triples(row.get("generated_triples", ""))
    stats["num_triples"] = len(triples)
    stats["unique_predicates"] = len({t["predicate"] for t in triples if t["predicate"]})

    return stats


def process_csv(path: Path, output_path: Path | None = None) -> Path:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    for col in STAT_COLUMNS:
        if col not in fieldnames:
            fieldnames.append(col)

    for row in rows:
        stats = compute_stats(row)
        for col, value in stats.items():
            row[col] = str(value)

    out = output_path or path
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    return out


def process_dir(test_dir: Path, domains: list[str] | None = None) -> list[Path]:
    csvs: list[Path] = []
    for domain_dir in sorted(test_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domains and domain_dir.name not in set(domains):
            continue
        csvs.extend(sorted(domain_dir.glob("*_scoring.csv")))

    processed: list[Path] = []
    for csv_path in csvs:
        try:
            out = process_csv(csv_path)
            print(f"[ok] {out}")
            processed.append(out)
        except Exception as exc:
            logger.warning("Failed to process %s: %s", csv_path, exc)
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-csv", type=Path, help="Path to a single scoring CSV to process.")
    parser.add_argument("--test-dir", type=Path, help="Directory containing per-domain folders with *_scoring.csv files.")
    parser.add_argument("--output", type=Path, help="Output path for --input-csv (default: in-place).")
    parser.add_argument("--domains", default=None, help="Comma-separated domain names to include when using --test-dir.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if args.input_csv:
        if args.output and args.test_dir:
            raise SystemExit("Use --output only with --input-csv, not with --test-dir.")
        out = process_csv(args.input_csv, args.output)
        print(f"[ok] {out}")
    elif args.test_dir:
        domains = None
        if args.domains:
            domains = [d.strip() for d in args.domains.split(",")]
        process_dir(args.test_dir, domains)
    else:
        raise SystemExit("Specify either --input-csv or --test-dir.")


if __name__ == "__main__":
    main()