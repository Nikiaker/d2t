# Fine-tuning a per-domain data-to-text + RDF-triples model

This document describes how a base instruct LLM (Gemma 4 31B IT) is fine-tuned
per domain so that, given a single raw structured-data instance, it emits **both**
a natural-language verbalization of that instance **and** the corresponding set
of RDF semantic triples — in one decode, as a single JSON object.

The pipeline lives in `tripler/finetune/` and the cluster jobs in `.conda/`.

---

## 1. Goal and idea

The existing tripler pipeline produces, for each raw input instance, two outputs
in two separate LLM calls:

1. **Reference text** — a concise natural-language summary of the instance
   (`generated_text_by_instance[i].text`).
2. **Reference triples** — an RDF `(subject, predicate, object)` triple list
   extracted from that text against a per-domain predicate catalog
   (`triples_by_instance[i].triples`).

Those two outputs are already aligned by `instance_id`. They are exactly the
targets a single model would need to produce jointly. So instead of running the
two-stage tripler pipeline at inference time, we **distill** its behavior into
one fine-tuned model: given the raw instance as input, the model learns to emit
`{"text": "...", "triples": [...]}` directly. One decode replaces two LLM calls
plus the predicate-catalog bookkeeping, and the output is a single parseable
JSON blob.

One fine-tuned model is produced **per domain** (e.g. `gsmarena` /
`mobile_phone_specification`). Per-domain specialization keeps the predicate
vocabulary stable and the verbalization style consistent with the reference
labels of that domain.

### Distillation caveat

Because the reference text and reference triples are themselves produced by the
same base LLM via tripler, the fine-tuned model is bounded by the quality of
those labels. It can be **faster and more consistent** than the two-stage
pipeline (one decode, deterministic JSON, no catalog warm-up), but it cannot
exceed the quality of the references. Improving references is an upstream
tripler-prompt concern, not a fine-tuning concern.

---

## 2. Method: QLoRA supervised fine-tuning

We use **QLoRA** (Quantized Low-Rank Adaptation) — the standard recipe for
fine-tuning a large model on a single GPU with limited memory.

### How QLoRA works

- The **base model weights are frozen** and loaded in 4-bit precision (NF4
  quantization with double quantization) via bitsandbytes. Frozen weights cost
  no optimizer state and no gradients, so memory for a 31B model fits on one
  A100 (80 GB).
- A small set of **trainable LoRA adapters** is inserted alongside the frozen
  weights of every attention and MLP projection
  (`q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj`). Each
  adapter is a pair of low-rank matrices `B·A` (rank `r=16`, scaled by
  `α/r`). Only these adapter matrices are updated by the optimizer; their
  parameter count is a tiny fraction of the base model.
- Compute (forward/backward) is done in **bf16** (`bnb_4bit_compute_dtype`); the
  4-bit weights are dequantized on the fly for each matmul. This keeps
  numerical quality close to a full-precision fine-tune while holding memory
  down.
- Gradient checkpointing + paged 8-bit AdamW further reduce activation and
  optimizer memory; FlashAttention-2 speeds up the attention kernels.

After training, the adapter is **merged back into the base** weights
(`merge_and_unload`) and the result is saved as a standard fp16/bf16
checkpoint that vLLM serves directly — no adapter loading needed at inference,
so serving is identical to the existing batch scripts.

### Why this and not full fine-tuning

- Memory: a 31B model in fp16 is ~62 GB just for weights + ~the same for the
  Adam state; full FT needs multi-GPU sharding (FSDP/DeepSpeed). QLoRA fits on
  one A100, which keeps the experiment cheap, reproducible, and SLURM-simple.
- Data volume: with on the order of 800–2000 labeled examples per domain,
  LoRA's low-rank constraint acts as a regularizer and tends to outperform full
  FT at this scale (less overfitting, preserves the base model's general
  abilities).
- Reproducibility: one adapter per domain is a small, inspectable artifact; the
  merged model is drop-in for the existing vLLM serving scripts.

### Completion-only loss

Training uses TRL `SFTTrainer` with `completion_only_loss=True`, which masks the
loss on the prompt tokens (system + user) so gradients flow only from the
assistant's target tokens (`{"text": "...", "triples": [...]}`). This prevents
the model from being trained to *predict the input* and focuses learning on
producing the joint {text, triples} output for the given input.

