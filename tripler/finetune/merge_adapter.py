"""Merge a trained LoRA adapter back into the base model and save a standalone
fp16/bf16 checkpoint that vLLM can serve directly.

Usage:
    python merge_adapter.py \
        --base-id RedHatAI/gemma-4-31B-it \
        --adapter tripler/finetune/runs/gsmarena/adapter \
        --out $SCRATCH/ft_models/gsmarena_gemma4_31b_merged
"""

import argparse
import logging
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-id", required=True, help="Original HF base id (must match training).")
    parser.add_argument("--adapter", type=Path, required=True, help="Adapter dir produced by train_qlora.py.")
    parser.add_argument("--out", type=Path, required=True, help="Merged model output dir.")
    parser.add_argument("--dtype", default="bfloat16", choices=["bfloat16", "float16"])
    args = parser.parse_args()

    torch_dtype = torch.bfloat16 if args.dtype == "bfloat16" else torch.float16

    logger.info("loading base %s in %s", args.base_id, args.dtype)
    base = AutoModelForCausalLM.from_pretrained(
        args.base_id,
        torch_dtype=torch_dtype,
        device_map="cpu",
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )
    logger.info("loading adapter %s", args.adapter)
    merged = PeftModel.from_pretrained(base, str(args.adapter))
    merged = merged.merge_and_unload()

    args.out.mkdir(parents=True, exist_ok=True)
    logger.info("saving merged model to %s", args.out)
    merged.save_pretrained(str(args.out), safe_serialization=True)

    tokenizer = AutoTokenizer.from_pretrained(args.base_id, trust_remote_code=True)
    tokenizer.save_pretrained(str(args.out))
    logger.info("done; vllm serve %s will load this dir", args.out)


if __name__ == "__main__":
    main()