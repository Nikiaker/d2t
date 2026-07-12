"""Build per-app-script scoring CSVs from extracted-triples outputs.

For every extracted_triples_*.json under a test output directory (e.g.
tripler/outputs/test8), emit a CSV with one row per instance containing:
  instance_id, domain, input_data, generated_text, generated_triples,
  summary, completeness, faithfulness, omissions

The last four columns are left empty for manual scoring (1-5).
"""

import argparse
import csv
import json
import re
from pathlib import Path
from typing import Any

SCORE_COLUMNS = ["summary", "completeness", "faithfulness", "omissions"]
TRIPLE_SEP = " ; "
TRIPLE_FMT = "{subject} --{predicate}-> {object}"


def map_input_file(input_file: str, tripler_dir: Path) -> Path:
    basename = Path(input_file).name
    return tripler_dir / "inputs" / basename


def extract_instances(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [{"instance_id": idx, "data": item} for idx, item in enumerate(payload)]

    if isinstance(payload, dict):
        if isinstance(payload.get("forecasts"), list):
            return [
                {"instance_id": idx, "data": forecast}
                for idx, forecast in enumerate(payload["forecasts"])
            ]
        if isinstance(payload.get("list"), list):
            return [
                {"instance_id": idx, "data": item}
                for idx, item in enumerate(payload["list"])
            ]
        for key, value in payload.items():
            if isinstance(value, list):
                return [{"instance_id": idx, "data": item} for idx, item in enumerate(value)]

    raise ValueError("Unsupported input JSON structure for instance extraction")


def load_input_instances(input_file: str, tripler_dir: Path) -> list[dict[str, Any]]:
    local_path = map_input_file(input_file, tripler_dir)
    if not local_path.exists():
        raise FileNotFoundError(f"Input file not found locally: {local_path} (from {input_file})")
    payload = json.loads(local_path.read_text(encoding="utf-8"))
    return extract_instances(payload)


def format_triples(triples: list[dict[str, Any]]) -> str:
    return TRIPLE_SEP.join(
        TRIPLE_FMT.format(subject=t.get("subject", ""), predicate=t.get("predicate", ""), object=t.get("object", ""))
        for t in triples
    )


def rows_for_output(output_path: Path, tripler_dir: Path) -> list[list[str]]:
    data = json.loads(output_path.read_text(encoding="utf-8"))
    domain = data.get("problem_domain") or output_path.parent.name
    input_file = data.get("input_file", "")
    instances = load_input_instances(input_file, tripler_dir)
    instance_by_id = {ins["instance_id"]: ins for ins in instances}

    text_entries = data.get("generated_text_by_instance", [])
    triples_entries = data.get("triples_by_instance", [])
    text_by_id = {e.get("instance_id"): e.get("text", "") for e in text_entries}
    triples_by_id = {e.get("instance_id"): e.get("triples", []) for e in triples_entries}

    all_ids = sorted(set(text_by_id) | set(triples_by_id) | set(instance_by_id))
    rows: list[list[str]] = []
    for iid in all_ids:
        ins = instance_by_id.get(iid, {})
        input_data = json.dumps(ins.get("data", {}), ensure_ascii=False, separators=(",", ":"))
        text = text_by_id.get(iid, "")
        triples = format_triples(triples_by_id.get(iid, []))
        rows.append([
            str(iid), domain, input_data, text, triples, "", "", "", "",
        ])
    return rows


def process_output(output_path: Path, tripler_dir: Path) -> Path:
    out_name = output_path.stem + "_scoring.csv"
    out_path = output_path.parent / out_name
    header = ["instance_id", "domain", "input_data", "generated_text", "generated_triples"] + SCORE_COLUMNS
    rows = rows_for_output(output_path, tripler_dir)
    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header)
        writer.writerows(rows)
    return out_path


def script_suffix(path: Path) -> str:
    m = re.search(r"extracted_triples_(.+)\.json$", path.name)
    return m.group(1) if m else path.stem


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-dir", default="tripler/outputs/test8", help="Directory containing per-domain output folders.")
    parser.add_argument("--tripler-dir", default="tripler", help="Tripler directory where inputs/ lives.")
    parser.add_argument("--domains", default=None, help="Comma-separated domain names to include; default all.")
    args = parser.parse_args()

    test_dir = Path(args.test_dir)
    tripler_dir = Path(args.tripler_dir)
    if not test_dir.is_dir():
        raise SystemExit(f"Test directory not found: {test_dir}")

    domain_filter = None
    if args.domains:
        domain_filter = set(d.strip() for d in args.domains.split(","))

    processed = 0
    for domain_dir in sorted(test_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domain_filter and domain_dir.name not in domain_filter:
            continue
        output_files = sorted(domain_dir.glob("extracted_triples_*.json"))
        if not output_files:
            continue
        for output_file in output_files:
            try:
                out_path = process_output(output_file, tripler_dir)
                print(f"[ok] {out_path}")
                processed += 1
            except Exception as exc:
                print(f"[fail] {output_file}: {exc}")
    print(f"Done. {processed} CSV file(s) written.")


if __name__ == "__main__":
    main()