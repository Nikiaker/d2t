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

RULE_CREATION_SYSTEM_PROMPT = (
    "You design extraction rules for a domain. "
    "Return ONLY JSON with schema: "
    "{\"predicates\":[\"...\"],"
    "\"example_triples\":[{\"subject\":\"...\",\"predicate\":\"...\",\"object\":\"...\"}],"
    "\"example_text\":\"...\","
    "\"guidelines\":[\"...\"]}. "
    "Rules: include precise and reusable predicates, provide concrete example triples with strict formatting, "
    "provide an example text matching those triples, and give practical transformation guidelines."
)

RULE_FEASIBILITY_SYSTEM_PROMPT = (
    "You evaluate whether given extraction rules are sufficient to extract triples from a text. "
    "Return ONLY JSON with schema: "
    "{\"possible\":true|false,\"reason\":\"...\",\"rule_gaps\":[\"...\"]}."
)

RULE_REVISION_SYSTEM_PROMPT = (
    "You revise extraction rules so triples can be produced from a text. "
    "Return ONLY JSON with schema: "
    "{\"predicates\":[\"...\"],"
    "\"example_triples\":[{\"subject\":\"...\",\"predicate\":\"...\",\"object\":\"...\"}],"
    "\"example_text\":\"...\","
    "\"guidelines\":[\"...\"]}. "
    "Keep existing high-quality rules, but add or adjust what is necessary to cover the failing case."
)

TRIPLES_FROM_TEXT_WITH_RULES_SYSTEM_PROMPT = (
    "You extract semantic triples from natural language text using provided rules. "
    "Return ONLY JSON with this exact schema: "
    '{"triples":[{"subject":"...","predicate":"...","object":"..."}]}. '
    "Follow rule guidelines and mimic the formatting style from example triples. "
    "Prefer predicates from the rule predicate list whenever possible."
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

RULES_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "domain_rules",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "predicates": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "example_triples": {
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
                "example_text": {"type": "string"},
                "guidelines": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["predicates", "example_triples", "example_text", "guidelines"],
        },
    },
}

RULE_FEASIBILITY_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "rule_feasibility",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "possible": {"type": "boolean"},
                "reason": {"type": "string"},
                "rule_gaps": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["possible", "reason", "rule_gaps"],
        },
    },
}


def _dedupe_strings(values: list[str]) -> list[str]:
    return list(dict.fromkeys(v.strip() for v in values if str(v).strip()))


