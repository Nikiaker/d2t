"""CSV loading/saving and domain/pipeline metadata for the scoring GUI."""

from __future__ import annotations

import csv
import os
import tempfile

def _resolve_data_root() -> str:
    """Data root: SCORING_GUI_DATA env -> bundle layout (<root>/data) -> repo layout."""
    env = os.environ.get("SCORING_GUI_DATA")
    if env:
        return os.path.normpath(env)
    parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    bundle = os.path.join(parent, "data")
    if os.path.isdir(bundle):
        return bundle
    return os.path.join(parent, "outputs", "test10")


TEST10_ROOT = _resolve_data_root()

GUIDELINES_PATH = os.path.join(TEST10_ROOT, "guidelines.md")

# Display name -> subdirectory inside test10/
DOMAINS = {
    "ice_hockey": "ice_hockey_match",
    "mobile_phone": "mobile_phone_specification",
    "owid": "owid",
    "weather_forecast": "weather_forecast",
    "wikidata": "wikidata",
}

# CSV file stem -> friendly pipeline label
PIPELINE_LABELS = {
    "extracted_triples_rules_text_pipeline": "Rules-Iterative Refinement",
    "extracted_triples_text_pipeline": "Text-First Extraction with Normalization",
    "extracted_triples_text_predicate_catalog_stable": "Evolving Catalog",
}

# The four columns the evaluator fills (per guidelines.md)
SCORE_COLUMNS = [
    "text_summary",
    "text_faithfulness",
    "triples_completeness",
    "triples_omissions",
]

SCORE_LABELS = {
    "text_summary": ("Text", "Summary", "Is the text a concise, coherent summary of the source data?"),
    "text_faithfulness": ("Text", "Faithfulness", "Is every claim in the text grounded in the source data?"),
    "triples_completeness": ("Triples", "Completeness", "Do the triples cover all main points of the text?"),
    "triples_omissions": ("Triples", "Omissions", "What do the triples leave out? Higher = fewer harmful omissions."),
}


def list_scoring_files(domain: str) -> list[tuple[str, str]]:
    """Return (label, absolute path) for every *_scoring.csv in the domain dir."""
    subdir = os.path.join(TEST10_ROOT, DOMAINS[domain])
    found = []
    for name in sorted(os.listdir(subdir)):
        if not name.endswith("_scoring.csv"):
            continue
        stem = name[: -len("_scoring.csv")]
        if stem.startswith("human_"):
            continue  # human copies are not scored through the GUI
        label = PIPELINE_LABELS.get(stem, stem)
        found.append((label, os.path.join(subdir, name)))
    return found


class ScoringFile:
    """In-memory model of one *_scoring.csv file with read/write support."""

    def __init__(self, path: str):
        self.path = path
        with open(path, newline="", encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            self.fieldnames = list(reader.fieldnames or [])
            self.rows = [dict(r) for r in reader]
        self.rows.sort(key=lambda r: self._id(r))
        for missing in SCORE_COLUMNS:
            if missing not in self.fieldnames:
                raise ValueError(f"{path} is missing required column {missing!r}")

    @staticmethod
    def _id(row: dict) -> int:
        try:
            return int(row.get("instance_id", ""))
        except ValueError:
            return 0

    def row(self, index: int) -> dict:
        return self.rows[index]

    def scores(self, index: int) -> dict[str, str]:
        row = self.rows[index]
        return {col: (row.get(col) or "").strip() for col in SCORE_COLUMNS}

    def is_evaluated(self, index: int) -> bool:
        return all(v for v in self.scores(index).values())

    def evaluated_count(self) -> int:
        return sum(1 for i in range(len(self.rows)) if self.is_evaluated(i))

    def save_scores(self, index: int, scores: dict[str, str]) -> None:
        """Update the four score columns for one row and rewrite the same file atomically."""
        row = self.rows[index]
        for col in SCORE_COLUMNS:
            row[col] = scores.get(col, "")
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=os.path.dirname(self.path), prefix=".scoring_tmp_", suffix=".csv"
        )
        try:
            with os.fdopen(tmp_fd, "w", newline="", encoding="utf-8-sig") as fh:
                writer = csv.DictWriter(fh, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(self.rows)
            os.replace(tmp_path, self.path)
        except BaseException:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise
