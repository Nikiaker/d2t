"""LLM-as-a-judge batch scorer for the scoring CSVs.

Reads every *_scoring.csv under a test output directory, builds ONE combined
OpenAI Batch with 4 judge requests per row (one per criterion: summary,
completeness, faithfulness, omissions), submits it, waits for completion, and
writes <stem>_scored.csv next to each input CSV with the four score columns
filled in, plus a <stem>_judge_reasons.json sidecar with the judge's reasons.

python3 tripler/judge_scoring_batch.py \
  --model google/gemma-4-31B-it \
  --base-url http://localhost:2996/v1 \
  --api-key none \
  --test-dir tripler/outputs/test8 \
  --batch-timeout-seconds 7200
# optional: --domains ice_hockey_match,wikidata --force --no-reasons --poll-interval-seconds 10
"""

import argparse
import csv
import io
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from app import (
    parse_json_response,
    read_openai_file_text,
    wait_for_batch_completion,
)

logger = logging.getLogger(__name__)

CRITERIA = ["summary", "completeness", "faithfulness", "omissions"]
SCORE_COLUMNS = CRITERIA
HEADER = ["instance_id", "domain", "input_data", "generated_text", "generated_triples"] + CRITERIA
STATE_FILENAME = "_judge_batch_state.json"
TRIPLE_SEP = " ; "


JUDGE_SYSTEM_PROMPTS: dict[str, str] = {
    "summary": (
        "You are a strict judge evaluating a data-to-text and data-to-triples conversion. "
        "You will see: (1) the original structured data instance, (2) the natural-language text "
        "generated from it, and (3) the semantic triples generated from it. "
        "Rate how well the text AND triples JOINTLY summarize the input on a 1-5 scale. "
        "5 = all key information is captured concisely and correctly in both the text and the triples. "
        "3 = the most important aspects are captured but with notable gaps or verbosity. "
        "1 = essentially nothing of the input is represented. "
        "Return ONLY JSON with this exact schema: "
        '{"score": <integer 1-5>, "reason": "<one short sentence>"}'
    ),
    "completeness": (
        "You are a strict judge evaluating a data-to-text and data-to-triples conversion. "
        "You will see: (1) the original structured data instance, (2) the natural-language text "
        "generated from it, and (3) the semantic triples generated from it. "
        "Rate what fraction of the RELEVANT input information is represented in the text and/or the triples, on a 1-5 scale. "
        "5 = every relevant attribute, entity, value, and relationship from the input appears in at least one of the two representations. "
        "3 = the main entities and the primary facts are present, but several secondary attributes are missing. "
        "1 = almost no relevant information is present. "
        "Return ONLY JSON with this exact schema: "
        '{"score": <integer 1-5>, "reason": "<one short sentence>"}'
    ),
    "faithfulness": (
        "You are a strict judge evaluating a data-to-text and data-to-triples conversion. "
        "You will see: (1) the original structured data instance, (2) the natural-language text "
        "generated from it, and (3) the semantic triples generated from it. "
        "Rate whether the text and the triples are FAITHFUL to the input, i.e. every claim they make is directly grounded in the input with NO fabrication or distortion, on a 1-5 scale. "
        "5 = fully grounded; nothing in the text or triples contradicts or extends the input. "
        "3 = mostly grounded but with one or two unsupported or slightly distorted claims. "
        "1 = major hallucinations or contradictions relative to the input. "
        "Return ONLY JSON with this exact schema: "
        '{"score": <integer 1-5>, "reason": "<one short sentence>"}'
    ),
    "omissions": (
        "You are a strict judge evaluating a data-to-text and data-to-triples conversion. "
        "You will see: (1) the original structured data instance, (2) the natural-language text "
        "generated from it, and (3) the semantic triples generated from it. "
        "Rate how FEW important pieces of information are missing from the text and the triples combined, on an inverted 1-5 scale. "
        "5 = no significant omission; all key fields, entities, values, and relationships are present. "
        "3 = some important but non-central information is missing. "
        "1 = most key fields or entities are omitted. "
        "Return ONLY JSON with this exact schema: "
        '{"score": <integer 1-5>, "reason": "<one short sentence>"}'
    ),
}

JUDGE_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "judge_score",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "score": {"type": "integer"},
                "reason": {"type": "string"},
            },
            "required": ["score", "reason"],
        },
    },
}