---

## 3. The single training example

For every raw instance `i` we build one chat-templated example:

- **system** — an instruction to convert one structured instance into concise
  text plus its RDF triples, and to return JSON only with schema
  `{"text":"...","triples":[{"subject","predicate","object"}]}`.
- **user** — byte-identical to the prompt the tripler pipeline used:
  `"Create a concise natural-language summary of this ONE data instance and
  extract its semantic triples.\n\ninstance_context={...}\n\nReturn JSON only."`
  where `{...}` is the JSON serialization of `{"instance_id": i, "data": <raw
  item>}` (the exact object `tripler/app.py::extract_instances` produces, and
  the exact string `app_text_predicate_catalog_stable.py` puts in the user
  message). Prompt parity between training and inference is essential: the
  merged model must see the same token sequence it will see when served.
- **assistant (target / loss)** — `{"text": <ref_text>, "triples": <ref_triples>}`
  serialized as JSON (`ensure_ascii=False`), taken from the tripler output.

These three messages are rendered with the base tokenizer's `chat_template`
(`apply_chat_template, tokenize=False`) so the tokens fed to the trainer match
the tokens vLLM will assemble at serve time.

### Gemma 4 + PEFT note (LoRA target modules)

Gemma 4 wraps every attention/MLP projection in a custom `Gemma4ClippableLinear`
module — an `nn.Module` that holds an inner `nn.Linear` at attribute `.linear`
and applies optional input/output clamping. PEFT's LoRA dispatcher only accepts
`nn.Linear` (and a small allow-list of other types), and the type check runs
**before** `exclude_modules`, so passing the conventional
`target_modules=["q_proj", ..., "down_proj"]` makes PEFT raise
`ValueError: Target module Gemma4ClippableLinear(...) is not supported`. This is
upstream PEFT bug [#3129](https://github.com/huggingface/peft/issues/3129), not
a problem in this pipeline.

Workaround (`train_qlora.py`): pass `target_modules` as a single regex string
that drills into the inner `.linear` submodule of each wrapper:

```python
target_modules=r".*\.(?:q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)\.linear$"
```

Because it is a *string* (not a list), PEFT treats it as a regex and matches the
inner `Linear4bit` (an `nn.Linear` subclass), which it accepts. The wrapper
module stays in place — so the model's state-dict keys are byte-identical to the
official base, and `merge_adapter.py` / `vllm serve` load the merged checkpoint
unchanged. Clamping behavior is preserved at inference because we never unwrap.
`train_qlora.py` also asserts that the regex matched > 0 modules right after
`SFTTrainer` is built, to guard against a silent under-coverage regression
(PEFT only raises when **zero** target modules match — a too-narrow regex that
matches *some* layers would otherwise train without error). If you switch to a
non-multimodal Gemma variant whose projections are plain `nn.Linear`, restore the
plain list `["q_proj", ..., "down_proj"]` and drop the `.linear` suffix.

---

## 4. Pipeline stages

### Stage A — `build_dataset.py`

Zips `tripler/inputs/gsmarena_train.json` (raw instances, ~1000) with the
tripler output JSON by `instance_id`, renders each triple via the Gemma chat
template, and writes TRL-native `train.jsonl` / `dev.jsonl` plus a `split.json`
sidecar recording the held-out `instance_id`s. Default split: 200 dev / rest
train, deterministic by `--seed`.

Working directory: `tripler/finetune/datasets/gsmarena/`.

### Stage B — `train_qlora.py`

QLoRA training (TRL + PEFT) on one A100. Defaults (tuned for ~800 train
examples):

| knob | default |
|---|---|
| epochs | 3 |
| learning rate | 1e-4, cosine, warmup 0.03 |
| per-device batch | 1 |
| grad accum | 16 (effective batch 16) |
| max length | 8192 |
| LoRA r / α / dropout | 16 / 32 / 0.05 |
| precision | bf16 compute, NF4 4-bit weights |
| optimizer | paged_adamw_8bit |
| attention | FlashAttention-2 |
| loss | completion-only (prompt masked) |

Adapter + tokenizer + `training_metadata.json`
(git SHA, base id, seed, final dev loss) are saved to
`tripler/finetune/runs/gsmarena/adapter`.

Scaling beyond ~2000 examples: switch to multi-GPU FSDP by providing an
`accelerate` config in the batch script and requesting `--gres=gpu:4`; the
script's arguments already expose `--bs` and `--grad-accum` to retune. No code
changes needed for data size up to a few thousand on a single A100.

### Stage C — `merge_adapter.py`

Loads the base bf16 instruct model on CPU, attaches the adapter, calls
`merge_and_unload()`, and saves the merged checkpoint to
`$SCRATCH/ft_models/gsmarena_gemma4_31b_merged`. The merged dir is a drop-in
for `vllm serve <path>` — identical to how existing batch scripts serve base
models. No adapter lives at inference.

### Stage D — `eval.py` (separate job)

Standalone evaluation. For each model (base baseline + fine-tuned) it:

1. starts `vllm serve <model>` on a port and waits for the `/v1/models`
   health endpoint,
2. sends the dev prompts with the **exact same** user content used at training
   (zero-shot, no few-shot, `enable_thinking:false` via the chat template),
3. parses each response as `{"text","triples"}`,
4. scores against the dev references.

Metrics (matching `problems/triples_to_text/final_test.py` for comparability
with the thesis results):

- **Text** — BLEU (`evaluate`/sacrebleu) and METEOR (`evaluate`), per-example
  mean over the dev split.
- **Triples** — set precision / recall / F1 over
  `(subject, predicate, object)` tuples against the reference triples
  (micro-averaged TP/FP/FN across the dev set).
- **Predicate catalog adherence** (optional, `--catalog <tripler output>`) —
  the fraction of produced predicates that belong to the domain's
  `unique_predicates` catalog; measures whether the fine-tuned model stays on
  the learned predicate vocabulary.

Output: `tripler/finetune/runs/gsmarena/eval_report.json` with per-model metric
blocks, written incrementally as each model finishes.

---

## 5. Running on the cluster

Two SLURM jobs (matching the existing `.conda/batch_*.sh` style). Both require
`HF_TOKEN` to be exported in the SLURM environment (Gemma weights are gated on
Hugging Face). The `finetune-env` conda env (`.conda/finetune-env.yml`) is used
by both.

### One-shot: build dataset + train + merge

```bash
sbatch .conda/batch_finetune_gsmarena.sh
```

Override knobs via SLURM env when submitting:

```bash
INPUT_FILE=$D2TPATH/tripler/inputs/gsmarena_train.json \
TRIPLES_FILE=$D2TPATH/tripler/outputs/<run>/mobile_phone_specification/extracted_triples_text_predicate_catalog_stable.json \
MERGED_DIR=$SCRATCH/ft_models/gsmarena_gemma4_31b_merged \
sbatch .conda/batch_finetune_gsmarena.sh
```

### Evaluation (separate, re-runnable)

```bash
sbatch .conda/batch_eval_gsmarena.sh
```

Eval starts vLLM twice (base, then merged) and writes the combined report; it
does not retrain, so it can be re-run after model changes without touching
training.

### Conda env creation (one-time, on the cluster)

```bash
conda env create -f .conda/finetune-env.yml
```

`flash-attn` builds for the cluster's CUDA version (`module load CUDA/12.8.0`);
if the wheel build is slow, install it separately with `--no-build-isolation`
inside the env after the rest is installed.

---

## 6. Conventions respected

- **No secrets in the repo.** `HF_TOKEN` and any cluster endpoints come from
  the SLURM environment; they are never written into committed files.
- **Artifacts are gitignored.** `tripler/finetune/datasets/`,
  `tripler/finetune/runs/`, and the merged model under `$SCRATCH` are all
  treated like other `outputs/`/`openevolve_output*` artifacts and are not
  committed.
- **No renames/renumbers** of existing configs/scripts; everything under
  `tripler/finetune/` and the two new `.conda/batch_*gsmarena.sh` files is
  purely additive.
- **Prompt parity** between training and inference is enforced by reusing
  `tripler.app.extract_instances` and the tripler user-prompt wording at
  dataset-build time, and by using the base tokenizer's `chat_template` (the
  same one vLLM applies at serve time).