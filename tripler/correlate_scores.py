#!/usr/bin/env python3
"""Compute correlation between LLM-judge and human scores.

Reads two CSVs (LLM-scored and human-scored) sharing the schema
  instance_id, domain, input_data, generated_text, generated_triples,
  text_summary, text_completeness, text_faithfulness, text_omissions,
  triples_summary, triples_completeness, triples_faithfulness, triples_omissions
and reports, per criterion and per overall variant:
  - Pearson r           (linear correlation)
  - Spearman rho        (rank correlation)
  - Kendall tau-b       (rank concordance)
  - Quadratic weighted Cohen's kappa (chance-corrected ordinal agreement)

Scores are split into two independent judge tasks:
  - text_*    : data -> reference text
  - triples_* : reference text -> triples

Overall variants (per task, never mixing the two tasks):
  - overall_text (pooled)    : concatenate the 4 text_* criteria across instances
  - overall_triples (pooled) : concatenate the 4 triples_* criteria across instances
  - overall_text (mean)      : average the 4 text_* scores per instance, then correlate
  - overall_triples (mean)   : average the 4 triples_* scores per instance, then correlate

Run with:
python3 tripler/correlate_scores.py \
  --llm <path-to-LLM-scored.csv> \
  --human <path-to-human-scored.csv> \
  [--out-csv <summary.csv>]

To process the test10 directory in one run:
python3 tripler/correlate_scores.py \
  --test-dir tripler/outputs/test10 \
  --out-csv tripler/outputs/test10/correlation_results.csv

In directory mode, human files are discovered as `human_*_scoring.csv` and
paired with the corresponding `*_scored.csv` file in the same domain folder.
The output is a combined CSV with domain and variant columns.
"""

import argparse
import csv
import logging
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)

CRITERIA = [
    "text_summary", "text_completeness", "text_faithfulness", "text_omissions",
    "triples_summary", "triples_completeness", "triples_faithfulness", "triples_omissions",
]
METRIC_COLS = ["pearson_r", "spearman_rho", "kendall_tau", "qw_kappa"]
SCORE_MIN = 1
SCORE_MAX = 5


def to_int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value if SCORE_MIN <= value <= SCORE_MAX else None
    if isinstance(value, float) and not np.isnan(value):
        if not value.is_integer():
            return None
        value = int(value)
        return value if SCORE_MIN <= value <= SCORE_MAX else None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            number = float(s)
        except ValueError:
            return None
        if not number.is_integer():
            return None
        number = int(number)
        return number if SCORE_MIN <= number <= SCORE_MAX else None
    return None


