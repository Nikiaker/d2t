import argparse
import io
import json
import logging
from dataclasses import asdict
from json import JSONDecodeError
from pathlib import Path
from typing import Any

from openai import OpenAI

from app import (
    EXTRACTION_RESPONSE_FORMAT,
    Triple,
    call_llm_json,
    extract_instances,
    parse_json_response,
    read_openai_file_text,
    wait_for_batch_completion,
)

logger = logging.getLogger(__name__)

TEXT_GENERATION_SYSTEM_PROMPT = (
    "You convert one structured data instance into concise natural language. "
    "Return ONLY JSON with schema: {\"text\":\"...\"}. "
    "Capture the most important information, trends, extremes, and notable conditions. "
    "If the instance contains a time series (for example a weather forecast), summarize it at a high level "
    "instead of listing every point."
)

TEXT_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "instance_text_generation",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
        },
    },
}

FIRST_INSTANCE_TRIPLES_SYSTEM_PROMPT = (
    "You extract semantic triples from text. "
    "Return ONLY JSON with this exact schema: "
    '{"triples":[{"subject":"...","predicate":"...","object":"..."}]}. '
    "Use concise predicate labels in lower_snake_case when possible and avoid duplicates."
)

CATALOG_GUIDED_TRIPLES_SYSTEM_PROMPT = (
    "You extract semantic triples from text using a predicate catalog with examples. "
    "Return ONLY JSON with this exact schema: "
    '{"triples":[{"subject":"...","predicate":"...","object":"..."}]}. '
    "Use only predicates from the provided catalog when possible. "
    "Introduce a new predicate only when none of the catalog predicates can describe the fact."
)


def build_text_generation_batch_jsonl(
    model: str,
    text_generation_system_prompt: str,
    instances: list[dict[str, Any]],
) -> str:
    lines: list[str] = []

    for instance in instances:
        instance_id = instance.get("instance_id")
        user_prompt = (
            "Create a concise natural-language summary of this ONE data instance.\n\n"
            f"instance_context={json.dumps(instance, ensure_ascii=False)}\n\n"
            "Return JSON only."
        )
        request_payload = {
            "custom_id": f"instance-{instance_id}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "system", "content": text_generation_system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": TEXT_RESPONSE_FORMAT,
            },
        }
        lines.append(json.dumps(request_payload, ensure_ascii=False))

    return "\n".join(lines) + "\n"


def parse_text_generation_batch_output(output_text: str) -> dict[int, str]:
    text_by_instance_id: dict[int, str] = {}

    for raw_line in output_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        entry = json.loads(line)
        custom_id = str(entry.get("custom_id", ""))
        if not custom_id.startswith("instance-"):
            continue

        try:
            instance_id = int(custom_id.split("instance-", 1)[1])
        except ValueError:
            logger.warning("Skipping text batch item with invalid custom_id: %s", custom_id)
            continue

        response_obj = entry.get("response")
        if not isinstance(response_obj, dict):
            logger.warning("Missing response for text generation instance %s", instance_id)
            text_by_instance_id[instance_id] = ""
            continue

        body = response_obj.get("body") or {}
        choices = body.get("choices") or []
        if not choices:
            logger.warning("No choices returned for text generation instance %s", instance_id)
            text_by_instance_id[instance_id] = ""
            continue

        content = str(((choices[0] or {}).get("message") or {}).get("content") or "")
        try:
            result = parse_json_response(content)
            text_by_instance_id[instance_id] = str(result.get("text", "")).strip()
        except (JSONDecodeError, ValueError) as exc:
            logger.warning(
                "Invalid JSON in text-generation batch output for instance %s: %s",
                instance_id,
                exc,
            )
            text_by_instance_id[instance_id] = ""

    return text_by_instance_id


def generate_texts_from_instances_batch(
    client: OpenAI,
    model: str,
    text_generation_system_prompt: str,
    instances: list[dict[str, Any]],
    batch_timeout_seconds: int,
) -> dict[int, str]:
    if not instances:
        return {}

    batch_jsonl = build_text_generation_batch_jsonl(
        model=model,
        text_generation_system_prompt=text_generation_system_prompt,
        instances=instances,
    )
    batch_jsonl_bytes = batch_jsonl.encode("utf-8")
    logger.info("Text-generation batch file size: %d bytes", len(batch_jsonl_bytes))

    input_file = client.files.create(
        file=("instance_text_generation_batch.jsonl", io.BytesIO(batch_jsonl_bytes)),
        purpose="batch",
    )

    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("Started text-generation batch: %s", batch.id)

    final_batch = wait_for_batch_completion(
        client=client,
        batch_id=batch.id,
        timeout_seconds=batch_timeout_seconds,
    )

    if getattr(final_batch, "status", None) != "completed":
        raise RuntimeError(
            f"Text-generation batch {batch.id} did not complete successfully: {final_batch.status}"
        )

    output_file_id = getattr(final_batch, "output_file_id", None)
    if not output_file_id:
        raise RuntimeError(f"Text-generation batch {batch.id} completed but has no output_file_id")

    output_text = read_openai_file_text(client=client, file_id=output_file_id)
    return parse_text_generation_batch_output(output_text)


