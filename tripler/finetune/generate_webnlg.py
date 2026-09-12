#!/usr/bin/env python3
"""Run a fine-tuned joint text-and-triples model over raw JSON instances.

The request prompt and response shape intentionally match ``build_dataset.py``.
The resulting JSON is directly consumable by ``tripler/json_to_xml_converter.py``.

Example::

    python generate_webnlg.py \
        --input tripler/inputs/seed_2994/owid_dev_2994.json \
        --output tripler/outputs/webnlg_seed_2994/json/owid_dev_2994.json \
        --model /raid/.../owid_gemma4_31b_regularized_capacity_merged \
        --base-url http://localhost:3001/v1 \
        --top-level-key none
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import re
from pathlib import Path
from typing import Any

from openai import OpenAI

_TRIPLER_DIR = Path(__file__).resolve().parents[1]
import sys

if str(_TRIPLER_DIR) not in sys.path:
    sys.path.insert(0, str(_TRIPLER_DIR))

from app import extract_instances, parse_json_response, read_openai_file_text, wait_for_batch_completion  # noqa: E402
from joint_prompt import SYSTEM_PROMPT, build_user_prompt  # noqa: E402

logger = logging.getLogger(__name__)

JOINT_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "instance_text_and_triples",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "text": {"type": "string"},
                "triples": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "subject": {"type": "string"},
                            "predicate": {"type": "string"},
                            "object": {"type": "string"},
                        },
                        "required": ["subject", "predicate", "object"],
                    },
                },
            },
            "required": ["text", "triples"],
        },
    },
}

_INSTANCE_ID_RE = re.compile(r"^instance-(\d+)$")


def build_batch_jsonl(model: str, instances: list[dict[str, Any]], max_tokens: int) -> str:
    """Build OpenAI batch requests with stable IDs and prompt parity."""
    lines = []
    for instance in instances:
        instance_id = int(instance["instance_id"])
        body = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(instance)},
            ],
            "response_format": JOINT_RESPONSE_FORMAT,
            "temperature": 0.0,
            "max_tokens": max_tokens,
            "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
        }
        lines.append(
            json.dumps(
                {
                    "custom_id": f"instance-{instance_id}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": body,
                },
                ensure_ascii=False,
            )
        )
    return "\n".join(lines) + ("\n" if lines else "")


def _parse_prediction(content: str) -> dict[str, Any]:
    result = parse_json_response(content)
    if not isinstance(result, dict):
        raise ValueError("model response is not a JSON object")

    text = result.get("text", "")
    if not isinstance(text, str):
        raise ValueError("model response field 'text' is not a string")

    triples: list[dict[str, str]] = []
    raw_triples = result.get("triples", [])
    if not isinstance(raw_triples, list):
        raise ValueError("model response field 'triples' is not a list")
    for raw_triple in raw_triples:
        if not isinstance(raw_triple, dict):
            continue
        triple = {
            "subject": str(raw_triple.get("subject", "")).strip(),
            "predicate": str(raw_triple.get("predicate", "")).strip(),
            "object": str(raw_triple.get("object", "")).strip(),
        }
        if all(triple.values()):
            triples.append(triple)
    return {"text": text.strip(), "triples": triples}


def parse_batch_output(output_text: str) -> tuple[dict[int, dict[str, Any]], dict[int, str]]:
    """Parse successful and failed batch rows separately."""
    predictions: dict[int, dict[str, Any]] = {}
    errors: dict[int, str] = {}

    for raw_line in output_text.splitlines():
        if not raw_line.strip():
            continue
        entry = json.loads(raw_line)
        match = _INSTANCE_ID_RE.match(str(entry.get("custom_id", "")))
        if not match:
            continue
        instance_id = int(match.group(1))

        if entry.get("error"):
            errors[instance_id] = json.dumps(entry["error"], ensure_ascii=False)
            continue

        response = entry.get("response") or {}
        body = response.get("body") or {}
        choices = body.get("choices") or []
        if not choices:
            errors[instance_id] = "batch response contains no choices"
            continue
        content = str(((choices[0] or {}).get("message") or {}).get("content") or "")
        try:
            predictions[instance_id] = _parse_prediction(content)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            errors[instance_id] = str(exc)

    return predictions, errors


def _run_batch(
    client: OpenAI,
    model: str,
    instances: list[dict[str, Any]],
    max_tokens: int,
    timeout_seconds: int,
) -> tuple[dict[int, dict[str, Any]], dict[int, str]]:
    batch_jsonl = build_batch_jsonl(model, instances, max_tokens)
    input_file = client.files.create(
        file=("joint_webnlg_generation.jsonl", io.BytesIO(batch_jsonl.encode("utf-8"))),
        purpose="batch",
    )
    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("started batch %s for %d instances", batch.id, len(instances))
    final_batch = wait_for_batch_completion(client, batch.id, timeout_seconds)
    if getattr(final_batch, "status", None) != "completed":
        raise RuntimeError(f"batch {batch.id} ended with status {final_batch.status}")
    output_file_id = getattr(final_batch, "output_file_id", None)
    if not output_file_id:
        raise RuntimeError(f"batch {batch.id} completed without output_file_id")
    output_text = read_openai_file_text(client, output_file_id)
    return parse_batch_output(output_text)


def _chunks(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    if size <= 0:
        return [items]
    return [items[start : start + size] for start in range(0, len(items), size)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True, help="Model name passed to the served vLLM endpoint")
    parser.add_argument("--base-url", default="http://localhost:3001/v1")
    parser.add_argument("--api-key", default="none")
    parser.add_argument("--top-level-key", default="none")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--batch-size", type=int, default=0, help="Requests per batch; 0 submits one batch")
    parser.add_argument("--batch-timeout-seconds", type=int, default=21600)
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"input file does not exist: {args.input}")

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    instances = extract_instances(payload, top_level_key=args.top_level_key)
    logger.info("loaded %d instances from %s", len(instances), args.input)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)
    predictions: dict[int, dict[str, Any]] = {}
    errors: dict[int, str] = {}
    batches = _chunks(instances, args.batch_size)
    for batch_number, batch_instances in enumerate(batches, start=1):
        logger.info("submitting batch %d/%d", batch_number, len(batches))
        batch_predictions, batch_errors = _run_batch(
            client,
            args.model,
            batch_instances,
            args.max_tokens,
            args.batch_timeout_seconds,
        )
        predictions.update(batch_predictions)
        errors.update(batch_errors)

    generated_text_by_instance = []
    triples_by_instance = []
    all_triples = []
    failed_instances = []
    for instance in instances:
        instance_id = int(instance["instance_id"])
        prediction = predictions.get(instance_id, {"text": "", "triples": []})
        if instance_id not in predictions:
            failed_instances.append(
                {"instance_id": instance_id, "error": errors.get(instance_id, "missing batch result")}
            )
        generated_text_by_instance.append({"instance_id": instance_id, "text": prediction["text"]})
        triples_by_instance.append({"instance_id": instance_id, "triples": prediction["triples"]})
        all_triples.extend(prediction["triples"])

    output = {
        "input_file": str(args.input),
        "model": args.model,
        "instances_count": len(instances),
        "parsed_instances_count": len(predictions),
        "failed_instances_count": len(failed_instances),
        "failed_instances": failed_instances,
        "triples_count": len(all_triples),
        "unique_predicates": list(dict.fromkeys(t["predicate"] for t in all_triples)),
        "generated_text_by_instance": generated_text_by_instance,
        "triples_by_instance": triples_by_instance,
        "all_triples": all_triples,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info("wrote %s (%d failures)", args.output, len(failed_instances))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    main()
