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
    EQUIVALENCE_SYSTEM_PROMPT,
    EXTRACTION_RESPONSE_FORMAT,
    Triple,
    extract_instances,
    load_prompt_override,
    normalize_predicates,
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

TRIPLES_FROM_TEXT_SYSTEM_PROMPT = (
    "You extract semantic triples from natural language text. "
    "Return ONLY JSON with this exact schema: "
    '{"triples":[{"subject":"...","predicate":"...","object":"..."}]}. '
    "Rules: preserve the full meaning of the input text, avoid duplicate triples, "
    "and keep predicates in lower_snake_case when possible."
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
                "extra_body": {
                    "chat_template_kwargs": {"enable_thinking": False}
                },
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


def build_triples_from_text_batch_jsonl(
    model: str,
    triples_from_text_system_prompt: str,
    text_by_instance_id: dict[int, str],
) -> str:
    lines: list[str] = []

    for instance_id, text in text_by_instance_id.items():
        if not text:
            continue

        user_prompt = (
            "Extract semantic triples that fully capture the meaning of this text.\n\n"
            f"text={json.dumps(text, ensure_ascii=False)}\n\n"
            "Return JSON only."
        )
        request_payload = {
            "custom_id": f"instance-{instance_id}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "system", "content": triples_from_text_system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": EXTRACTION_RESPONSE_FORMAT,
                "extra_body": {
                    "chat_template_kwargs": {"enable_thinking": False}
                },
            },
        }
        lines.append(json.dumps(request_payload, ensure_ascii=False))

    return "\n".join(lines) + "\n"


def parse_triples_from_text_batch_output(output_text: str) -> dict[int, list[Triple]]:
    triples_by_instance_id: dict[int, list[Triple]] = {}

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
            logger.warning("Skipping triples-from-text batch item with invalid custom_id: %s", custom_id)
            continue

        response_obj = entry.get("response")
        if not isinstance(response_obj, dict):
            logger.warning("Missing response for triples-from-text instance %s", instance_id)
            triples_by_instance_id[instance_id] = []
            continue

        body = response_obj.get("body") or {}
        choices = body.get("choices") or []
        if not choices:
            logger.warning("No choices returned for triples-from-text instance %s", instance_id)
            triples_by_instance_id[instance_id] = []
            continue

        content = str(((choices[0] or {}).get("message") or {}).get("content") or "")
        try:
            result = parse_json_response(content)
        except (JSONDecodeError, ValueError) as exc:
            logger.warning(
                "Invalid JSON in triples-from-text batch output for instance %s: %s",
                instance_id,
                exc,
            )
            triples_by_instance_id[instance_id] = []
            continue

        raw_triples = result.get("triples", [])
        triples: list[Triple] = []
        for triple_entry in raw_triples:
            subject = str(triple_entry.get("subject", "")).strip()
            predicate = str(triple_entry.get("predicate", "")).strip()
            obj = str(triple_entry.get("object", "")).strip()
            if subject and predicate and obj:
                triples.append(Triple(subject=subject, predicate=predicate, object=obj))

        triples_by_instance_id[instance_id] = triples

    return triples_by_instance_id


def triples_from_texts_batch(
    client: OpenAI,
    model: str,
    triples_from_text_system_prompt: str,
    text_by_instance_id: dict[int, str],
    batch_timeout_seconds: int,
) -> dict[int, list[Triple]]:
    if not text_by_instance_id:
        return {}

    batch_jsonl = build_triples_from_text_batch_jsonl(
        model=model,
        triples_from_text_system_prompt=triples_from_text_system_prompt,
        text_by_instance_id=text_by_instance_id,
    )

    if not batch_jsonl.strip():
        return {}

    batch_jsonl_bytes = batch_jsonl.encode("utf-8")
    logger.info("Triples-from-text batch file size: %d bytes", len(batch_jsonl_bytes))

    input_file = client.files.create(
        file=("triples_from_text_batch.jsonl", io.BytesIO(batch_jsonl_bytes)),
        purpose="batch",
    )

    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("Started triples-from-text batch: %s", batch.id)

    final_batch = wait_for_batch_completion(
        client=client,
        batch_id=batch.id,
        timeout_seconds=batch_timeout_seconds,
    )

    if getattr(final_batch, "status", None) != "completed":
        raise RuntimeError(
            f"Triples-from-text batch {batch.id} did not complete successfully: {final_batch.status}"
        )

    output_file_id = getattr(final_batch, "output_file_id", None)
    if not output_file_id:
        raise RuntimeError(f"Triples-from-text batch {batch.id} completed but has no output_file_id")

    output_text = read_openai_file_text(client=client, file_id=output_file_id)
    return parse_triples_from_text_batch_output(output_text)


