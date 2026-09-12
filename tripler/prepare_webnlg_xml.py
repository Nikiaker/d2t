#!/usr/bin/env python3
"""Package joint-model JSON output into WebNLG directory layout.

The WebNLG benchmark reader searches ``<split>/<n>triples`` directories for
``.xml`` files. This utility creates one category file per supported triple
count and writes a report for empty, malformed, or unsupported predictions.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import ElementTree, fromstring

from json_to_xml_converter import create_xml_tree, write_xml_file


def _index_texts(data: dict[str, Any]) -> dict[int, str]:
    result: dict[int, str] = {}
    for item in data.get("generated_text_by_instance", []):
        if isinstance(item, dict) and "instance_id" in item:
            result[int(item["instance_id"])] = str(item.get("text", "")).strip()
    return result


def package_json(
    input_path: Path,
    output_root: Path,
    category: str,
    split: str,
    min_triples: int = 1,
    max_triples: int = 7,
) -> dict[str, Any]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    text_by_id = _index_texts(data)
    groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
    report: dict[str, Any] = {
        "input_file": str(input_path),
        "output_root": str(output_root),
        "category": category,
        "split": split,
        "min_triples": min_triples,
        "max_triples": max_triples,
        "accepted_instance_ids": [],
        "skipped": [],
        "output_files": [],
    }

    seen_ids: set[int] = set()
    for item in data.get("triples_by_instance", []):
        if not isinstance(item, dict) or "instance_id" not in item:
            report["skipped"].append({"reason": "missing_instance_id"})
            continue
        instance_id = int(item["instance_id"])
        if instance_id in seen_ids:
            report["skipped"].append({"instance_id": instance_id, "reason": "duplicate_instance_id"})
            continue
        seen_ids.add(instance_id)

        triples = item.get("triples")
        if not isinstance(triples, list):
            report["skipped"].append({"instance_id": instance_id, "reason": "triples_not_a_list"})
            continue
        valid_triples = []
        malformed = False
        for triple in triples:
            if not isinstance(triple, dict):
                malformed = True
                break
            normalized = {
                "subject": str(triple.get("subject", "")).strip(),
                "predicate": str(triple.get("predicate", "")).strip(),
                "object": str(triple.get("object", "")).strip(),
            }
            if not all(normalized.values()):
                malformed = True
                break
            valid_triples.append(normalized)
        if malformed:
            report["skipped"].append({"instance_id": instance_id, "reason": "malformed_triple"})
            continue

        triple_count = len(valid_triples)
        if triple_count < min_triples:
            report["skipped"].append({"instance_id": instance_id, "reason": "no_triples"})
            continue
        if triple_count > max_triples:
            report["skipped"].append(
                {"instance_id": instance_id, "reason": "unsupported_triple_count", "count": triple_count}
            )
            continue
        if not text_by_id.get(instance_id):
            report["skipped"].append({"instance_id": instance_id, "reason": "missing_text"})
            continue

        groups[triple_count].append({"instance_id": instance_id, "triples": valid_triples})
        report["accepted_instance_ids"].append(instance_id)

    for triple_count in sorted(groups):
        bucket = groups[triple_count]
        bucket_ids = {item["instance_id"] for item in bucket}
        bucket_data = {
            "triples_by_instance": bucket,
            "generated_text_by_instance": [
                {"instance_id": instance_id, "text": text_by_id[instance_id]}
                for instance_id in sorted(bucket_ids)
            ],
        }
        output_path = output_root / split / f"{triple_count}triples" / f"{category}.xml"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_xml_file(create_xml_tree(bucket_data, category), str(output_path))
        # Verify the produced file is parseable before reporting it as usable.
        ElementTree(fromstring(output_path.read_text(encoding="utf-8")))
        report["output_files"].append(
            {"path": str(output_path), "triple_count": triple_count, "entries": len(bucket)}
        )

    report["input_instances"] = len(data.get("triples_by_instance", []))
    report["accepted_instances"] = len(report["accepted_instance_ids"])
    report["skipped_instances"] = len(report["skipped"])
    report_dir = output_root / "generated_seed_2994_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"{category}_{split}.json"
    report["report_file"] = str(report_path)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True, help="WebNLG en/ directory")
    parser.add_argument("--category", required=True, help="XML category, e.g. Owid")
    parser.add_argument("--split", choices=("train", "dev", "test"), required=True)
    parser.add_argument("--min-triples", type=int, default=1)
    parser.add_argument("--max-triples", type=int, default=7)
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input file does not exist: {args.input}")
    if not args.category.replace("_", "").isalnum():
        parser.error("category must contain only letters, numbers, or underscores")
    if args.min_triples < 1 or args.max_triples < args.min_triples:
        parser.error("invalid triple-count range")

    report = package_json(
        args.input,
        args.output_root,
        args.category,
        args.split,
        args.min_triples,
        args.max_triples,
    )
    print(
        f"packaged category={args.category} split={args.split} "
        f"accepted={report['accepted_instances']} skipped={report['skipped_instances']}"
    )


if __name__ == "__main__":
    main()
