"""Run final_test.py while retaining metrics from earlier single-judge passes."""

import json
import os
import runpy
import tempfile
from pathlib import Path
from typing import Any


FIRST_JUDGE_METRICS = {"gramatic", "ommisions", "additions"}


def merge_scores(existing: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Keep previous judge metrics and first-judge diagnostic metrics."""
    existing_metrics = existing.get("metrics", {})
    current_metrics = current.get("metrics", {})

    if not isinstance(existing_metrics, dict) or not isinstance(current_metrics, dict):
        return current

    merged_metrics = dict(existing_metrics)
    merged_metrics.update(current_metrics)
    for metric in FIRST_JUDGE_METRICS:
        if metric in existing_metrics:
            merged_metrics[metric] = existing_metrics[metric]

    merged = dict(current)
    merged["metrics"] = merged_metrics
    return merged


def load_scores(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Scores file must contain a JSON object: {path}")
    return data


def main() -> None:
    scores_path = Path("scores.json")
    backup_path: Path | None = None

    try:
        if scores_path.exists() and os.getenv("FINAL_TEST_MERGE_RESET") != "1":
            with tempfile.NamedTemporaryFile(
                dir=scores_path.parent,
                prefix="scores-before-merge-",
                suffix=".json",
                delete=False,
            ) as backup_file:
                backup_path = Path(backup_file.name)
            scores_path.replace(backup_path)

        runpy.run_path(str(Path(__file__).with_name("final_test.py")), run_name="__main__")

        if backup_path is not None:
            merged = merge_scores(load_scores(backup_path), load_scores(scores_path))
            scores_path.write_text(json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    except BaseException:
        if backup_path is not None and backup_path.exists():
            if scores_path.exists():
                scores_path.unlink()
            backup_path.replace(scores_path)
        raise
    finally:
        if backup_path is not None and backup_path.exists():
            backup_path.unlink()


if __name__ == "__main__":
    main()
