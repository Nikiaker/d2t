"""Build a TRL-native SFT dataset by zipping raw input instances with tripler
reference outputs (text + triples) for a single domain.

Usage:
    python build_dataset.py \
        --input tripler/inputs/gsmarena_train.json \
        --triples tripler/outputs/<run>/mobile_phone_specification/extracted_triples_text_predicate_catalog_stable.json \
        --out-dir tripler/finetune/datasets/gsmarena \
        --base-id RedHatAI/gemma-4-31B-it \
        --holdout 200 --seed 13

Each output record is {"messages": [{"role":"system"},{"role":"user"},{"role":"assistant"}]}.
The assistant target is a single JSON object {"text": "...", "triples": [...]}.
Prompt parity with the tripler extraction pipeline is preserved by reusing its
instance serialization and user-prompt wording byte-for-byte.
"""

import argparse
import json
import logging
import random
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_TRIPLER_DIR = _REPO_ROOT / "tripler"
if str(_TRIPLER_DIR) not in sys.path:
    sys.path.insert(0, str(_TRIPLER_DIR))

from app import extract_instances  # noqa: E402
from transformers import AutoTokenizer  # noqa: E402

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You convert one structured data instance into concise natural language and a "
    "corresponding set of RDF semantic triples. "
    'Return ONLY JSON with schema: {"text":"...","triples":[{'
    '"subject":"...","predicate":"...","object":"..."}]}. '
    "Capture the most important information, trends, extremes, and notable conditions. "
    "Use concise predicate labels in lower_snake_case when possible and avoid duplicates. "
    "If the instance contains a time series (for example a weather forecast), summarize it "
    "at a high level instead of listing every point."
)


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False))
            fh.write("\n")


def _build_user_prompt(instance: dict[str, Any]) -> str:
    return (
        "Create a concise natural-language summary of this ONE data instance "
        "and extract its semantic triples.\n\n"
        f"instance_context={json.dumps(instance, ensure_ascii=False)}\n\n"
        "Return JSON only."
    )


def _build_target(text: str, triples: list[dict[str, str]]) -> str:
    payload = {"text": text, "triples": triples}
    return json.dumps(payload, ensure_ascii=False)


def _index_triples_output(triples_output: dict[str, Any]) -> dict[int, dict[str, Any]]:
    by_id: dict[int, dict[str, Any]] = {}
    for entry in triples_output.get("triples_by_instance", []):
        if isinstance(entry, dict) and "instance_id" in entry:
            by_id[int(entry["instance_id"])] = entry
    return by_id


def _index_text_output(triples_output: dict[str, Any]) -> dict[int, str]:
    by_id: dict[int, str] = {}
    for entry in triples_output.get("generated_text_by_instance", []):
        if isinstance(entry, dict) and "instance_id" in entry and "text" in entry:
            by_id[int(entry["instance_id"])] = str(entry["text"])
    return by_id


def _is_joined(doc: dict[str, Any]) -> bool:
    return isinstance(doc.get("per_instance"), list)


def _index_joined(doc: dict[str, Any]) -> tuple[dict[int, str], dict[int, dict[str, Any]], set[str]]:
    text_by_id: dict[int, str] = {}
    triples_by_id: dict[int, dict[str, Any]] = {}
    for entry in doc["per_instance"]:
        if not isinstance(entry, dict) or "instance_id" not in entry:
            continue
        iid = int(entry["instance_id"])
        text_by_id[iid] = str(entry.get("reference", ""))
        triples_by_id[iid] = {"triples": entry.get("normalized_triples", [])}
    catalog = set(doc.get("unique_predicates_after", []) or doc.get("unique_predicates", []))
    return text_by_id, triples_by_id, catalog


