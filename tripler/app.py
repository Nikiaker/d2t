import argparse
import json
import itertools
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import logging
from json import JSONDecodeError

from openai import OpenAI

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = (
    "You convert one structured data instance into semantic triples. "
    "Return ONLY JSON with this exact schema: "
    '{"triples":[{"subject":"...","predicate":"...","object":"..."}]}. '
    "Rules: use concise noun phrases for subject/object, use short predicate labels, "
    "avoid duplicates, and keep predicates in lower_snake_case when possible."
)

EQUIVALENCE_SYSTEM_PROMPT = (
    "You decide if two predicates are semantically equivalent in meaning. "
    "Return ONLY JSON with schema: "
    '{"equivalent": true|false, "confidence": 0.0-1.0, "reason": "..."}. '
    "Be strict: equivalent only if they can be safely merged in a knowledge graph."
)


@dataclass
class Triple:
    subject: str
    predicate: str
    object: str


class UnionFind:
    def __init__(self, items: list[str]) -> None:
        self.parent = {item: item for item in items}

    def find(self, x: str) -> str:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def load_prompt_override(path: str | None, default_prompt: str) -> str:
    if not path:
        return default_prompt
    return Path(path).read_text(encoding="utf-8")


def parse_json_response(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("{"):
        return json.loads(stripped)

    # Recover from models that wrap JSON in markdown fences.
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))

    # Fallback: first JSON object-like block.
    block = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if block:
        return json.loads(block.group(0))

    raise ValueError("Could not parse JSON from model response")


def extract_instances(payload: Any) -> list[dict[str, Any]]:
    instances: list[dict[str, Any]] = []

    if isinstance(payload, dict) and isinstance(payload.get("forecasts"), list):
        for forecast in payload["forecasts"]:
            city = (forecast.get("city") or {}).get("name")
            for idx, item in enumerate(forecast.get("list") or []):
                instances.append(
                    {
                        "instance_id": len(instances),
                        "city": city,
                        "position_in_city": idx,
                        "data": item,
                    }
                )
        return instances

    if isinstance(payload, dict) and isinstance(payload.get("list"), list):
        for idx, item in enumerate(payload["list"]):
            instances.append({"instance_id": idx, "data": item})
        return instances

    if isinstance(payload, list):
        for idx, item in enumerate(payload):
            instances.append({"instance_id": idx, "data": item})
        return instances

    raise ValueError(
        "Unsupported JSON structure. Expected one of: "
        "{forecasts:[{list:[...]}]}, {list:[...]}, or [...]."
    )


def call_llm_json(client: OpenAI, model: str, system_prompt: str, user_prompt: str) -> dict[str, Any]:
    logger.debug(f"System prompt:\n{system_prompt}\nUser prompt:\n{user_prompt}")

    max_retries = 3
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for attempt in range(max_retries + 1):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": False}
            }
        )
        content = response.choices[0].message.content or ""
        logger.debug(f"Raw model response (attempt {attempt + 1}/{max_retries + 1}):\n{content}")

        try:
            return parse_json_response(content)
        except (JSONDecodeError, ValueError) as exc:
            if attempt >= max_retries:
                logger.warning(
                    "Failed to parse JSON after %d retries. Last error: %s",
                    max_retries,
                    exc,
                )
                raise

            logger.warning(
                "Invalid JSON from model (attempt %d/%d). Retrying with format correction instruction. Error: %s",
                attempt + 1,
                max_retries + 1,
                exc,
            )
            correction_prompt = (
                "Your previous response was not valid JSON for the required schema. "
                "Return ONLY valid JSON. Do not include markdown, explanations, or trailing text. "
                f"Parser error: {exc}"
            )
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "user", "content": correction_prompt})

    raise RuntimeError("Unreachable retry state")


