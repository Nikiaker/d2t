#!/usr/bin/env python3
"""Offline join of an extraction-output JSON and a normalization-output JSON.

This script reconstructs the per-instance (original_data, reference, raw_triples,
normalized_triples) view that the tripler `normalize` subcommand does not emit.
It does NOT call any LLM and does NOT modify any tripler source; it only reads
two JSON files that a tripler run already produced and writes a joined JSON.

Usage:
  python scripts/join_extract_normalize.py \
      --extract  <path/to/extract_output.json> \
      --normalize <path/to/normalize_output.json> \
      --output   <path/to/joined_output.json> \
      [--input <path/to/original_input.json>] \
      [--top-level-key <key|none>]

If --input is given, the original raw instance data is included in the output,
aligned by zero-based index (matching `instance_id` assigned by
`app.extract_instances`). If --top-level-key is given, it selects the list
inside the input JSON the same way `app.extract_instances` would (e.g.
"forecasts", "list", "none" for a bare array). If omitted, the script tries the
same auto-detection heuristics used by `app.extract_instances`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def select_input_list(payload: Any, top_level_key: str | None) -> list[Any]:
    """Mirror app.extract_instances' instance selection (list-only branch).

    Returns the raw list of instances in input order, so that index i corresponds
    to instance_id i. Raises ValueError with a helpful message on mismatched
    shapes, matching the semantics of `app.extract_instances`.
    """
    if top_level_key == "none":
        if not isinstance(payload, list):
            raise ValueError("When --top-level-key='none', input must be a JSON array")
        return list(payload)

    if top_level_key is not None:
        if not isinstance(payload, dict):
            raise ValueError(f"Input must be a JSON object to use --top-level-key={top_level_key!r}")
        items = payload.get(top_level_key)
        if not isinstance(items, list):
            raise ValueError(f"Key {top_level_key!r} is not a list in the input JSON")
        return list(items)

    # Auto-detect (matches app.extract_instances heuristics).
    if isinstance(payload, dict) and isinstance(payload.get("forecasts"), list):
        return list(payload["forecasts"])
    if isinstance(payload, dict) and isinstance(payload.get("list"), list):
        return list(payload["list"])
    if isinstance(payload, list):
        return list(payload)
    raise ValueError(
        "Could not auto-detect input list. Expected one of: "
        "{forecasts:[...]}, {list:[...]}, or a bare array. "
        "Pass --top-level-key to disambiguate."
    )


def build_canonical_map(normalize_output: dict[str, Any]) -> dict[str, str]:
    """Map every synonym predicate -> its canonical representative.

    `predicate_groups` maps canonical -> [synonyms...] and, per `app.py:889-898`,
    the canonical is itself a member of its group, so
    `canonical_map[canonical] == canonical` holds trivially.
    """
    groups = normalize_output.get("predicate_groups", {})
    canonical_map: dict[str, str] = {}
    for canonical, synonyms in groups.items():
        for s in synonyms:
            canonical_map[s] = canonical
    return canonical_map


def normalize_triples(
    raw_triples: list[dict[str, Any]],
    canonical_map: dict[str, str],
) -> list[dict[str, Any]]:
    """Rewrite the predicate field only; subject and object are preserved.

    Mirrors `app.normalize_predicates` (`app.py:900-903`), which substitutes
    each predicate with its class representative and leaves the rest verbatim.
    A defensive `.get(..., original)` fallback is kept even though every
    extracted predicate should appear as a key in the mapping.
    """
    normalized: list[dict[str, Any]] = []
    for t in raw_triples:
        original_predicate = t.get("predicate", "")
        normalized.append(
            {
                "subject": t.get("subject", ""),
                "predicate": canonical_map.get(original_predicate, original_predicate),
                "object": t.get("object", ""),
            }
        )
    return normalized


def index_by_instance_id(items: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    indexed: dict[int, dict[str, Any]] = {}
    for entry in items:
        iid = entry.get("instance_id")
        if iid is None:
            continue
        indexed[int(iid)] = entry
    return indexed


def sanity_check(extract_output: dict[str, Any], normalize_output: dict[str, Any]) -> None:
    """Warn loudly if the two JSONs are not from the same tripler run."""
    source = normalize_output.get("extraction_source")
    input_file = extract_output.get("input_file")
    if source and input_file and Path(source).resolve() != Path(input_file).resolve():
        print(
            f"WARNING: normalize output's extraction_source={source!r} does not "
            f"match extract output's input_file={input_file!r}. The two files "
            f"may not come from the same extraction run; results may be wrong.",
            file=sys.stderr,
        )

    before = set(normalize_output.get("unique_predicates_before", []))
    extracted = set(extract_output.get("unique_predicates", []))
    if before and before != extracted:
        only_in_extract = extracted - before
        only_in_normalize = before - extracted
        if only_in_extract or only_in_normalize:
            print(
                "WARNING: predicate sets disagree between extract and normalize "
                f"outputs (extract-only={sorted(only_in_extract)}, "
                f"normalize-only={sorted(only_in_normalize)}). ",
                file=sys.stderr,
            )


def cmd_join(args: argparse.Namespace) -> None:
    extract_output = load_json(args.extract)
    normalize_output = load_json(args.normalize)

    sanity_check(extract_output, normalize_output)

    canonical_map = build_canonical_map(normalize_output)

    text_by_id = index_by_instance_id(extract_output.get("generated_text_by_instance", []))
    raw_triples_by_id = index_by_instance_id(extract_output.get("triples_by_instance", []))

    # Optional: load original input and select the raw instance list.
    raw_instances: list[Any] | None = None
    if args.input:
        input_payload = load_json(args.input)
        raw_instances = select_input_list(input_payload, args.top_level_key)

    instances_count = int(extract_output.get("instances_count", 0))

    per_instance: list[dict[str, Any]] = []
    for iid in range(instances_count):
        text_entry = text_by_id.get(iid, {})
        triples_entry = raw_triples_by_id.get(iid, {})

        raw_triples = list(triples_entry.get("triples", []))
        norm_triples = normalize_triples(raw_triples, canonical_map)

        joined: dict[str, Any] = {
            "instance_id": iid,
            "reference": text_entry.get("text", ""),
            "raw_triples": raw_triples,
            "normalized_triples": norm_triples,
        }

        if raw_instances is not None:
            if iid < len(raw_instances):
                joined["original_data"] = raw_instances[iid]
            else:
                joined["original_data"] = None
                print(
                    f"WARNING: instance_id={iid} has no corresponding entry in "
                    f"the input list (len={len(raw_instances)}); original_data "
                    f"set to null.",
                    file=sys.stderr,
                )

        per_instance.append(joined)

    flat_raw = extract_output.get("all_triples", [])
    flat_normalized = [
        {
            "subject": t.get("subject", ""),
            "predicate": canonical_map.get(t.get("predicate", ""), t.get("predicate", "")),
            "object": t.get("object", ""),
        }
        for t in flat_raw
    ]

    output: dict[str, Any] = {
        "extraction_source": extract_output.get("input_file"),
        "normalization_source": args.normalize,
        "input_source": args.input,
        "instances_count": instances_count,
        "triples_count": int(extract_output.get("triples_count", 0)),
        "unique_predicates_before": extract_output.get("unique_predicates", []),
        "unique_predicates_after": normalize_output.get("unique_predicates_after", []),
        "predicate_groups": normalize_output.get("predicate_groups", {}),
        "predicate_pair_comparisons_count": normalize_output.get(
            "predicate_pair_comparisons_count", 0
        ),
        "per_instance": per_instance,
        "all_triples": flat_raw,
        "all_triples_normalized": flat_normalized,
    }

    Path(args.output).write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Joined output written to {args.output}")
    print(
        f"  instances: {instances_count}  "
        f"triples (raw): {len(flat_raw)}  "
        f"predicates (before/after): "
        f"{len(output['unique_predicates_before'])}/"
        f"{len(output['unique_predicates_after'])}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Offline join of tripler extract + normalize outputs into a "
            "per-instance (original_data, reference, raw_triples, "
            "normalized_triples) JSON. Does not call any LLM."
        )
    )
    parser.add_argument(
        "--extract",
        required=True,
        help="Path to the JSON produced by `app_text_pipeline.py ... extract` "
        "(or app.py extract).",
    )
    parser.add_argument(
        "--normalize",
        required=True,
        help="Path to the JSON produced by `... normalize --input <extract.json>`.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to write the joined JSON.",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Optional path to the original raw input JSON. When given, the "
        "original instance data is included per-instance, aligned by zero-based "
        "index (matching instance_id assignment in app.extract_instances).",
    )
    parser.add_argument(
        "--top-level-key",
        default=None,
        help="Top-level JSON key holding the instance list in --input (e.g. "
        "'forecasts', 'list', or 'none' for a bare array). If omitted, the "
        "same auto-detection heuristics as app.extract_instances are used.",
    )
    args = parser.parse_args()
    cmd_join(args)


if __name__ == "__main__":
    main()