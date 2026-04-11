import json
import logging
from dataclasses import asdict
from typing import Any

from openai import OpenAI

from app import Triple, call_llm_json

DOMAIN_PREDICATE_SYSTEM_PROMPT = (
    "You are building a predicate inventory for a knowledge graph domain. "
    "Return ONLY JSON with schema: {\"predicates\":[\"...\"]}. "
    "Produce a comprehensive list of predicate labels that could plausibly appear in triples for the domain. "
    "Use concise lower_snake_case labels when possible. Avoid duplicates."
)

INSTANCE_TRIPLE_SYSTEM_PROMPT = (
    "You extract semantic triples for a single data instance using ONLY the provided predicate list. "
    "Return ONLY JSON with schema: {\"triples\":[{\"subject\":\"...\",\"predicate\":\"...\",\"object\":\"...\"}],"
    "\"needs_new_predicates\": true|false, \"missing_predicates\":[\"...\"]}. "
    "If no provided predicate fits a fact in the instance, set needs_new_predicates to true and list the missing predicate labels. "
    "Do not invent predicates outside the provided list unless you are explicitly reporting them as missing_predicates."
)

DOMAIN_PREDICATE_EXPANSION_SYSTEM_PROMPT = (
    "You expand a predicate inventory for a knowledge graph domain. "
    "Return ONLY JSON with schema: {\"predicates\":[\"...\"]}. "
    "Given the domain, the current predicate list, and the missing predicate requests, return only new predicate labels that should be added. "
    "Avoid duplicates and keep labels concise and lower_snake_case when possible."
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
                "needs_new_predicates": {"type": "boolean"},
                "missing_predicates": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["triples", "needs_new_predicates", "missing_predicates"],
        },
    },
}


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
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=DOMAIN_PREDICATE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=DOMAIN_PREDICATE_RESPONSE_FORMAT,
    )
    return _parse_predicate_list(result)


def extract_instance_triples(
    client: OpenAI,
    model: str,
    domain: str,
    allowed_predicates: list[str],
    instance: dict[str, Any],
) -> tuple[list[Triple], bool, list[str]]:
    user_prompt = (
        "Extract semantic triples for this ONE data instance using ONLY the provided predicate list.\n\n"
        f"domain={domain}\n"
        f"allowed_predicates={json.dumps(allowed_predicates, ensure_ascii=False)}\n"
        f"instance_context={json.dumps(instance, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=INSTANCE_TRIPLE_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=INSTANCE_TRIPLE_RESPONSE_FORMAT,
    )

    allowed_set = set(allowed_predicates)
    triples: list[Triple] = []
    used_predicates: list[str] = []
    for triple_entry in result.get("triples", []):
        subject = str(triple_entry.get("subject", "")).strip()
        predicate = str(triple_entry.get("predicate", "")).strip()
        obj = str(triple_entry.get("object", "")).strip()
        if subject and predicate and obj:
            triples.append(Triple(subject=subject, predicate=predicate, object=obj))
            used_predicates.append(predicate)

    missing_predicates = _dedupe_predicates(
        [str(predicate) for predicate in result.get("missing_predicates", [])]
        + [predicate for predicate in used_predicates if predicate not in allowed_set]
    )
    needs_new_predicates = bool(result.get("needs_new_predicates", False)) or bool(missing_predicates)

    return triples, needs_new_predicates, missing_predicates


def expand_predicate_inventory(
    client: OpenAI,
    model: str,
    domain: str,
    allowed_predicates: list[str],
    missing_predicates: list[str],
) -> list[str]:
    if not missing_predicates:
        return []

    user_prompt = (
        "Add any needed predicates for this domain.\n\n"
        f"domain={domain}\n"
        f"current_predicates={json.dumps(allowed_predicates, ensure_ascii=False)}\n"
        f"missing_predicates={json.dumps(missing_predicates, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    result = call_llm_json(
        client=client,
        model=model,
        system_prompt=DOMAIN_PREDICATE_EXPANSION_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        response_format=DOMAIN_PREDICATE_RESPONSE_FORMAT,
    )
    return _parse_predicate_list(result)


def run_domain_predicate_workflow(
    *,
    client: OpenAI,
    model: str,
    domain: str,
    instances: list[dict[str, Any]],
    max_expansion_rounds: int,
    logger: logging.Logger,
) -> dict[str, Any]:
    predicate_inventory = generate_initial_predicates(client=client, model=model, domain=domain)
    logger.info("Initial predicate inventory size: %d", len(predicate_inventory))

    initial_predicates = list(predicate_inventory)
    predicate_additions: list[dict[str, Any]] = []
    incomplete_instances: list[int] = []
    all_triples: list[Triple] = []
    triples_by_instance: list[dict[str, Any]] = []

    for index, instance in enumerate(instances, start=1):
        instance_id = int(instance.get("instance_id", index - 1))
        logger.info("Processing instance %d/%d", index, len(instances))

        candidate_triples: list[Triple] = []
        completed = False

        for round_num in range(1, max_expansion_rounds + 1):
            candidate_triples, needs_new_predicates, missing_predicates = extract_instance_triples(
                client=client,
                model=model,
                domain=domain,
                allowed_predicates=predicate_inventory,
                instance=instance,
            )

            if not needs_new_predicates:
                completed = True
                break

            logger.info(
                "Instance %s requested predicate expansion in round %d: %s",
                instance_id,
                round_num,
                ", ".join(missing_predicates) if missing_predicates else "<unspecified>",
            )

            new_predicates = expand_predicate_inventory(
                client=client,
                model=model,
                domain=domain,
                allowed_predicates=predicate_inventory,
                missing_predicates=missing_predicates,
            )
            new_predicates = [predicate for predicate in new_predicates if predicate not in predicate_inventory]

            if not new_predicates:
                logger.warning(
                    "No new predicates were added for instance %s; moving to the next instance",
                    instance_id,
                )
                break

            predicate_inventory.extend(new_predicates)
            predicate_additions.append(
                {
                    "instance_id": instance_id,
                    "round": round_num,
                    "added_predicates": new_predicates,
                    "requested_missing_predicates": missing_predicates,
                }
            )

        if not completed:
            incomplete_instances.append(instance_id)
            candidate_triples = []

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
        "incomplete_instances": incomplete_instances,
        "triples_by_instance": triples_by_instance,
        "all_triples": [asdict(t) for t in all_triples],
    }