def triples_from_instance(
    client: OpenAI,
    model: str,
    extraction_system_prompt: str,
    instance: dict[str, Any],
) -> list[Triple]:
    user_prompt = (
        "Generate semantic triples for this ONE data instance.\n\n"
        f"instance_context={json.dumps(instance, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )
    try:
        result = call_llm_json(client, model, extraction_system_prompt, user_prompt)
    except Exception as exc:
        logger.warning(
            "Skipping instance %s after JSON-format retries failed: %s",
            instance.get("instance_id"),
            exc,
        )
        return []

    raw_triples = result.get("triples", [])

    triples: list[Triple] = []
    for t in raw_triples:
        subject = str(t.get("subject", "")).strip()
        predicate = str(t.get("predicate", "")).strip()
        obj = str(t.get("object", "")).strip()
        if subject and predicate and obj:
            triples.append(Triple(subject=subject, predicate=predicate, object=obj))
    
    logger.info(f"Extracted {len(triples)} triples from instance {instance['instance_id']}")
    return triples


def predicates_equivalent(
    client: OpenAI,
    model: str,
    equivalence_system_prompt: str,
    p1: str,
    p2: str,
) -> tuple[bool, float, str]:
    user_prompt = (
        "Decide whether these predicates are equivalent in meaning.\n"
        f"predicate_a={p1}\n"
        f"predicate_b={p2}\n"
        "Use strict semantic equivalence (not merely related)."
    )

    try:
        result = call_llm_json(client, model, equivalence_system_prompt, user_prompt)
    except Exception as exc:
        logger.warning(
            "Skipping predicate comparison for '%s' vs '%s' after JSON-format retries failed: %s",
            p1,
            p2,
            exc,
        )
        return False, 0.0, "skipped_due_to_invalid_json"

    equivalent = bool(result.get("equivalent", False))
    confidence = float(result.get("confidence", 0.0))
    reason = str(result.get("reason", "")).strip()
    return equivalent, confidence, reason


def normalize_predicates(
    client: OpenAI,
    model: str,
    equivalence_system_prompt: str,
    triples: list[Triple],
) -> tuple[list[Triple], dict[str, list[str]], list[dict[str, Any]], int]:
    predicates = list(dict.fromkeys(t.predicate for t in triples))
    uf = UnionFind(predicates)
    comparisons: list[dict[str, Any]] = []
    total_pairs = len(predicates) * (len(predicates) - 1) // 2

    logger.info(
        "Unique predicates: %d | Pairwise comparisons (nC2): %d",
        len(predicates),
        total_pairs,
    )

    current_num = 0

    for p1, p2 in itertools.combinations(predicates, 2):
        logger.debug(f"Comparing predicates: '{p1}' vs '{p2}'")
        equivalent, confidence, reason = predicates_equivalent(
            client=client,
            model=model,
            equivalence_system_prompt=equivalence_system_prompt,
            p1=p1,
            p2=p2,
        )
        comparisons.append(
            {
                "predicate_a": p1,
                "predicate_b": p2,
                "equivalent": equivalent,
                "confidence": confidence,
                "reason": reason,
            }
        )
        if equivalent:
            logger.debug(f"Predicates '{p1}' and '{p2}' are equivalent (confidence: {confidence:.2f})")
            uf.union(p1, p2)
        
        current_num += 1
        logger.info(f"Completed {current_num}/{total_pairs} comparisons")

    groups: dict[str, list[str]] = {}
    for p in predicates:
        root = uf.find(p)
        groups.setdefault(root, []).append(p)

    canonical_by_predicate: dict[str, str] = {}
    for _, group in groups.items():
        canonical = group[0]  # requirement: choose first element in each group
        for p in group:
            canonical_by_predicate[p] = canonical

    normalized = [
        Triple(subject=t.subject, predicate=canonical_by_predicate[t.predicate], object=t.object)
        for t in triples
    ]

    return normalized, groups, comparisons, total_pairs


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Generate semantic triples from JSON and normalize equivalent predicates via LLM."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON file")
    parser.add_argument("--output", required=True, help="Path to output JSON file")
    parser.add_argument("--model", required=True, help="Model name served by vLLM/OpenAI-compatible API")
    parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")
    parser.add_argument(
        "--extract-prompt-file",
        default=None,
        help="Optional file to override extraction system prompt",
    )
    parser.add_argument(
        "--equivalence-prompt-file",
        default=None,
        help="Optional file to override predicate-equivalence system prompt",
    )
    args = parser.parse_args()

    logger.info(f"OpenAI base URL: {args.base_url}")
    logger.info(f"Model: {args.model}")

    extraction_system_prompt = load_prompt_override(args.extract_prompt_file, EXTRACTION_SYSTEM_PROMPT)
    equivalence_system_prompt = load_prompt_override(args.equivalence_prompt_file, EQUIVALENCE_SYSTEM_PROMPT)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    instances = extract_instances(payload)
    instances_num = len(instances)

    logger.info(f"Extracted {instances_num} instances from input JSON")

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    all_triples: list[Triple] = []
    triples_by_instance: list[dict[str, Any]] = []

    for i, instance in enumerate(instances):
        triples = triples_from_instance(
            client=client,
            model=args.model,
            extraction_system_prompt=extraction_system_prompt,
            instance=instance,
        )
        all_triples.extend(triples)
        triples_by_instance.append(
            {
                "instance_id": instance["instance_id"],
                "triples": [asdict(t) for t in triples],
            }
        )
        logger.info(f"Processed instance {i + 1}/{instances_num}")

    logger.info("Normalizing predicates across all triples...")
    normalized, groups, comparisons, predicate_pair_comparisons_count = normalize_predicates(
        client=client,
        model=args.model,
        equivalence_system_prompt=equivalence_system_prompt,
        triples=all_triples,
    )

    output_payload = {
        "input_file": args.input,
        "instances_count": len(instances),
        "triples_count": len(all_triples),
        "unique_predicates_before": list(dict.fromkeys(t.predicate for t in all_triples)),
        "predicate_pair_comparisons_count": predicate_pair_comparisons_count,
        "predicate_groups": groups,
        "pairwise_predicate_comparisons": comparisons,
        "triples_by_instance": triples_by_instance,
        "normalized_triples": [asdict(t) for t in normalized],
    }

    Path(args.output).write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