def cmd_extract(args: argparse.Namespace) -> None:
    logger.info("OpenAI base URL: %s", args.base_url)
    logger.info("Model: %s", args.model)

    text_generation_system_prompt = load_prompt_override(
        args.text_prompt_file,
        TEXT_GENERATION_SYSTEM_PROMPT,
    )
    triples_from_text_system_prompt = load_prompt_override(
        args.triples_prompt_file,
        TRIPLES_FROM_TEXT_SYSTEM_PROMPT,
    )

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    instances = extract_instances(payload)
    instances_num = len(instances)
    logger.info("Extracted %d instances from input JSON", instances_num)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logger.info("Submitting text-generation batch for %d instances...", instances_num)
    text_by_instance_id = generate_texts_from_instances_batch(
        client=client,
        model=args.model,
        text_generation_system_prompt=text_generation_system_prompt,
        instances=instances,
        batch_timeout_seconds=args.batch_timeout_seconds,
    )

    logger.info("Submitting triples-from-text batch for %d instances...", instances_num)
    triples_by_instance_id = triples_from_texts_batch(
        client=client,
        model=args.model,
        triples_from_text_system_prompt=triples_from_text_system_prompt,
        text_by_instance_id=text_by_instance_id,
        batch_timeout_seconds=args.batch_timeout_seconds,
    )

    all_triples: list[Triple] = []
    text_by_instance: list[dict[str, Any]] = []
    triples_by_instance: list[dict[str, Any]] = []

    for i, instance in enumerate(instances):
        instance_id = instance["instance_id"]
        generated_text = text_by_instance_id.get(instance_id, "")
        triples = triples_by_instance_id.get(instance_id, [])

        text_by_instance.append(
            {
                "instance_id": instance_id,
                "text": generated_text,
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

    unique_predicates = list(dict.fromkeys(t.predicate for t in all_triples))

    extraction_output = {
        "input_file": args.input,
        "instances_count": len(instances),
        "triples_count": len(all_triples),
        "unique_predicates": unique_predicates,
        "generated_text_by_instance": text_by_instance,
        "triples_by_instance": triples_by_instance,
        "all_triples": [asdict(t) for t in all_triples],
    }

    Path(args.output).write_text(
        json.dumps(extraction_output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Extraction complete. Results saved to %s", args.output)


def cmd_normalize(args: argparse.Namespace) -> None:
    logger.info("OpenAI base URL: %s", args.base_url)
    logger.info("Model: %s", args.model)

    extraction_output = json.loads(Path(args.input).read_text(encoding="utf-8"))
    equivalence_system_prompt = load_prompt_override(args.equivalence_prompt_file, EQUIVALENCE_SYSTEM_PROMPT)

    all_triples_dict = extraction_output.get("all_triples", [])
    all_triples = [
        Triple(
            subject=t["subject"],
            predicate=t["predicate"],
            object=t["object"],
        )
        for t in all_triples_dict
    ]

    logger.info("Loaded %d triples from %s", len(all_triples), args.input)
    logger.info("Normalizing predicates across all triples...")

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    normalized, groups, comparisons, predicate_pair_comparisons_count = normalize_predicates(
        client=client,
        model=args.model,
        equivalence_system_prompt=equivalence_system_prompt,
        triples=all_triples,
        batch_timeout_seconds=args.batch_timeout_seconds,
    )

    unique_predicates_before = list(dict.fromkeys(t.predicate for t in all_triples))
    unique_predicates_after = list(dict.fromkeys(t.predicate for t in normalized))

    normalization_output = {
        "extraction_source": args.input,
        "unique_predicates_before": unique_predicates_before,
        "unique_predicates_after": unique_predicates_after,
        "predicate_pair_comparisons_count": predicate_pair_comparisons_count,
        "predicate_groups": groups,
        "pairwise_predicate_comparisons": comparisons,
        "normalized_triples": [asdict(t) for t in normalized],
    }

    Path(args.output).write_text(
        json.dumps(normalization_output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info("Normalization complete. Results saved to %s", args.output)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Two-step text-first semantic triple extraction and normalization pipeline."
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    extract_parser = subparsers.add_parser(
        "extract",
        help="Generate natural text per instance, then extract triples from text",
    )
    extract_parser.add_argument("--input", required=True, help="Path to input JSON file")
    extract_parser.add_argument("--output", required=True, help="Path to output extraction results")
    extract_parser.add_argument("--model", required=True, help="Model name served by vLLM/OpenAI-compatible API")
    extract_parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    extract_parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")
    extract_parser.add_argument(
        "--text-prompt-file",
        default=None,
        help="Optional file to override text-generation system prompt",
    )
    extract_parser.add_argument(
        "--triples-prompt-file",
        default=None,
        help="Optional file to override triples-from-text system prompt",
    )
    extract_parser.add_argument(
        "--batch-timeout-seconds",
        type=int,
        default=1800,
        help="Max seconds to wait for each batch completion",
    )
    extract_parser.set_defaults(func=cmd_extract)

    normalize_parser = subparsers.add_parser("normalize", help="Normalize predicates from extraction output")
    normalize_parser.add_argument("--input", required=True, help="Path to extraction output file")
    normalize_parser.add_argument("--output", required=True, help="Path to output normalization results")
    normalize_parser.add_argument("--model", required=True, help="Model name served by vLLM/OpenAI-compatible API")
    normalize_parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    normalize_parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")
    normalize_parser.add_argument(
        "--equivalence-prompt-file",
        default=None,
        help="Optional file to override predicate-equivalence system prompt",
    )
    normalize_parser.add_argument(
        "--batch-timeout-seconds",
        type=int,
        default=1800,
        help="Max seconds to wait for predicate comparison batch completion",
    )
    normalize_parser.set_defaults(func=cmd_normalize)

    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