def _triples_from_result(result: dict[str, Any]) -> list[Triple]:
    triples: list[Triple] = []
    for t in result.get("triples", []):
        subject = str(t.get("subject", "")).strip()
        predicate = str(t.get("predicate", "")).strip()
        obj = str(t.get("object", "")).strip()
        if subject and predicate and obj:
            triples.append(Triple(subject=subject, predicate=predicate, object=obj))
    return triples


def extract_first_instance_triples(
    client: OpenAI,
    model: str,
    text: str,
) -> list[Triple]:
    user_prompt = (
        "Extract semantic triples from this text.\n\n"
        f"text={json.dumps(text, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=FIRST_INSTANCE_TRIPLES_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=EXTRACTION_RESPONSE_FORMAT,
    )
    return _triples_from_result(result)


def extract_catalog_guided_triples(
    client: OpenAI,
    model: str,
    text: str,
    predicate_examples: list[dict[str, Any]],
) -> list[Triple]:
    user_prompt = (
        "Extract semantic triples from this text.\n\n"
        "Use predicates from catalog if possible. If none can express a fact, only then use a new predicate.\n\n"
        f"predicate_catalog={json.dumps(predicate_examples, ensure_ascii=False)}\n"
        f"text={json.dumps(text, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=CATALOG_GUIDED_TRIPLES_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=EXTRACTION_RESPONSE_FORMAT,
    )
    return _triples_from_result(result)


def cmd_extract(args: argparse.Namespace) -> None:
    logger.info("OpenAI base URL: %s", args.base_url)
    logger.info("Model: %s", args.model)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    instances = extract_instances(payload, top_level_key=args.top_level_key)
    instances_num = len(instances)
    logger.info("Extracted %d instances from input JSON", instances_num)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logger.info("Generating text for all instances...")
    text_by_instance_id = generate_texts_from_instances_batch(
        client=client,
        model=args.model,
        text_generation_system_prompt=TEXT_GENERATION_SYSTEM_PROMPT,
        instances=instances,
        batch_timeout_seconds=args.batch_timeout_seconds,
    )

    all_triples: list[Triple] = []
    triples_by_instance: list[dict[str, Any]] = []
    generated_text_by_instance: list[dict[str, Any]] = []

    predicate_example_by_name: dict[str, dict[str, Any]] = {}
    predicate_discoveries: list[dict[str, Any]] = []

    for i, instance in enumerate(instances):
        instance_id = int(instance["instance_id"])
        text = text_by_instance_id.get(instance_id, "")

        generated_text_by_instance.append(
            {
                "instance_id": instance_id,
                "text": text,
            }
        )

        if not text:
            triples: list[Triple] = []
        elif i == 0:
            triples = extract_first_instance_triples(client=client, model=args.model, text=text)
        else:
            catalog = list(predicate_example_by_name.values())
            triples = extract_catalog_guided_triples(
                client=client,
                model=args.model,
                text=text,
                predicate_examples=catalog,
            )

        for triple in triples:
            if triple.predicate not in predicate_example_by_name:
                predicate_example_by_name[triple.predicate] = {
                    "predicate": triple.predicate,
                    "example_triple": asdict(triple),
                }
                predicate_discoveries.append(
                    {
                        "instance_id": instance_id,
                        "predicate": triple.predicate,
                        "example_triple": asdict(triple),
                    }
                )

        triples_by_instance.append(
            {
                "instance_id": instance_id,
                "triples": [asdict(t) for t in triples],
            }
        )
        all_triples.extend(triples)
        logger.info("Processed instance %d/%d", i + 1, instances_num)

    predicate_catalog = list(predicate_example_by_name.values())
    unique_predicates = [entry["predicate"] for entry in predicate_catalog]

    output = {
        "input_file": args.input,
        "instances_count": len(instances),
        "triples_count": len(all_triples),
        "unique_predicates": unique_predicates,
        "predicate_catalog": predicate_catalog,
        "predicate_discoveries": predicate_discoveries,
        "generated_text_by_instance": generated_text_by_instance,
        "triples_by_instance": triples_by_instance,
        "all_triples": [asdict(t) for t in all_triples],
    }

    Path(args.output).write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Extraction complete. Results saved to %s", args.output)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Text-first triple extraction with evolving predicate catalog and examples."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output extraction results")
    parser.add_argument("--model", required=True, help="Model name served by vLLM/OpenAI-compatible API")
    parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")
    parser.add_argument(
        "--batch-timeout-seconds",
        type=int,
        default=1800,
        help="Max seconds to wait for text-generation batch completion",
    )
    parser.add_argument(
        "--top-level-key",
        default=None,
        help="Top-level JSON key containing instances. Use 'none' if instances are at top level as a list. If not specified, auto-detects.",
    )

    args = parser.parse_args()
    cmd_extract(args)


if __name__ == "__main__":
    main()