def _normalize_rules(raw: dict[str, Any], fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    fallback = fallback or {
        "predicates": [],
        "example_triples": [],
        "example_text": "",
        "guidelines": [],
    }

    predicates = _dedupe_strings([str(v) for v in raw.get("predicates", [])])
    if not predicates:
        predicates = list(fallback.get("predicates", []))

    example_triples: list[dict[str, str]] = []
    for t in raw.get("example_triples", []):
        subject = str(t.get("subject", "")).strip()
        predicate = str(t.get("predicate", "")).strip()
        obj = str(t.get("object", "")).strip()
        if subject and predicate and obj:
            example_triples.append(
                {
                    "subject": subject,
                    "predicate": predicate,
                    "object": obj,
                }
            )
    if not example_triples:
        example_triples = list(fallback.get("example_triples", []))

    example_text = str(raw.get("example_text", "")).strip()
    if not example_text:
        example_text = str(fallback.get("example_text", ""))

    guidelines = _dedupe_strings([str(v) for v in raw.get("guidelines", [])])
    if not guidelines:
        guidelines = list(fallback.get("guidelines", []))

    return {
        "predicates": predicates,
        "example_triples": example_triples,
        "example_text": example_text,
        "guidelines": guidelines,
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


def generate_initial_rules(client: OpenAI, model: str, domain: str) -> dict[str, Any]:
    user_prompt = (
        "Create extraction rules for the domain.\n\n"
        f"domain={domain}\n\n"
        "Return JSON only."
    )
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=RULE_CREATION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=RULES_RESPONSE_FORMAT,
    )
    return _normalize_rules(result)


def assess_rules_on_text(
    client: OpenAI,
    model: str,
    rules: dict[str, Any],
    text: str,
) -> dict[str, Any]:
    user_prompt = (
        "Evaluate if these rules are sufficient to extract triples from the text.\n\n"
        f"rules={json.dumps(rules, ensure_ascii=False)}\n"
        f"text={json.dumps(text, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=RULE_FEASIBILITY_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=RULE_FEASIBILITY_RESPONSE_FORMAT,
    )
    return {
        "possible": bool(result.get("possible", False)),
        "reason": str(result.get("reason", "")).strip(),
        "rule_gaps": _dedupe_strings([str(v) for v in result.get("rule_gaps", [])]),
    }


def revise_rules(
    client: OpenAI,
    model: str,
    domain: str,
    current_rules: dict[str, Any],
    text: str,
    reason: str,
    rule_gaps: list[str],
) -> dict[str, Any]:
    user_prompt = (
        "Revise these rules so triples can be generated for the failing text.\n\n"
        f"domain={domain}\n"
        f"current_rules={json.dumps(current_rules, ensure_ascii=False)}\n"
        f"failing_text={json.dumps(text, ensure_ascii=False)}\n"
        f"failure_reason={reason}\n"
        f"rule_gaps={json.dumps(rule_gaps, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=RULE_REVISION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=RULES_RESPONSE_FORMAT,
    )
    return _normalize_rules(result, fallback=current_rules)


def build_triples_from_text_with_rules_batch_jsonl(
    model: str,
    rules: dict[str, Any],
    text_by_instance_id: dict[int, str],
) -> str:
    lines: list[str] = []

    for instance_id, text in text_by_instance_id.items():
        if not text:
            continue

        user_prompt = (
            "Extract semantic triples from this text using the provided rules.\n\n"
            f"rules={json.dumps(rules, ensure_ascii=False)}\n"
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
                    {"role": "system", "content": TRIPLES_FROM_TEXT_WITH_RULES_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": EXTRACTION_RESPONSE_FORMAT,
            },
        }
        lines.append(json.dumps(request_payload, ensure_ascii=False))

    return "\n".join(lines) + "\n"


def parse_triples_batch_output(output_text: str) -> dict[int, list[Triple]]:
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
            logger.warning("Skipping triples batch item with invalid custom_id: %s", custom_id)
            continue

        response_obj = entry.get("response")
        if not isinstance(response_obj, dict):
            logger.warning("Missing response for instance %s", instance_id)
            triples_by_instance_id[instance_id] = []
            continue

        body = response_obj.get("body") or {}
        choices = body.get("choices") or []
        if not choices:
            logger.warning("No choices for instance %s", instance_id)
            triples_by_instance_id[instance_id] = []
            continue

        content = str(((choices[0] or {}).get("message") or {}).get("content") or "")
        try:
            result = parse_json_response(content)
        except (JSONDecodeError, ValueError) as exc:
            logger.warning("Invalid JSON for instance %s: %s", instance_id, exc)
            triples_by_instance_id[instance_id] = []
            continue

        triples: list[Triple] = []
        for triple_entry in result.get("triples", []):
            subject = str(triple_entry.get("subject", "")).strip()
            predicate = str(triple_entry.get("predicate", "")).strip()
            obj = str(triple_entry.get("object", "")).strip()
            if subject and predicate and obj:
                triples.append(Triple(subject=subject, predicate=predicate, object=obj))

        triples_by_instance_id[instance_id] = triples

    return triples_by_instance_id


def triples_from_texts_with_rules_batch(
    client: OpenAI,
    model: str,
    rules: dict[str, Any],
    text_by_instance_id: dict[int, str],
    batch_timeout_seconds: int,
) -> dict[int, list[Triple]]:
    if not text_by_instance_id:
        return {}

    batch_jsonl = build_triples_from_text_with_rules_batch_jsonl(
        model=model,
        rules=rules,
        text_by_instance_id=text_by_instance_id,
    )
    if not batch_jsonl.strip():
        return {}

    batch_jsonl_bytes = batch_jsonl.encode("utf-8")
    logger.info("Rules+text triples batch file size: %d bytes", len(batch_jsonl_bytes))

    input_file = client.files.create(
        file=("rules_text_triples_batch.jsonl", io.BytesIO(batch_jsonl_bytes)),
        purpose="batch",
    )

    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("Started rules+text triples batch: %s", batch.id)

    final_batch = wait_for_batch_completion(
        client=client,
        batch_id=batch.id,
        timeout_seconds=batch_timeout_seconds,
    )
    if getattr(final_batch, "status", None) != "completed":
        raise RuntimeError(f"Rules+text triples batch {batch.id} failed: {final_batch.status}")

    output_file_id = getattr(final_batch, "output_file_id", None)
    if not output_file_id:
        raise RuntimeError(f"Rules+text triples batch {batch.id} has no output_file_id")

    output_text = read_openai_file_text(client=client, file_id=output_file_id)
    return parse_triples_batch_output(output_text)


def cmd_extract(args: argparse.Namespace) -> None:
    logger.info("OpenAI base URL: %s", args.base_url)
    logger.info("Model: %s", args.model)
    logger.info("Domain: %s", args.domain)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    instances = extract_instances(payload)
    instances_num = len(instances)
    logger.info("Extracted %d instances from input JSON", instances_num)

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logger.info("Generating initial domain rules...")
    rules_initial = generate_initial_rules(client=client, model=args.model, domain=args.domain)
    rules_current = json.loads(json.dumps(rules_initial, ensure_ascii=False))

    logger.info("Generating text for all instances...")
    text_by_instance_id = generate_texts_from_instances_batch(
        client=client,
        model=args.model,
        text_generation_system_prompt=TEXT_GENERATION_SYSTEM_PROMPT,
        instances=instances,
        batch_timeout_seconds=args.batch_timeout_seconds,
    )

    rules_validation_rounds: list[dict[str, Any]] = []
    rules_revision_history: list[dict[str, Any]] = []
    rules_validated_all_texts = False

    for round_num in range(1, args.max_rules_revision_rounds + 1):
        failing: dict[str, Any] | None = None
        checked = 0

        for instance in instances:
            instance_id = int(instance["instance_id"])
            text = text_by_instance_id.get(instance_id, "")
            if not text:
                checked += 1
                continue

            assessment = assess_rules_on_text(
                client=client,
                model=args.model,
                rules=rules_current,
                text=text,
            )
            checked += 1

            if not assessment["possible"]:
                failing = {
                    "instance_id": instance_id,
                    "text": text,
                    "reason": assessment["reason"],
                    "rule_gaps": assessment["rule_gaps"],
                }
                break

        round_log = {
            "round": round_num,
            "checked_instances": checked,
            "failed_instance_id": None if failing is None else failing["instance_id"],
        }
        rules_validation_rounds.append(round_log)

        if failing is None:
            rules_validated_all_texts = True
            logger.info("Rules validated against all texts in round %d", round_num)
            break

        logger.info(
            "Rules failed on instance %s in round %d; revising rules",
            failing["instance_id"],
            round_num,
        )
        rules_current = revise_rules(
            client=client,
            model=args.model,
            domain=args.domain,
            current_rules=rules_current,
            text=failing["text"],
            reason=failing["reason"],
            rule_gaps=failing["rule_gaps"],
        )
        rules_revision_history.append(
            {
                "round": round_num,
                "failed_instance_id": failing["instance_id"],
                "reason": failing["reason"],
                "rule_gaps": failing["rule_gaps"],
            }
        )

    if not rules_validated_all_texts:
        logger.warning(
            "Rules were not validated on all texts within %d revision rounds",
            args.max_rules_revision_rounds,
        )

    logger.info("Submitting final rules-based triples batch...")
    triples_by_instance_id = triples_from_texts_with_rules_batch(
        client=client,
        model=args.model,
        rules=rules_current,
        text_by_instance_id=text_by_instance_id,
        batch_timeout_seconds=args.batch_timeout_seconds,
    )

    all_triples: list[Triple] = []
    triples_by_instance: list[dict[str, Any]] = []
    generated_text_by_instance: list[dict[str, Any]] = []

    for i, instance in enumerate(instances):
        instance_id = int(instance["instance_id"])
        text = text_by_instance_id.get(instance_id, "")
        triples = triples_by_instance_id.get(instance_id, [])

        generated_text_by_instance.append(
            {
                "instance_id": instance_id,
                "text": text,
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

    output = {
        "input_file": args.input,
        "problem_domain": args.domain,
        "instances_count": len(instances),
        "rules_initial": rules_initial,
        "rules_final": rules_current,
        "rules_validated_all_texts": rules_validated_all_texts,
        "rules_validation_rounds": rules_validation_rounds,
        "rules_revision_history": rules_revision_history,
        "triples_count": len(all_triples),
        "unique_predicates": unique_predicates,
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
        description="Rules-driven text-to-triples pipeline with iterative rule refinement."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output extraction results")
    parser.add_argument("--domain", required=True, help="Problem domain, e.g. weather forecast")
    parser.add_argument("--model", required=True, help="Model name served by vLLM/OpenAI-compatible API")
    parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")
    parser.add_argument(
        "--batch-timeout-seconds",
        type=int,
        default=1800,
        help="Max seconds to wait for each batch completion",
    )
    parser.add_argument(
        "--max-rules-revision-rounds",
        type=int,
        default=20,
        help="Max number of times rules can be revised after failing texts",
    )

    args = parser.parse_args()
    cmd_extract(args)


if __name__ == "__main__":
    main()
