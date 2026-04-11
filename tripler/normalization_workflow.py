import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable

from openai import OpenAI


def run_normalization_from_extraction_output(
    *,
    args: Any,
    logger: Any,
    default_equivalence_system_prompt: str,
    load_prompt_override: Callable[[str | None, str], str],
    normalize_predicates: Callable[..., tuple[list[Any], dict[str, list[str]], list[dict[str, Any]], int]],
    triple_type: type,
) -> None:
    logger.info("OpenAI base URL: %s", args.base_url)
    logger.info("Model: %s", args.model)

    extraction_output = json.loads(Path(args.input).read_text(encoding="utf-8"))
    equivalence_system_prompt = load_prompt_override(
        args.equivalence_prompt_file,
        default_equivalence_system_prompt,
    )

    all_triples_dict = extraction_output.get("all_triples", [])
    all_triples = [
        triple_type(
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
