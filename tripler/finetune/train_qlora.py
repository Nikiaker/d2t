"""QLoRA supervised fine-tuning of a Gemma instruct model on a per-domain
{text, triples} dataset produced by build_dataset.py.

Single-A100 defaults target ~800 train examples. Scale to multi-GPU FSDP by
providing an accelerate config in the batch script (no changes here needed for
data size up to a few thousand).

Usage:
    python train_qlora.py \
        --base-id RedHatAI/gemma-4-31B-it \
        --train tripler/finetune/datasets/gsmarena/train.jsonl \
        --dev tripler/finetune/datasets/gsmarena/dev.jsonl \
        --out tripler/finetune/runs/gsmarena/adapter \
        --epochs 3 --lr 1e-4 --max-len 8192 --lora-r 16
"""

import argparse
import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from datasets import load_dataset
from peft import LoraConfig
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTConfig, SFTTrainer

logger = logging.getLogger(__name__)


@dataclass
class TrainMetadata:
    base_id: str
    train_path: str
    dev_path: str
    out_dir: str
    epochs: float
    lr: float
    max_len: int
    lora_r: int
    lora_alpha: int
    lora_dropout: float
    eff_batch: int
    warmup_ratio: float
    weight_decay: float
    seed: int
    git_sha: str
    final_dev_loss: float


def _git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


def _load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-id", default="RedHatAI/gemma-4-31B-it")
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--dev", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="Adapter output dir.")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--max-len", type=int, default=8192)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--lora-dropout", type=float, default=0.05)
    parser.add_argument("--bs", type=int, default=1, help="per_device_train_batch_size")
    parser.add_argument("--grad-accum", type=int, default=16)
    parser.add_argument("--warmup-ratio", type=float, default=0.03)
    parser.add_argument("--weight-decay", type=float, default=0.0)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--max-steps", type=int, default=-1, help="Smoke-test override (-1 = full run).")
    args = parser.parse_args()

    if not os.environ.get("HF_TOKEN"):
        logger.warning("HF_TOKEN not set; Gemma is gated and download will fail without it.")

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.base_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_id,
        quantization_config=bnb,
        dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
        attn_implementation="sdpa",
    )
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    if hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()

    train_ds = load_dataset("json", data_files=str(args.train), split="train")
    dev_ds = load_dataset("json", data_files=str(args.dev), split="train")

    lora = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=r"^model\.language_model\..*\.(?:q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)$",
    )

    sft_args = SFTConfig(
        output_dir=str(args.out),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.bs,
        per_device_eval_batch_size=args.bs,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        lr_scheduler_type="cosine",
        warmup_ratio=args.warmup_ratio,
        logging_steps=5,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=5,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        bf16=True,
        optim="paged_adamw_8bit",
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        max_length=args.max_len,
        packing=False,
        loss_type="nll",
        completion_only_loss=False,
        report_to="none",
        seed=args.seed,
        data_seed=args.seed,
        max_steps=args.max_steps,
        dataset_text_field="messages",
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_args,
        train_dataset=train_ds,
        eval_dataset=dev_ds,
        processing_class=tokenizer,
        peft_config=lora,
    )
    peft_model = trainer.model
    targeted = (
        getattr(peft_model, "targeted_module_names", None)
        or getattr(getattr(peft_model, "base_model", None), "targeted_module_names", None)
        or []
    )
    logger.info("LoRA targeted %d modules; sample=%s", len(targeted), targeted[:3])
    assert len(targeted) > 0, "regex matched 0 modules — adapter would train nothing"
    if hasattr(peft_model, "print_trainable_parameters"):
        peft_model.print_trainable_parameters()
    logger.info("starting training: %d train / %d dev, eff batch=%d, max_len=%d",
                len(train_ds), len(dev_ds), args.bs * args.grad_accum, args.max_len)
    trainer.train()

    eval_metrics = trainer.evaluate()
    final_dev_loss = float(eval_metrics.get("eval_loss", float("nan")))
    logger.info("final dev loss: %.4f", final_dev_loss)

    args.out.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(args.out))
    tokenizer.save_pretrained(str(args.out))

    meta = TrainMetadata(
        base_id=args.base_id,
        train_path=str(args.train),
        dev_path=str(args.dev),
        out_dir=str(args.out),
        epochs=args.epochs,
        lr=args.lr,
        max_len=args.max_len,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        eff_batch=args.bs * args.grad_accum,
        warmup_ratio=args.warmup_ratio,
        weight_decay=args.weight_decay,
        seed=args.seed,
        git_sha=_git_sha(),
        final_dev_loss=final_dev_loss,
    )
    (args.out / "training_metadata.json").write_text(
        json.dumps(asdict(meta), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("saved adapter + metadata to %s", args.out)


if __name__ == "__main__":
    main()
