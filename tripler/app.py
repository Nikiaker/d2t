import argparse
import json
import itertools
import re
import io
import time
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
    "avoid duplicates, and keep predicates in lower_snake_case when possible. "
    "If the instance contains many time points (e.g., a full forecast), extract only the most important high-level aspects "
    "(location/context, key trends, extremes, notable conditions) rather than point-by-point details."
)

EQUIVALENCE_SYSTEM_PROMPT = (
    "You decide if two predicates are semantically equivalent in meaning. "
    "Return ONLY JSON with schema: "
    '{"equivalent": true|false, "confidence": 0.0-1.0, "reason": "..."}. '
    "Be strict: equivalent only if they can be safely merged in a knowledge graph."
)

EXTRACTION_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "triple_extraction",
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
                }
            },
            "required": ["triples"],
        },
    },
}

EQUIVALENCE_RESPONSE_FORMAT: dict[str, Any] = {
    "type": "json_schema",
    "json_schema": {
        "name": "predicate_equivalence",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "equivalent": {"type": "boolean"},
                "confidence": {"type": "number"},
                "reason": {"type": "string"},
            },
            "required": ["equivalent", "confidence", "reason"],
        },
    },
}


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
        for idx, forecast in enumerate(payload["forecasts"]):
            city = (forecast.get("city") or {}).get("name")
            instances.append(
                {
                    "instance_id": idx,
                    "city": city,
                    "data": forecast,
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


def call_llm_json(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_format: dict[str, Any] | None = None,
) -> dict[str, Any]:
    logger.debug(f"System prompt:\n{system_prompt}\nUser prompt:\n{user_prompt}")

    max_retries = 3
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    for attempt in range(max_retries + 1):
        request_payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "extra_body": {
                "chat_template_kwargs": {"enable_thinking": False}
            },
        }
        if response_format is not None:
            request_payload["response_format"] = response_format

        response = client.chat.completions.create(**request_payload)
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
        result = call_llm_json(
            client,
            model,
            extraction_system_prompt,
            user_prompt,
            response_format=EXTRACTION_RESPONSE_FORMAT,
        )
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


def build_extraction_batch_jsonl(
    model: str,
    extraction_system_prompt: str,
    instances: list[dict[str, Any]],
) -> str:
    lines: list[str] = []
    for instance in instances:
        instance_id = instance.get("instance_id")
        user_prompt = (
            "Generate semantic triples for this ONE data instance.\n\n"
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
                    {"role": "system", "content": extraction_system_prompt},
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


def wait_for_batch_completion(
    client: OpenAI,
    batch_id: str,
    timeout_seconds: int,
    poll_interval_seconds: int = 3,
) -> Any:
    start = time.time()
    terminal_states = {"completed", "failed", "cancelled", "expired"}

    while True:
        batch = client.batches.retrieve(batch_id)
        status = getattr(batch, "status", "unknown")
        logger.info("Batch %s status: %s", batch_id, status)

        if status in terminal_states:
            return batch

        elapsed = time.time() - start
        if elapsed > timeout_seconds:
            raise TimeoutError(
                f"Timed out waiting for batch {batch_id} after {timeout_seconds} seconds"
            )

        time.sleep(poll_interval_seconds)


def parse_batch_output(
    output_text: str,
) -> dict[int, list[Triple]]:
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
            logger.warning("Skipping batch item with invalid custom_id: %s", custom_id)
            continue

        response_obj = entry.get("response")
        if not isinstance(response_obj, dict):
            logger.warning("Missing response for instance %s", instance_id)
            triples_by_instance_id[instance_id] = []
            continue

        body = response_obj.get("body") or {}
        choices = body.get("choices") or []
        if not choices:
            logger.warning("No choices returned for instance %s", instance_id)
            triples_by_instance_id[instance_id] = []
            continue

        content = str(((choices[0] or {}).get("message") or {}).get("content") or "")
        try:
            result = parse_json_response(content)
        except (JSONDecodeError, ValueError) as exc:
            logger.warning(
                "Invalid JSON in batch output for instance %s: %s",
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


def read_openai_file_text(client: OpenAI, file_id: str) -> str:
    file_response = client.files.content(file_id)
    text_attr = getattr(file_response, "text", None)
    if isinstance(text_attr, str):
        return text_attr
    if callable(text_attr):
        return text_attr()

    content_attr = getattr(file_response, "content", b"")
    if callable(content_attr):
        content_attr = content_attr()
    if isinstance(content_attr, bytes):
        return content_attr.decode("utf-8")
    return str(content_attr)


def triples_from_instances_batch(
    client: OpenAI,
    model: str,
    extraction_system_prompt: str,
    instances: list[dict[str, Any]],
    batch_timeout_seconds: int,
) -> dict[int, list[Triple]]:
    if not instances:
        return {}

    batch_jsonl = build_extraction_batch_jsonl(
        model=model,
        extraction_system_prompt=extraction_system_prompt,
        instances=instances,
    )
    batch_jsonl_bytes = batch_jsonl.encode("utf-8")
    logger.info("Extraction batch file size: %d bytes", len(batch_jsonl_bytes))

    input_file = client.files.create(
        file=("triples_extraction_batch.jsonl", io.BytesIO(batch_jsonl_bytes)),
        purpose="batch",
    )

    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("Started extraction batch: %s", batch.id)

    final_batch = wait_for_batch_completion(
        client=client,
        batch_id=batch.id,
        timeout_seconds=batch_timeout_seconds,
    )

    if getattr(final_batch, "status", None) != "completed":
        raise RuntimeError(f"Batch {batch.id} did not complete successfully: {final_batch.status}")

    output_file_id = getattr(final_batch, "output_file_id", None)
    if not output_file_id:
        raise RuntimeError(f"Batch {batch.id} completed but has no output_file_id")

    output_text = read_openai_file_text(client=client, file_id=output_file_id)

    return parse_batch_output(output_text)


def build_equivalence_batch_jsonl(
    model: str,
    equivalence_system_prompt: str,
    predicate_pairs: list[tuple[str, str]],
) -> tuple[str, dict[str, tuple[str, str]]]:
    lines: list[str] = []
    pair_by_custom_id: dict[str, tuple[str, str]] = {}

    for index, (p1, p2) in enumerate(predicate_pairs):
        custom_id = f"predicate-pair-{index}"
        pair_by_custom_id[custom_id] = (p1, p2)

        user_prompt = (
            "Decide whether these predicates are equivalent in meaning.\n"
            f"predicate_a={p1}\n"
            f"predicate_b={p2}\n"
            "Use strict semantic equivalence (not merely related)."
        )
        request_payload = {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": model,
                "messages": [
                    {"role": "system", "content": equivalence_system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "response_format": EQUIVALENCE_RESPONSE_FORMAT,
                "extra_body": {
                    "chat_template_kwargs": {"enable_thinking": False}
                },
            },
        }
        lines.append(json.dumps(request_payload, ensure_ascii=False))

    return "\n".join(lines) + "\n", pair_by_custom_id


def parse_equivalence_batch_output(
    output_text: str,
    pair_by_custom_id: dict[str, tuple[str, str]],
) -> dict[str, dict[str, Any]]:
    result_by_custom_id: dict[str, dict[str, Any]] = {}

    for raw_line in output_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        entry = json.loads(line)
        custom_id = str(entry.get("custom_id", ""))
        if custom_id not in pair_by_custom_id:
            continue

        p1, p2 = pair_by_custom_id[custom_id]

        error_obj = entry.get("error")
        if error_obj:
            logger.warning(
                "Batch request error for predicate pair '%s' vs '%s': %s",
                p1,
                p2,
                error_obj,
            )
            result_by_custom_id[custom_id] = {
                "predicate_a": p1,
                "predicate_b": p2,
                "equivalent": False,
                "confidence": 0.0,
                "reason": "request_error",
            }
            continue

        response_obj = entry.get("response")
        if not isinstance(response_obj, dict):
            logger.warning("Missing response for predicate pair '%s' vs '%s'", p1, p2)
            result_by_custom_id[custom_id] = {
                "predicate_a": p1,
                "predicate_b": p2,
                "equivalent": False,
                "confidence": 0.0,
                "reason": "missing_response",
            }
            continue

        body = response_obj.get("body") or {}
        choices = body.get("choices") or []
        if not choices:
            logger.warning("No choices for predicate pair '%s' vs '%s'", p1, p2)
            result_by_custom_id[custom_id] = {
                "predicate_a": p1,
                "predicate_b": p2,
                "equivalent": False,
                "confidence": 0.0,
                "reason": "no_choices",
            }
            continue

        content = str(((choices[0] or {}).get("message") or {}).get("content") or "")
        try:
            parsed = parse_json_response(content)
            equivalent = bool(parsed.get("equivalent", False))
            confidence_raw = parsed.get("confidence", 0.0)
            try:
                confidence = float(confidence_raw)
            except (TypeError, ValueError):
                confidence = 0.0
            reason = str(parsed.get("reason", "")).strip()
            result_by_custom_id[custom_id] = {
                "predicate_a": p1,
                "predicate_b": p2,
                "equivalent": equivalent,
                "confidence": confidence,
                "reason": reason,
            }
        except (JSONDecodeError, ValueError) as exc:
            logger.warning(
                "Invalid JSON in equivalence batch output for '%s' vs '%s': %s",
                p1,
                p2,
                exc,
            )
            result_by_custom_id[custom_id] = {
                "predicate_a": p1,
                "predicate_b": p2,
                "equivalent": False,
                "confidence": 0.0,
                "reason": "invalid_json",
            }

    return result_by_custom_id


def predicates_equivalent_batch(
    client: OpenAI,
    model: str,
    equivalence_system_prompt: str,
    predicate_pairs: list[tuple[str, str]],
    batch_timeout_seconds: int,
) -> list[dict[str, Any]]:
    if not predicate_pairs:
        return []

    batch_jsonl, pair_by_custom_id = build_equivalence_batch_jsonl(
        model=model,
        equivalence_system_prompt=equivalence_system_prompt,
        predicate_pairs=predicate_pairs,
    )
    batch_jsonl_bytes = batch_jsonl.encode("utf-8")
    logger.info("Predicate equivalence batch file size: %d bytes", len(batch_jsonl_bytes))

    input_file = client.files.create(
        file=("predicate_equivalence_batch.jsonl", io.BytesIO(batch_jsonl_bytes)),
        purpose="batch",
    )

    batch = client.batches.create(
        input_file_id=input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    logger.info("Started predicate equivalence batch: %s", batch.id)

    final_batch = wait_for_batch_completion(
        client=client,
        batch_id=batch.id,
        timeout_seconds=batch_timeout_seconds,
    )
    if getattr(final_batch, "status", None) != "completed":
        raise RuntimeError(
            f"Predicate equivalence batch {batch.id} did not complete successfully: {final_batch.status}"
        )

    output_file_id = getattr(final_batch, "output_file_id", None)
    if not output_file_id:
        raise RuntimeError(f"Predicate equivalence batch {batch.id} has no output_file_id")

    output_text = read_openai_file_text(client=client, file_id=output_file_id)
    parsed_by_custom_id = parse_equivalence_batch_output(
        output_text=output_text,
        pair_by_custom_id=pair_by_custom_id,
    )

    ordered_results: list[dict[str, Any]] = []
    for index, (p1, p2) in enumerate(predicate_pairs):
        custom_id = f"predicate-pair-{index}"
        ordered_results.append(
            parsed_by_custom_id.get(
                custom_id,
                {
                    "predicate_a": p1,
                    "predicate_b": p2,
                    "equivalent": False,
                    "confidence": 0.0,
                    "reason": "missing_result",
                },
            )
        )

    return ordered_results


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
        result = call_llm_json(
            client,
            model,
            equivalence_system_prompt,
            user_prompt,
            response_format=EQUIVALENCE_RESPONSE_FORMAT,
        )
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
    batch_timeout_seconds: int,
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

    predicate_pairs = list(itertools.combinations(predicates, 2))
    batch_results = predicates_equivalent_batch(
        client=client,
        model=model,
        equivalence_system_prompt=equivalence_system_prompt,
        predicate_pairs=predicate_pairs,
        batch_timeout_seconds=batch_timeout_seconds,
    )

    for current_num, comparison in enumerate(batch_results, start=1):
        p1 = str(comparison.get("predicate_a", ""))
        p2 = str(comparison.get("predicate_b", ""))
        equivalent = bool(comparison.get("equivalent", False))
        confidence = float(comparison.get("confidence", 0.0))
        reason = str(comparison.get("reason", ""))

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
            logger.debug(
                "Predicates '%s' and '%s' are equivalent (confidence: %.2f)",
                p1,
                p2,
                confidence,
            )
            uf.union(p1, p2)

        logger.info("Completed %d/%d comparisons", current_num, total_pairs)

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


def cmd_extract(args: argparse.Namespace) -> None:
    """Extract triples from input JSON data."""
    logger.info(f"OpenAI base URL: {args.base_url}")
    logger.info(f"Model: {args.model}")

    extraction_system_prompt = load_prompt_override(args.extract_prompt_file, EXTRACTION_SYSTEM_PROMPT)

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    instances = extract_instances(payload)
    instances_num = len(instances)

    logger.info(f"Extracted {instances_num} instances from input JSON")

    client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    all_triples: list[Triple] = []
    triples_by_instance: list[dict[str, Any]] = []

    logger.info("Submitting extraction batch for %d instances...", instances_num)
    triples_by_instance_id = triples_from_instances_batch(
        client=client,
        model=args.model,
        extraction_system_prompt=extraction_system_prompt,
        instances=instances,
        batch_timeout_seconds=args.batch_timeout_seconds,
    )

    for i, instance in enumerate(instances):
        triples = triples_by_instance_id.get(instance["instance_id"], [])
        all_triples.extend(triples)
        triples_by_instance.append(
            {
                "instance_id": instance["instance_id"],
                "triples": [asdict(t) for t in triples],
            }
        )
        logger.info(f"Processed instance {i + 1}/{instances_num}")

    unique_predicates = list(dict.fromkeys(t.predicate for t in all_triples))

    extraction_output = {
        "input_file": args.input,
        "instances_count": len(instances),
        "triples_count": len(all_triples),
        "unique_predicates": unique_predicates,
        "triples_by_instance": triples_by_instance,
        "all_triples": [asdict(t) for t in all_triples],
    }

    Path(args.output).write_text(
        json.dumps(extraction_output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    logger.info(f"Extraction complete. Results saved to {args.output}")


def cmd_normalize(args: argparse.Namespace) -> None:
    """Normalize predicates using extracted triples from extraction output file."""
    logger.info(f"OpenAI base URL: {args.base_url}")
    logger.info(f"Model: {args.model}")

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

    logger.info(f"Loaded {len(all_triples)} triples from {args.input}")
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
    logger.info(f"Normalization complete. Results saved to {args.output}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Two-step semantic triple extraction and normalization pipeline."
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Extract subcommand
    extract_parser = subparsers.add_parser("extract", help="Extract triples from input data")
    extract_parser.add_argument("--input", required=True, help="Path to input JSON file")
    extract_parser.add_argument("--output", required=True, help="Path to output extraction results")
    extract_parser.add_argument("--model", required=True, help="Model name served by vLLM/OpenAI-compatible API")
    extract_parser.add_argument("--base-url", default="http://localhost:8000/v1", help="OpenAI-compatible base URL")
    extract_parser.add_argument("--api-key", default="local-key", help="API key value accepted by the local server")
    extract_parser.add_argument(
        "--extract-prompt-file",
        default=None,
        help="Optional file to override extraction system prompt",
    )
    extract_parser.add_argument(
        "--batch-timeout-seconds",
        type=int,
        default=1800,
        help="Max seconds to wait for extraction batch completion",
    )
    extract_parser.set_defaults(func=cmd_extract)

    # Normalize subcommand
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
