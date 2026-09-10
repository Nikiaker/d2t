#!/usr/bin/env python3
"""Normalize human scoring CSVs for ``correlate_scores.py``.

Human scoring files created with the older rubric use ``triples_completeness``
for the criterion now called ``triples_additions``. This script converts every
``human_*_scoring.csv`` below a test directory to the current four-score schema,
copies the first 10 text scores from each rules file to the other methods in
the same domain, and validates each file against its matching LLM-scored CSV.

Original files are backed up under ``<test-dir>/.human_score_backups`` before
replacement. Use ``--dry-run`` to validate and report without changing files.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


SCORE_COLUMNS = [
    "text_summary",
    "text_faithfulness",
    "triples_additions",
    "triples_omissions",
]
TEXT_SCORE_COLUMNS = ["text_summary", "text_faithfulness"]
RULES_HUMAN_FILENAME = "human_extracted_triples_rules_text_pipeline_scoring.csv"

SOURCE_COLUMNS = {
    "text_summary": "text_summary",
    "text_faithfulness": "text_faithfulness",
    "triples_additions": "triples_completeness",
    "triples_omissions": "triples_omissions",
}

LEGACY_SCORE_COLUMNS = {
    "text_completeness",
    "text_omissions",
    "triples_summary",
    "triples_completeness",
    "triples_faithfulness",
}

MIN_SCORE = 1
MAX_SCORE = 5


def llm_path_for_human(human_path: Path) -> Path:
    prefix = "human_"
    suffix = "_scoring.csv"
    if not human_path.name.startswith(prefix) or not human_path.name.endswith(suffix):
        raise ValueError(f"Not a human scoring file: {human_path}")
    llm_name = human_path.name[len(prefix) : -len(suffix)] + "_scored.csv"
    return human_path.with_name(llm_name)


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fieldnames = list(reader.fieldnames or [])
        if not fieldnames:
            raise ValueError(f"CSV has no header: {path}")
        rows = list(reader)
    return fieldnames, rows


def instance_ids(path: Path, rows: list[dict[str, str]]) -> set[str]:
    if "instance_id" not in (rows[0] if rows else {}):
        raise ValueError(f"Missing instance_id column: {path}")
    ids = [str(row.get("instance_id", "")).strip() for row in rows]
    if any(not value for value in ids):
        raise ValueError(f"Empty instance_id in {path}")
    if len(set(ids)) != len(ids):
        raise ValueError(f"Duplicate instance_id in {path}")
    return set(ids)


def validate_score(value: Any, path: Path, row_number: int, column: str) -> None:
    text = "" if value is None else str(value).strip()
    if not text:
        return
    try:
        number = float(text)
    except ValueError as exc:
        raise ValueError(f"{path}:{row_number}: {column} is not numeric: {text!r}") from exc
    if not number.is_integer() or not MIN_SCORE <= int(number) <= MAX_SCORE:
        raise ValueError(f"{path}:{row_number}: {column} must be an integer from 1 to 5")


def output_fieldnames(fieldnames: list[str]) -> list[str]:
    retained = [
        field
        for field in fieldnames
        if field not in LEGACY_SCORE_COLUMNS and field not in SCORE_COLUMNS
    ]
    try:
        insert_at = retained.index("generated_triples") + 1
    except ValueError:
        insert_at = len(retained)
    return retained[:insert_at] + SCORE_COLUMNS + retained[insert_at:]


def instance_sort_key(instance_id: str) -> tuple[int, Any]:
    return (0, int(instance_id)) if instance_id.isdigit() else (1, instance_id)


def normalize_rows(
    path: Path,
    fieldnames: list[str],
    rows: list[dict[str, str]],
) -> tuple[list[str], list[dict[str, str]]]:
    source_for_target = {
        target: (
            source
            if source in fieldnames
            else target
            if target in fieldnames
            else None
        )
        for target, source in SOURCE_COLUMNS.items()
    }
    missing = sorted(target for target, source in source_for_target.items() if source is None)
    if missing:
        raise ValueError(f"{path}: missing score columns: {', '.join(missing)}")

    normalized: list[dict[str, str]] = []
    output_fields = output_fieldnames(fieldnames)
    for row_number, row in enumerate(rows, start=2):
        output = {field: row.get(field, "") for field in output_fields}
        for target, source in SOURCE_COLUMNS.items():
            source_column = source_for_target[target]
            assert source_column is not None
            validate_score(row.get(source_column), path, row_number, source_column)
            output[target] = (row.get(source_column) or "").strip()
        normalized.append(output)
    return output_fields, normalized


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8-sig",
        newline="",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as stream:
        temporary_path = Path(stream.name)
        writer = csv.DictWriter(
            stream,
            fieldnames=fieldnames,
            extrasaction="raise",
            lineterminator="\r\n",
        )
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary_path, path)


def preflight(
    human_paths: list[Path],
) -> list[tuple[Path, list[str], list[dict[str, str]]]]:
    prepared = []
    for human_path in human_paths:
        llm_path = llm_path_for_human(human_path)
        if not llm_path.exists():
            raise ValueError(f"Missing LLM counterpart for {human_path}: {llm_path}")

        human_fields, human_rows = read_csv(human_path)
        _, llm_rows = read_csv(llm_path)
        if instance_ids(human_path, human_rows) != instance_ids(llm_path, llm_rows):
            raise ValueError(f"instance_id mismatch between {human_path} and {llm_path}")

        output_fields, normalized_rows = normalize_rows(
            human_path, human_fields, human_rows
        )
        prepared.append((human_path, output_fields, normalized_rows))
    return prepared


def copy_text_scores(
    prepared: list[tuple[Path, list[str], list[dict[str, str]]]],
    limit: int,
) -> int:
    by_path = {path: (fields, rows) for path, fields, rows in prepared}
    by_domain: dict[Path, list[Path]] = {}
    for path in by_path:
        by_domain.setdefault(path.parent, []).append(path)

    copied = 0
    for domain, paths in sorted(by_domain.items()):
        source_path = domain / RULES_HUMAN_FILENAME
        if source_path not in by_path:
            print(f"[skip] no rules human file in {domain}")
            continue

        _, source_rows = by_path[source_path]
        source_by_id = {row["instance_id"].strip(): row for row in source_rows}
        scored_ids = sorted(
            [
                instance_id
                for instance_id, row in source_by_id.items()
                if all((row.get(column) or "").strip() for column in TEXT_SCORE_COLUMNS)
            ],
            key=instance_sort_key,
        )
        if len(scored_ids) < limit:
            raise ValueError(
                f"{source_path}: found {len(scored_ids)} complete text-scored rows; "
                f"expected at least {limit}"
            )
        selected_ids = scored_ids[:limit]

        for target_path in sorted(paths):
            if target_path == source_path:
                continue
            _, target_rows = by_path[target_path]
            target_by_id = {row["instance_id"].strip(): row for row in target_rows}
            for instance_id in selected_ids:
                source_row = source_by_id[instance_id]
                target_row = target_by_id[instance_id]
                for column in TEXT_SCORE_COLUMNS:
                    source_value = (source_row.get(column) or "").strip()
                    target_value = (target_row.get(column) or "").strip()
                    if target_value and target_value != source_value:
                        raise ValueError(
                            f"{target_path}: conflicting {column} for instance "
                            f"{instance_id}: {target_value!r} != {source_value!r}"
                        )
                    target_row[column] = source_value
            copied += 1
            print(
                f"[text] {target_path}: copied {len(selected_ids)} rows "
                f"from {source_path.name}"
            )
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--test-dir",
        default="tripler/outputs/test10_re",
        help="Test output directory containing per-domain folders.",
    )
    parser.add_argument(
        "--backup-dir",
        default=None,
        help="Backup directory; defaults to <test-dir>/.human_score_backups.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and report changes without replacing files.",
    )
    parser.add_argument(
        "--text-score-limit",
        type=int,
        default=10,
        help="Number of populated text-score rows to copy from each rules file.",
    )
    parser.add_argument(
        "--no-copy-text-scores",
        action="store_true",
        help="Do not copy text scores from rules files to other methods.",
    )
    args = parser.parse_args()

    test_dir = Path(args.test_dir)
    if not test_dir.is_dir():
        print(f"Test directory not found: {test_dir}", file=sys.stderr)
        return 2

    human_paths = sorted(test_dir.glob("*/human_*_scoring.csv"))
    if not human_paths:
        print(f"No human_*_scoring.csv files found under {test_dir}", file=sys.stderr)
        return 2
    if args.text_score_limit < 1:
        print("--text-score-limit must be positive", file=sys.stderr)
        return 2

    try:
        prepared = preflight(human_paths)
    except (OSError, ValueError) as exc:
        print(f"Preflight failed: {exc}", file=sys.stderr)
        return 1

    try:
        copied = 0 if args.no_copy_text_scores else copy_text_scores(
            prepared, args.text_score_limit
        )
    except ValueError as exc:
        print(f"Text-score copy failed: {exc}", file=sys.stderr)
        return 1

    backup_dir = Path(args.backup_dir) if args.backup_dir else test_dir / ".human_score_backups"
    if args.dry_run:
        for path, fields, rows in prepared:
            print(f"[dry-run] {path}: {len(rows)} rows; columns={fields}")
        print(f"[dry-run] text scores copied to {copied} file(s)")
        return 0

    try:
        for path, fields, rows in prepared:
            backup_path = backup_dir / path.relative_to(test_dir)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            if not backup_path.exists():
                shutil.copy2(path, backup_path)
            write_csv(path, fields, rows)
            print(f"[ok] {path} (backup: {backup_path})")
    except (OSError, ValueError) as exc:
        print(f"Normalization failed: {exc}", file=sys.stderr)
        return 1

    print(
        f"Normalized {len(prepared)} human scoring file(s); "
        f"copied text scores to {copied} file(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