def discover_scoring_csvs(test_dir: Path, domains: list[str] | None) -> list[Path]:
    csvs: list[Path] = []
    for domain_dir in sorted(test_dir.iterdir()):
        if not domain_dir.is_dir():
            continue
        if domains and domain_dir.name not in set(domains):
            continue
        for path in sorted(domain_dir.glob("*_scoring.csv")):
            csvs.append(path)
    return csvs


def read_scoring_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def build_judge_batch_jsonl(
    model: str,
    csv_paths: list[Path],
    rows_by_idx: list[list[dict[str, str]]],
) -> str:
    lines: list[str] = []
    for csv_idx, rows in enumerate(rows_by_idx):
        for row in rows:
            instance_id = row["instance_id"]
            input_data = row.get("input_data", "")
            generated_text = row.get("generated_text", "")
            generated_triples = row.get("generated_triples", "")
            user_prompt = (
                "Judge this single conversion.\n\n"
                f"instance_id={instance_id}\n\n"
                "=== INPUT DATA (JSON) ===\n"
                f"{input_data}\n\n"
                "=== GENERATED TEXT ===\n"
                f"{generated_text}\n\n"
                "=== GENERATED TRIPLES ===\n"
                f"{generated_triples}\n\n"
                "Return JSON only."
            )
            for criterion in CRITERIA:
                custom_id = f"{csv_idx}:{instance_id}:{criterion}"
                request_payload = {
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": JUDGE_SYSTEM_PROMPTS[criterion]},
                            {"role": "user", "content": user_prompt},
                        ],
                        "response_format": JUDGE_RESPONSE_FORMAT,
                    },
                }
                lines.append(json.dumps(request_payload, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def parse_judge_batch_output(output_text: str) -> dict[str, dict[str, Any]]:
    results: dict[str, dict[str, Any]] = {}
    for raw_line in output_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            logger.warning("Skipping unparseable batch output line: %s", exc)
            continue
        custom_id = str(entry.get("custom_id", ""))
        response_obj = entry.get("response")
        if not isinstance(response_obj, dict):
            logger.warning("Missing response for custom_id=%s", custom_id)
            results[custom_id] = {"score": None, "reason": ""}
            continue
        body = response_obj.get("body") or {}
        choices = body.get("choices") or []
        if not choices:
            logger.warning("No choices returned for custom_id=%s", custom_id)
            results[custom_id] = {"score": None, "reason": ""}
            continue
        content = str(((choices[0] or {}).get("message") or {}).get("content") or "")
        try:
            parsed = parse_json_response(content)
            score_raw = parsed.get("score")
            try:
                score = int(score_raw)
            except (TypeError, ValueError):
                score = None
            reason = str(parsed.get("reason", "")).strip()
            results[custom_id] = {"score": score, "reason": reason}
        except Exception as exc:
            logger.warning("Invalid JSON in judge output for custom_id=%s: %s", custom_id, exc)
            results[custom_id] = {"score": None, "reason": ""}
    return results


def submit_batch(client: OpenAI, jsonl_text: str) -> Any:
    jsonl_bytes = jsonl_text.encode("utf-8")
    logger.info("Judge batch file size: %d bytes", len(jsonl_bytes))
    input_file = client.files.create(
        file=("judge_scoring_batch.jsonl", io.BytesIO(jsonl_bytes)),
        purpose="batch",
    )
    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("Started judge batch: %s", batch.id)
    return batch


def load_state(state_path: Path) -> dict[str, Any] | None:
    if not state_path.exists():
        return None
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning("Could not parse state file %s: %s", state_path, exc)
        return None


def save_state(state_path: Path, state: dict[str, Any]) -> None:
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def write_scored_outputs(
    csv_paths: list[Path],
    rows_by_idx: list[list[dict[str, str]]],
    results: dict[str, dict[str, Any]],
    write_reasons: bool,
) -> None:
    for csv_idx, (csv_path, rows) in enumerate(zip(csv_paths, rows_by_idx)):
        out_path = csv_path.with_name(csv_path.stem.replace("_scoring", "_scored") + ".csv")
        reasons_path = csv_path.with_name(csv_path.stem.replace("_scoring", "_judge_reasons") + ".json")
        reasons: dict[str, dict[str, str]] = {}
        with out_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow(HEADER)
            for row in rows:
                instance_id = row["instance_id"]
                score_cells = []
                instance_reasons: dict[str, str] = {}
                for criterion in CRITERIA:
                    custom_id = f"{csv_idx}:{instance_id}:{criterion}"
                    result = results.get(custom_id, {})
                    score = result.get("score")
                    score_cells.append(str(score) if score is not None else "")
                    if write_reasons:
                        instance_reasons[criterion] = result.get("reason", "")
                if write_reasons:
                    reasons[instance_id] = instance_reasons
                writer.writerow([
                    instance_id,
                    row.get("domain", ""),
                    row.get("input_data", ""),
                    row.get("generated_text", ""),
                    row.get("generated_triples", ""),
                    *score_cells,
                ])
        print(f"[ok] {out_path}")
        if write_reasons:
            reasons_path.write_text(json.dumps(reasons, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"[ok] {reasons_path}")


def all_outputs_exist(csv_paths: list[Path]) -> bool:
    if not csv_paths:
        return False
    for csv_path in csv_paths:
        out_path = csv_path.with_name(csv_path.stem.replace("_scoring", "_scored") + ".csv")
        if not out_path.exists():
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Model name served by the OpenAI-compatible API.")
    parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL.")
    parser.add_argument("--api-key", default="local-key", help="API key accepted by the server.")
    parser.add_argument("--test-dir", default="tripler/outputs/test8", help="Directory containing per-domain output folders.")
    parser.add_argument("--domains", default=None, help="Comma-separated domain names to include; default all.")
    parser.add_argument("--batch-timeout-seconds", type=int, default=7200, help="Max seconds to wait for the batch.")
    parser.add_argument("--force", action="store_true", help="Re-submit even if scored outputs already exist.")
    parser.add_argument("--no-reasons", action="store_true", help="Do not write the _judge_reasons.json sidecar.")
    parser.add_argument("--poll-interval-seconds", type=int, default=10, help="Seconds between batch status polls.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    test_dir = Path(args.test_dir)
    if not test_dir.is_dir():
        raise SystemExit(f"Test directory not found: {test_dir}")

    domains = None
    if args.domains:
        domains = [d.strip() for d in args.domains.split(",")]

    csv_paths = discover_scoring_csvs(test_dir, domains)
    if not csv_paths:
        raise SystemExit("No *_scoring.csv files found.")
    logger.info("Found %d scoring CSV(s):", len(csv_paths))
    for p in csv_paths:
        logger.info("  %s", p)

    if all_outputs_exist(csv_paths) and not args.force:
        print("All _scored.csv outputs already exist; nothing to do (use --force to re-run).")
        return

    rows_by_idx = [read_scoring_csv(p) for p in csv_paths]
    total_rows = sum(len(r) for r in rows_by_idx)
    logger.info("Total instances: %d; total judge requests: %d", total_rows, total_rows * len(CRITERIA))

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    state_path = test_dir / STATE_FILENAME
    state = None if args.force else load_state(state_path)

    if state and state.get("batch_id"):
        batch_id = state["batch_id"]
        logger.info("Resume: polling existing batch %s", batch_id)
        final_batch = wait_for_batch_completion(
            client=client,
            batch_id=batch_id,
            timeout_seconds=args.batch_timeout_seconds,
            poll_interval_seconds=args.poll_interval_seconds,
        )
    else:
        jsonl_text = build_judge_batch_jsonl(args.model, csv_paths, rows_by_idx)
        batch = submit_batch(client, jsonl_text)
        save_state(state_path, {
            "batch_id": batch.id,
            "csv_paths": [str(p) for p in csv_paths],
            "model": args.model,
            "created_at": time.time(),
        })
        final_batch = wait_for_batch_completion(
            client=client,
            batch_id=batch.id,
            timeout_seconds=args.batch_timeout_seconds,
            poll_interval_seconds=args.poll_interval_seconds,
        )

    if getattr(final_batch, "status", None) != "completed":
        raise RuntimeError(f"Batch {getattr(final_batch, 'id', '?')} did not complete: {final_batch.status}")

    output_file_id = getattr(final_batch, "output_file_id", None)
    if not output_file_id:
        raise RuntimeError(f"Batch {final_batch.id} completed but has no output_file_id")

    output_text = read_openai_file_text(client=client, file_id=output_file_id)
    results = parse_judge_batch_output(output_text)
    logger.info("Parsed %d judge results", len(results))

    write_scored_outputs(csv_paths, rows_by_idx, results, write_reasons=not args.no_reasons)

    if state_path.exists():
        state_path.unlink()
    print("Done.")


if __name__ == "__main__":
    main()