def load_csv(path: Path, criteria: list[str]) -> dict[str, dict[str, int | None]]:
    by_inst: dict[str, dict[str, int | None]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            inst = str(row["instance_id"]).strip()
            by_inst[inst] = {c: to_int_or_none(row.get(c)) for c in criteria}
    return by_inst


def aligned_pairs(llm: dict[str, dict], human: dict[str, dict], criterion: str) -> tuple[list[int], list[int]]:
    llm_vals, human_vals = [], []
    for inst in sorted(set(llm) & set(human), key=lambda x: int(x) if x.isdigit() else x):
        a = llm[inst].get(criterion)
        b = human[inst].get(criterion)
        if a is None or b is None:
            continue
        llm_vals.append(a)
        human_vals.append(b)
    return llm_vals, human_vals


def pearson_r(a: list[int], b: list[int]) -> float:
    if len(a) < 2 or len(set(a)) == 1 or len(set(b)) == 1:
        return float("nan")
    r, _ = stats.pearsonr(a, b)
    return float(r)


def spearman_rho(a: list[int], b: list[int]) -> float:
    if len(a) < 2 or len(set(a)) == 1 or len(set(b)) == 1:
        return float("nan")
    rho, _ = stats.spearmanr(a, b)
    return float(rho)


def kendall_tau(a: list[int], b: list[int]) -> float:
    if len(a) < 2 or len(set(a)) == 1 or len(set(b)) == 1:
        return float("nan")
    tau, _ = stats.kendalltau(a, b)
    return float(tau)


def quadratic_weighted_kappa(a: list[int], b: list[int]) -> float:
    if not a or len(a) != len(b):
        return float("nan")
    n = SCORE_MAX - SCORE_MIN + 1
    obs = np.zeros((n, n), dtype=float)
    weight = np.zeros((n, n), dtype=float)
    denom = (SCORE_MAX - SCORE_MIN) ** 2
    for i in range(n):
        for j in range(n):
            weight[i, j] = 1.0 - ((i - j) ** 2) / denom
    for av, bv in zip(a, b):
        if not (SCORE_MIN <= av <= SCORE_MAX and SCORE_MIN <= bv <= SCORE_MAX):
            return float("nan")
        obs[av - SCORE_MIN, bv - SCORE_MIN] += 1.0
    total = obs.sum()
    if total == 0:
        return float("nan")
    po = float((weight * obs).sum() / total)
    row = obs.sum(axis=1) / total
    col = obs.sum(axis=0) / total
    expected = np.outer(row, col)
    pe = float((weight * expected).sum())
    if np.isclose(pe, 1.0):
        # Chance agreement is perfect when both raters use one category only.
        return 0.0
    return 1.0 - (1.0 - po) / (1.0 - pe)


def compute_row(a: list[int], b: list[int]) -> dict[str, Any]:
    return {
        "n": len(a),
        "pearson_r": pearson_r(a, b),
        "spearman_rho": spearman_rho(a, b),
        "kendall_tau": kendall_tau(a, b),
        "qw_kappa": quadratic_weighted_kappa(a, b),
    }


def compute_row_cont(a: list[float], b: list[float]) -> dict[str, Any]:
    if not isinstance(a, list):
        a = list(a)
    if not isinstance(b, list):
        b = list(b)
    n = len(a)
    r = float("nan")
    rho = float("nan")
    tau = float("nan")
    if n >= 2:
        if len(set(a)) > 1 and len(set(b)) > 1:
            r, _ = stats.pearsonr(a, b)
            rho, _ = stats.spearmanr(a, b)
            tau, _ = stats.kendalltau(a, b)
    ai = [int(round(x)) for x in a]
    bi = [int(round(x)) for x in b]
    return {"n": n, "pearson_r": float(r), "spearman_rho": float(rho),
            "kendall_tau": float(tau), "qw_kappa": quadratic_weighted_kappa(ai, bi)}


def fmt(v: float) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return "  N/A"
    return f"{v:6.3f}"


def print_table(rows: list[dict[str, Any]]) -> None:
    header = f"{'criterion':<26} {'N':>4} {'Pearson r':>10} {'Spearman p':>11} {'Kendall t':>10} {'QW-k':>8}"
    print(header)
    print("-" * len(header))
    for row in rows:
        print(f"{row['label']:<26} {row['n']:>4} {fmt(row['pearson_r']):>10} {fmt(row['spearman_rho']):>11} {fmt(row['kendall_tau']):>10} {fmt(row['qw_kappa']):>8}")


def write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "n"] + METRIC_COLS)
        for row in rows:
            writer.writerow([
                row["label"], row["n"],
                "" if np.isnan(row["pearson_r"]) else f"{row['pearson_r']:.6f}",
                "" if np.isnan(row["spearman_rho"]) else f"{row['spearman_rho']:.6f}",
                "" if np.isnan(row["kendall_tau"]) else f"{row['kendall_tau']:.6f}",
                "" if np.isnan(row["qw_kappa"]) else f"{row['qw_kappa']:.6f}",
            ])
    print(f"[ok] {path}")


def discover_human_scoring_csvs(test_dir: Path, domains: set[str] | None) -> list[Path]:
    return sorted(
        path
        for path in test_dir.glob("*/human_*_scoring.csv")
        if path.parent.is_dir() and (domains is None or path.parent.name in domains)
    )


def llm_path_for_human(human_path: Path) -> Path:
    prefix = "human_"
    suffix = "_scoring.csv"
    if not human_path.name.startswith(prefix) or not human_path.name.endswith(suffix):
        raise ValueError(f"Not a human scoring file: {human_path}")
    llm_name = human_path.name[len(prefix):-len(suffix)] + "_scored.csv"
    return human_path.with_name(llm_name)


def variant_name(llm_path: Path) -> str:
    name = llm_path.stem
    if name.startswith("extracted_triples_"):
        name = name[len("extracted_triples_"):]
    return name.removesuffix("_scored")


def calculate_results(
    llm: dict[str, dict[str, int | None]],
    human: dict[str, dict[str, int | None]],
    criteria: list[str],
) -> list[dict[str, Any]]:
    common = set(llm) & set(human)
    if not common:
        raise ValueError("No common instance_ids; cannot correlate.")

    results: list[dict[str, Any]] = []
    for crit in criteria:
        a, b = aligned_pairs(llm, human, crit)
        row = {"label": crit}
        row.update(compute_row(a, b))
        results.append(row)

    task_groups = {
        "text": [c for c in criteria if c.startswith("text_")],
        "triples": [c for c in criteria if c.startswith("triples_")],
    }
    for task, task_criteria in task_groups.items():
        if not task_criteria:
            continue

        pooled_a, pooled_b = [], []
        for inst in sorted(common, key=lambda x: int(x) if x.isdigit() else x):
            for crit in task_criteria:
                av = llm[inst].get(crit)
                bv = human[inst].get(crit)
                if av is not None and bv is not None:
                    pooled_a.append(av)
                    pooled_b.append(bv)
        pooled_row = {"label": f"overall_{task} (pooled)"}
        pooled_row.update(compute_row(pooled_a, pooled_b))
        results.append(pooled_row)

        mean_a, mean_b = [], []
        for inst in sorted(common, key=lambda x: int(x) if x.isdigit() else x):
            av = [llm[inst].get(c) for c in task_criteria]
            bv = [human[inst].get(c) for c in task_criteria]
            if all(x is not None for x in av) and all(x is not None for x in bv):
                mean_a.append(float(np.mean(av)))
                mean_b.append(float(np.mean(bv)))
        mean_row = {"label": f"overall_{task} (mean)"}
        mean_metrics_cont = compute_row_cont(mean_a, mean_b)
        mean_row.update(mean_metrics_cont)
        results.append(mean_row)

    return results