def build_records(
    instances: list[dict[str, Any]],
    text_by_id: dict[int, str],
    triples_by_id: dict[int, dict[str, Any]],
    tokenizer,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    skipped = 0
    for inst in instances:
        iid = int(inst["instance_id"])
        if iid not in text_by_id or iid not in triples_by_id:
            skipped += 1
            continue
        ref_text = text_by_id[iid]
        ref_triples = triples_by_id[iid].get("triples", [])
        if not isinstance(ref_triples, list):
            skipped += 1
            continue
        user_prompt = _build_user_prompt(inst)
        target = _build_target(ref_text, ref_triples)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": target},
        ]
        try:
            rendered = tokenizer.apply_chat_template(messages, tokenize=False)
        except Exception as exc:
            logger.warning("chat template render failed for instance %s: %s", iid, exc)
            skipped += 1
            continue
        records.append(
            {
                "instance_id": iid,
                "messages": messages,
                "prompt": rendered[: rendered.index(target)] if target in rendered else "",
                "target": target,
            }
        )
    if skipped:
        logger.warning("skipped %d/%d instances without matching reference text+triples", skipped, len(instances))
    return records


def _split(records: list[dict[str, Any]], holdout: int, seed: int) -> tuple[list, list, list[int]]:
    rng = random.Random(seed)
    idxs = [r["instance_id"] for r in records]
    rng.shuffle(idxs)
    dev_ids = set(idxs[:holdout]) if holdout > 0 else set()
    train = [r for r in records if r["instance_id"] not in dev_ids]
    dev = [r for r in records if r["instance_id"] in dev_ids]
    return train, dev, sorted(dev_ids)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Raw quintd input JSON (list or dict).")
    parser.add_argument("--triples", type=Path, required=True, help="tripler output JSON (text+triples).")
    parser.add_argument("--out-dir", type=Path, required=True, help="Output dir for train.jsonl/dev.jsonl.")
    parser.add_argument("--base-id", default="RedHatAI/gemma-4-31B-it", help="HF base model id (chat template source).")
    parser.add_argument("--top-level-key", default="none", help="Passed to extract_instances ('none' => payload is a list).")
    parser.add_argument("--holdout", type=int, default=200, help="Number of instances reserved for dev eval.")
    parser.add_argument("--seed", type=int, default=13, help="Shuffle seed for the dev split.")
    args = parser.parse_args()

    payload = _load_json(args.input)
    triples_output = _load_json(args.triples)
    instances = extract_instances(payload, top_level_key=args.top_level_key)

    if _is_joined(triples_output):
        text_by_id, triples_by_id, _catalog = _index_joined(triples_output)
        logger.info("loaded %d instances (%s) + joined.json (%d per_instance, normalized_triples target)",
                    len(instances), args.input, len(triples_output["per_instance"]))
    else:
        text_by_id = _index_text_output(triples_output)
        triples_by_id = _index_triples_output(triples_output)
        logger.info("loaded %d instances (%s), %d reference texts, %d reference triples (legacy extract shape)",
                    len(instances), args.input, len(triples_output.get("generated_text_by_instance", [])),
                    len(triples_output.get("triples_by_instance", [])))

    tokenizer = AutoTokenizer.from_pretrained(args.base_id, trust_remote_code=True)
    if tokenizer.chat_template is None:
        raise RuntimeError(f"Tokenizer for {args.base_id} has no chat_template; supply a model with one.")

    records = build_records(instances, text_by_id, triples_by_id, tokenizer)
    if not records:
        raise RuntimeError("No trainable records produced; check input/triples alignment by instance_id.")
    logger.info("built %d aligned records from %d instances", len(records), len(instances))

    holdout = min(args.holdout, len(records) // 5)
    if args.holdout > 0 and holdout != args.holdout:
        logger.warning("holdout reduced to %d (max 1/5 of records)", holdout)
    train, dev, dev_ids = _split(records, holdout, args.seed)
    logger.info("split: %d train / %d dev (dev ids: %s)", len(train), len(dev), dev_ids[:10])

    args.out_dir.mkdir(parents=True, exist_ok=True)
    _write_jsonl([{"messages": r["messages"]} for r in train], args.out_dir / "train.jsonl")
    _write_jsonl([{"messages": r["messages"]} for r in dev], args.out_dir / "dev.jsonl")
    split_meta = {
        "input": str(args.input),
        "triples": str(args.triples),
        "base_id": args.base_id,
        "seed": args.seed,
        "holdout": holdout,
        "n_train": len(train),
        "n_dev": len(dev),
        "dev_ids": sorted(dev_ids),
    }
    (args.out_dir / "split.json").write_text(json.dumps(split_meta, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("wrote %s/{train,dev}.jsonl and split.json", args.out_dir)


if __name__ == "__main__":
    main()