"""Evaluate one or more Gemma checkpoints on the held-out dev split produced
by build_dataset.py. Each model is served via vLLM, queried with the exact same
zero-shot prompt used at training (no few-shot), and scored against the
reference {text, triples} from dev.jsonl.

Metrics (matching problems/triples_to_text/final_test.py for comparability):
  - text:    BLEU (evaluate) and METEOR (evaluate), per-example mean
  - triples: set precision / recall / F1 over (subject, predicate, object) tuples
  - optional: predicate catalog adherence to the tripler unique_predicates list

Usage:
    python eval.py \
        --dev tripler/finetune/datasets/gsmarena/dev.jsonl \
        --port 2997 \
        --report tripler/finetune/runs/gsmarena/eval_report.json \
        --model base RedHatAI/gemma-4-31B-it \
        --model ft $SCRATCH/ft_models/gsmarena_gemma4_31b_merged \
        [--catalog tripler/outputs/<run>/mobile_phone_specification/extracted_triples_text_predicate_catalog_stable.json]
"""

import argparse
import json
import logging
import re
import subprocess
import time
from pathlib import Path

import numpy as np
from openai import OpenAI

import evaluate  # noqa: E402

logger = logging.getLogger(__name__)

_BLEU = None
_METEOR = None


def _metrics():
    global _BLEU, _METEOR
    if _BLEU is None:
        _BLEU = evaluate.load("bleu")
        _METEOR = evaluate.load("meteor")
    return _BLEU, _METEOR


def _load_dev(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _prompt_messages(record: dict) -> list[dict]:
    msgs = record["messages"]
    return [m for m in msgs if m["role"] != "assistant"]


def _assistant_target(record: dict) -> dict:
    for m in record["messages"]:
        if m["role"] == "assistant":
            return json.loads(m["content"])
    raise ValueError("record has no assistant message")


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, flags=re.S)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def _wait_for_vllm(port: int, api_key: str, timeout: int = 600) -> bool:
    client = OpenAI(base_url=f"http://localhost:{port}/v1", api_key=api_key)
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            client.models.list()
            return True
        except Exception:
            time.sleep(5)
    return False


def _start_vllm(model_path: str, port: int, api_key: str) -> subprocess.Popen:
    cmd = [
        "vllm", "serve", model_path,
        "--port", str(port),
        "--api-key", api_key,
        "--max-model-len", "30K",
        "--reasoning-parser", "gemma4",
        "--default-chat-template-kwargs", '{"enable_thinking": false}',
        "--max-num-batched-tokens", "4096",
        "--gpu-memory-utilization", "0.95",
    ]
    logger.info("starting vLLM: %s", " ".join(cmd))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return proc


def _generate(client: OpenAI, model: str, dev: list[dict], max_tokens: int) -> list[dict | None]:
    out = []
    for i, rec in enumerate(dev):
        msgs = _prompt_messages(rec)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=msgs,
                temperature=0.0,
                max_tokens=max_tokens,
            )
            content = resp.choices[0].message.content or ""
        except Exception as exc:
            logger.warning("generate failed for example %d: %s", i, exc)
            out.append(None)
            continue
        parsed = _extract_json(content)
        out.append({"raw": content, "parsed": parsed})
    return out


def _triple_set(triples: list) -> set[tuple[str, str, str]]:
    s = set()
    for t in triples or []:
        try:
            s.add((str(t["subject"]), str(t["predicate"]), str(t["object"])))
        except Exception:
            continue
    return s


def _score_model(name: str, preds: list[dict | None], dev: list[dict], catalog: set[str] | None) -> dict:
    bleu, meteor = _metrics()
    bleu_scores, meteor_scores = [], []
    tp = fp = fn = 0
    adhere = 0
    adhere_total = 0
    n_parsed = 0
    for pred, rec in zip(preds, dev):
        ref = _assistant_target(rec)
        ref_text = ref.get("text", "")
        ref_set = _triple_set(ref.get("triples", []))
        if pred is None or pred["parsed"] is None:
            pred_text = ""
            pred_set = set()
        else:
            n_parsed += 1
            pred_text = pred["parsed"].get("text", "") or ""
            pred_set = _triple_set(pred["parsed"].get("triples", []))
            if catalog is not None:
                for tr in pred["parsed"].get("triples", []) or []:
                    adhere_total += 1
                    if str(tr.get("predicate", "")) in catalog:
                        adhere += 1
        b = bleu.compute(predictions=[pred_text], references=[[ref_text]])
        bleu_scores.append(float(b["bleu"]))
        m = meteor.compute(predictions=[pred_text], references=[[ref_text]])
        meteor_scores.append(float(m["meteor"]))
        tp += len(pred_set & ref_set)
        fp += len(pred_set - ref_set)
        fn += len(ref_set - pred_set)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {
        "model": name,
        "n_dev": len(dev),
        "n_parsed": n_parsed,
        "parse_rate": n_parsed / len(dev) if dev else 0.0,
        "bleu": float(np.mean(bleu_scores)) if bleu_scores else 0.0,
        "meteor": float(np.mean(meteor_scores)) if meteor_scores else 0.0,
        "triple_precision": prec,
        "triple_recall": rec,
        "triple_f1": f1,
        "triple_tp": tp,
        "triple_fp": fp,
        "triple_fn": fn,
        "predicate_adherence": (adhere / adhere_total) if (catalog is not None and adhere_total) else None,
    }


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dev", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--port", type=int, default=2997)
    parser.add_argument("--api-key", default="none")
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument("--model", action="append", nargs=2, metavar=("LABEL", "PATH"),
                        required=True, help="Repeatable: --model <label> <hf_id_or_path>")
    parser.add_argument("--catalog", type=Path, default=None,
                        help="tripler output JSON to read unique_predicates from.")
    args = parser.parse_args()

    catalog = None
    if args.catalog:
        cdoc = json.loads(args.catalog.read_text(encoding="utf-8"))
        catalog = set(cdoc.get("unique_predicates", []))
        logger.info("loaded %d catalog predicates", len(catalog))

    dev = _load_dev(args.dev)
    logger.info("loaded %d dev examples", len(dev))

    results = []
    for label, path in args.model:
        proc = _start_vllm(path, args.port, args.api_key)
        try:
            if not _wait_for_vllm(args.port, args.api_key):
                logger.error("vLLM did not become ready for %s; skipping", label)
                continue
            client = OpenAI(base_url=f"http://localhost:{args.port}/v1", api_key=args.api_key)
            served_name = path
            preds = _generate(client, served_name, dev, args.max_tokens)
            res = _score_model(label, preds, dev, catalog)
            logger.info("%s: bleu=%.4f meteor=%.4f triple_f1=%.4f parse_rate=%.3f",
                        label, res["bleu"], res["meteor"], res["triple_f1"], res["parse_rate"])
            results.append(res)
            with open(args.report, "w", encoding="utf-8") as fh:
                json.dump({"models": results}, fh, indent=2, ensure_ascii=False)
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=120)
            except Exception:
                proc.kill()

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as fh:
        json.dump({"models": results}, fh, indent=2, ensure_ascii=False)
    logger.info("report written to %s", args.report)


if __name__ == "__main__":
    main()