#!/usr/bin/env python3
"""Collect dev-split scores from finetune eval reports into per-method CSVs.

Scans a runs directory laid out as:

    <runs_dir>/<domain>/<method>/eval_report_ft.json    (fine-tuned methods)
    <runs_dir>/<domain>/eval_report{,_base,_ft}.json    (baseline at domain root)

Each report has the shape produced by tripler/finetune/eval.py:
    {"models": [{"split": "train", ...}, {"split": "dev", ...}]}

For every method, one CSV is written to <out_dir>/<method>.csv with one row
per domain, taking the metrics of the entry whose "split" is "dev".

Output columns:
    domain, bleu, meteor, triple_precision, triple_recall, triple_f1,
    parse_rate, predicate_adherence, n_examples, n_parsed
"""

import argparse
import csv
import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

METRIC_COLUMNS = [
    "bleu", "meteor", "triple_precision", "triple_recall", "triple_f1",
    "parse_rate", "predicate_adherence", "n_examples", "n_parsed",
]
INT_COLUMNS = {"n_examples", "n_parsed"}
METHOD_REPORT_NAME = "eval_report_ft.json"
BASELINE_REPORT_CANDIDATES = [
    "eval_report.json", "eval_report_base.json", "eval_report_ft.json",
]


def load_dev_entry(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("failed to read %s: %s", path, exc)
        return None

    models = data.get("models")
    if not isinstance(models, list):
        logger.warning("no 'models' array in %s", path)
        return None

    devs = [m for m in models if isinstance(m, dict) and m.get("split") == "dev"]
    if not devs:
        logger.warning("no entry with 'split' == 'dev' in %s", path)
        return None
    if len(devs) > 1:
        logger.warning("multiple 'dev' entries in %s; using the first", path)
    return devs[0]


def discover_reports(runs_dir: Path) -> dict[tuple[str, str], Path]:
    """Map (method, domain) -> report path."""
    found: dict[tuple[str, str], Path] = {}

    for domain_dir in sorted(p for p in runs_dir.iterdir() if p.is_dir()):
        domain = domain_dir.name

        for method_dir in sorted(p for p in domain_dir.iterdir() if p.is_dir()):
            report = method_dir / METHOD_REPORT_NAME
            if report.is_file():
                found[(method_dir.name, domain)] = report

        if ("baseline", domain) not in found:
            for name in BASELINE_REPORT_CANDIDATES:
                report = domain_dir / name
                if report.is_file():
                    found[("baseline", domain)] = report
                    break
            else:
                logger.warning("no baseline report found for domain %s", domain)

    return found


def format_value(column: str, value: Any) -> str:
    if value is None:
        return ""
    if column in INT_COLUMNS:
        return str(int(value))
    return f"{float(value):.4f}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", default="tripler/finetune/runs",
                        help="Directory with <domain>/<method>/eval_report_ft.json layout.")
    parser.add_argument("--out-dir", default=None,
                        help="Where to write per-method CSVs (default: --runs-dir).")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    runs_dir = Path(args.runs_dir)
    if not runs_dir.is_dir():
        raise SystemExit(f"Runs directory not found: {runs_dir}")

    out_dir = Path(args.out_dir) if args.out_dir else runs_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    found = discover_reports(runs_dir)
    if not found:
        raise SystemExit(f"No eval reports found under {runs_dir}")

    by_method: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for (method, domain), path in sorted(found.items()):
        entry = load_dev_entry(path)
        if entry is None:
            continue
        by_method[method][domain] = entry
        logger.info("read %s: domain=%s, method=%s", path, domain, method)

    if not by_method:
        raise SystemExit("No usable dev-split scores found.")

    for method, per_domain in sorted(by_method.items()):
        out_path = out_dir / f"{method}.csv"
        with out_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["domain"] + METRIC_COLUMNS)
            for domain in sorted(per_domain):
                entry = per_domain[domain]
                row = [domain] + [format_value(c, entry.get(c)) for c in METRIC_COLUMNS]
                writer.writerow(row)
        print(f"[ok] {out_path} ({len(per_domain)} domains)")


if __name__ == "__main__":
    main()