def batch_results(
    test_dir: Path,
    domains: set[str] | None,
    criteria: list[str],
) -> list[dict[str, Any]]:
    human_paths = discover_human_scoring_csvs(test_dir, domains)
    if not human_paths:
        raise SystemExit(f"No human_*_scoring.csv files found under {test_dir}")

    rows: list[dict[str, Any]] = []
    for human_path in human_paths:
        llm_path = llm_path_for_human(human_path)
        if not llm_path.exists():
            logger.warning("Missing LLM counterpart for %s: %s", human_path, llm_path)
            continue

        llm = load_csv(llm_path, criteria)
        human = load_csv(human_path, criteria)
        only_llm = set(llm) - set(human)
        only_human = set(human) - set(llm)
        if only_llm or only_human:
            logger.warning(
                "%s: %d instance(s) only in LLM CSV, %d only in human CSV",
                human_path,
                len(only_llm),
                len(only_human),
            )

        try:
            pair_results = calculate_results(llm, human, criteria)
        except ValueError as exc:
            logger.warning("Skipping %s: %s", human_path, exc)
            continue
        for result in pair_results:
            rows.append({
                "domain": human_path.parent.name,
                "variant": variant_name(llm_path),
                "criterion": result["label"],
                "n": result["n"],
                **{metric: result[metric] for metric in METRIC_COLS},
            })
        logger.info("%s: %d common instances", human_path, len(set(llm) & set(human)))

    if not rows:
        raise SystemExit("No human/LLM pairs could be correlated.")
    return rows


def write_batch_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["domain", "variant", "criterion", "n"] + METRIC_COLS
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output = {key: row[key] for key in fieldnames}
            for metric in METRIC_COLS:
                value = output[metric]
                output[metric] = "" if np.isnan(value) else f"{value:.6f}"
            writer.writerow(output)
    print(f"[ok] {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm", help="Path to the LLM-scored CSV.")
    parser.add_argument("--human", help="Path to the human-scored CSV.")
    parser.add_argument(
        "--test-dir",
        help="Directory containing domain folders with human_*_scoring.csv files.",
    )
    parser.add_argument(
        "--domains",
        default=None,
        help="Comma-separated domains to include in --test-dir mode; default all.",
    )
    parser.add_argument("--criteria", default=",".join(CRITERIA),
                        help="Comma-separated criterion column names to use.")
    parser.add_argument("--out-csv", default=None, help="Optional path to write a tidy summary CSV.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    criteria = [c.strip() for c in args.criteria.split(",") if c.strip()]
    if not criteria:
        raise SystemExit("No criteria specified.")

    if bool(args.llm) != bool(args.human):
        raise SystemExit("--llm and --human must be provided together.")
    if args.test_dir and (args.llm or args.human):
        raise SystemExit("Use either --test-dir or --llm/--human, not both.")

    if args.test_dir:
        test_dir = Path(args.test_dir)
        if not test_dir.is_dir():
            raise SystemExit(f"Test directory not found: {test_dir}")
        domains = {d.strip() for d in args.domains.split(",") if d.strip()} if args.domains else None
        results = batch_results(test_dir, domains, criteria)
        out_path = Path(args.out_csv) if args.out_csv else test_dir / "correlation_results.csv"
        write_batch_csv(out_path, results)
        return

    if not args.llm or not args.human:
        raise SystemExit("Provide --test-dir or both --llm and --human.")

    llm_path = Path(args.llm)
    human_path = Path(args.human)
    if not llm_path.exists():
        raise SystemExit(f"LLM CSV not found: {llm_path}")
    if not human_path.exists():
        raise SystemExit(f"Human CSV not found: {human_path}")

    llm = load_csv(llm_path, criteria)
    human = load_csv(human_path, criteria)
    only_llm = set(llm) - set(human)
    only_human = set(human) - set(llm)
    if only_llm:
        logger.warning("%d instance(s) only in LLM CSV: %s", len(only_llm), sorted(only_llm)[:5])
    if only_human:
        logger.warning("%d instance(s) only in human CSV: %s", len(only_human), sorted(only_human)[:5])
    logger.info("LLM instances: %d, human instances: %d, common: %d", len(llm), len(human), len(set(llm) & set(human)))

    results = calculate_results(llm, human, criteria)
    print_table(results)
    if args.out_csv:
        write_summary_csv(Path(args.out_csv), results)


if __name__ == "__main__":
    main()
