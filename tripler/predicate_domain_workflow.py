import json
import logging
from dataclasses import asdict
from typing import Any

from openai import OpenAI

from app import Triple, parse_json_response

DOMAIN_PREDICATE_SYSTEM_PROMPT = (
    "You are building a predicate inventory for a knowledge graph domain. "
    "Return ONLY JSON with schema: {\"predicates\":[\"...\"]}. "
    "Produce a comprehensive list of predicate labels that could plausibly appear in triples for the domain. "
    "Use concise lower_snake_case labels when possible. Avoid duplicates."
)

INSTANCE_TRIPLE_SYSTEM_PROMPT = (
    "You extract semantic triples for a single data instance using a preferred predicate list. "
    "Return ONLY JSON with schema: {\"triples\":[{\"subject\":\"...\",\"predicate\":\"...\",\"object\":\"...\"}]}. "
    "Use predicates from the provided list whenever possible. "
    "If no existing predicate fits a fact, create a new concise predicate label (prefer lower_snake_case)."
)

DOMAIN_PREDICATE_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "domain_predicates",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "predicates": {
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "required": ["predicates"],
        },
    },
}

INSTANCE_TRIPLE_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "domain_constrained_triples",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
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
            "required": ["triples"],
        },
    },
}


def _call_llm_json_once(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_format: dict[str, Any] | None = None,
) -> dict[str, Any]:
    request_payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if response_format is not None:
        request_payload["response_format"] = response_format

    response = client.chat.completions.create(**request_payload)
    content = response.choices[0].message.content or ""
    return parse_json_response(content)


def _dedupe_predicates(predicates: list[str]) -> list[str]:
    return list(dict.fromkeys(p.strip() for p in predicates if str(p).strip()))


def _parse_predicate_list(result: dict[str, Any]) -> list[str]:
    return _dedupe_predicates([str(predicate) for predicate in result.get("predicates", [])])


def generate_initial_predicates(
    client: OpenAI,
    model: str,
    domain: str,
) -> list[str]:
    user_prompt = (
        "Create a comprehensive list of predicates for this problem domain.\n\n"
        f"domain={domain}\n\n"
        "Return JSON only."
    )
    result = _call_llm_json_once(
        client=client,
        model=model,
        system_prompt=DOMAIN_PREDICATE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )
    return _parse_predicate_list(result)


def extract_instance_triples(
    client: OpenAI,
    model: str,
    domain: str,
    allowed_predicates: list[str],
    instance: dict[str, Any],
) -> list[Triple]:
    user_prompt = (
        "Extract semantic triples for this ONE data instance using ONLY the provided predicate list.\n\n"
        f"domain={domain}\n"
        f"allowed_predicates={json.dumps(allowed_predicates, ensure_ascii=False)}\n"
        f"instance_context={json.dumps(instance, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    result = _call_llm_json_once(
        client=client,
        model=model,
        system_prompt=INSTANCE_TRIPLE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    )

    triples: list[Triple] = []
    for triple_entry in result.get("triples", []):
        subject = str(triple_entry.get("subject", "")).strip()
        predicate = str(triple_entry.get("predicate", "")).strip()
        obj = str(triple_entry.get("object", "")).strip()
        if subject and predicate and obj:
            triples.append(Triple(subject=subject, predicate=predicate, object=obj))
    return triples


def run_domain_predicate_workflow(
    *,
    client: OpenAI,
    model: str,
    domain: str,
    instances: list[dict[str, Any]],
    logger: logging.Logger,
) -> dict[str, Any]:
    predicate_inventory = generate_initial_predicates(client=client, model=model, domain=domain)
    logger.info("Initial predicate inventory size: %d", len(predicate_inventory))

    initial_predicates = list(predicate_inventory)
    predicate_additions: list[dict[str, Any]] = []
    failed_instances: list[dict[str, Any]] = []
    all_triples: list[Triple] = []
    triples_by_instance: list[dict[str, Any]] = []

    for index, instance in enumerate(instances, start=1):
        instance_id = int(instance.get("instance_id", index - 1))
        logger.info("Processing instance %d/%d", index, len(instances))

        try:
            candidate_triples = extract_instance_triples(
                client=client,
                model=model,
                domain=domain,
                allowed_predicates=predicate_inventory,
                instance=instance,
            )
        except Exception as exc:
            logger.warning("Instance %s failed: %s", instance_id, exc)
            failed_instances.append({"instance_id": instance_id, "error": str(exc)})
            candidate_triples = []

        existing_predicates = set(predicate_inventory)
        newly_observed_predicates = _dedupe_predicates(
            [t.predicate for t in candidate_triples if t.predicate not in existing_predicates]
        )
        if newly_observed_predicates:
            predicate_inventory.extend(newly_observed_predicates)
            predicate_additions.append(
                {
                    "instance_id": instance_id,
                    "added_predicates": newly_observed_predicates,
                }
            )
            logger.info(
                "Added %d new predicates from instance %s",
                len(newly_observed_predicates),
                instance_id,
            )

        triples_by_instance.append(
            {
                "instance_id": instance_id,
                "triples": [asdict(t) for t in candidate_triples],
            }
        )
        all_triples.extend(candidate_triples)

    unique_predicates = list(dict.fromkeys(predicate_inventory))
    return {
        "problem_domain": domain,
        "instances_count": len(instances),
        "initial_predicates": initial_predicates,
        "unique_predicates": unique_predicates,
        "predicate_additions": predicate_additions,
        "failed_instances": failed_instances,
        "triples_by_instance": triples_by_instance,
        "all_triples": [asdict(t) for t in all_triples],
    }