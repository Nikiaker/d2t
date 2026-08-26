# Fine-tuning a per-domain data-to-text + RDF-triples model

This document describes how a base instruct LLM (Gemma 4 31B IT) is fine-tuned
per domain so that, given a single raw structured-data instance, it emits **both**
a natural-language verbalization of that instance **and** the corresponding set
of RDF semantic triples — in one decode, as a single JSON object.

The pipeline lives in `tripler/finetune/` and the cluster jobs in
`tripler/finetune/scripts/`.

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
  A100-SXM4-40GB (the cluster's 40 GB variant; the original recipe targeted the
  80 GB card, but PLGrid Athena exposes the 40 GB SKU).
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
  optimizer memory; SDPA dispatches sliding (head_dim=256) and global
  (head_dim=512) attention layers to compatible backends.

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

### Loss mode

Training uses TRL `SFTTrainer` with `loss_type="nll"` and
`completion_only_loss=False`. The dataset is conversational (`messages`) rather
than a prompt-completion dataset, so the complete rendered sequence is used by
the standard NLL path. Explicitly selecting NLL avoids TRL's chunked-CE path,
which is incompatible with Gemma 4's wrapped forward function.

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

Gemma 4 is a multimodal checkpoint: the top-level `model` has two sibling
backbones — `model.vision_tower` (image encoder) and `model.language_model`
(text decoder). In `model.vision_tower`, every attention/MLP projection is a
custom `Gemma4ClippableLinear` — an `nn.Module` wrapping an inner
`nn.Linear` at attribute `.linear` with optional input/output clamping. In
`model.language_model`, the projections are **plain `nn.Linear`** (no
`.linear` child). PEFT's LoRA dispatcher only accepts `nn.Linear` (and a small
allow-list of other types), and the type check runs **before**
`exclude_modules`, so the conventional `target_modules=["q_proj", ...,
"down_proj"]` makes PEFT suffix-match the vision tower's `Gemma4ClippableLinear`
first and raise `ValueError: Target module Gemma4ClippableLinear(...) is not
supported`. This is upstream PEFT bug
[#3129](https://github.com/huggingface/peft/issues/3129), not a problem in this
pipeline.

Workaround (`train_qlora.py`): scope `target_modules` **positively to the
language model only**, with no `.linear` suffix (the LM projections are already
plain `nn.Linear`):

```python
target_modules=r"^model\.language_model\..*\.(?:q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)$"
```

Because it is a *string* (not a list), PEFT treats it as a regex; the `^` and
`$` anchors keep it from drifting back to `vision_tower`/`audio_tower`; and
plain `nn.Linear`/`Linear4bit` is on PEFT's accept list. For the 31B Dense
checkpoint (60 LM layers × 7 projections) this matches **420 modules**; if your
run prints `LoRA targeted 420 modules` (and ~25M trainable params) the scoping
is correct. `train_qlora.py` also asserts `len(targeted) > 0` right after
`SFTTrainer` is built, to guard against a silent under-coverage regression
(PEFT only raises when **zero** target modules match — a too-narrow regex that
matches *some* layers would otherwise train without error). The vision/audio
towers see no adapters and stay frozen; their `Gemma4ClippableLinear` wrappers
are untouched, so the model's state-dict keys are byte-identical to the
official base and `merge_adapter.py` / `vllm serve` load the merged checkpoint
unchanged. If training a non-multimodal Gemma variant whose LM projections live
at `model.layers.{i}.self_attn.{...}_proj` (no `language_model` prefix),
loosen the regex to `r"^model\.layers\..*\.(?:...)\$"`.

### Gemma 4 hybrid head-dim + FlashAttention

Gemma 4 uses **hybrid attention**: most layers are sliding-window with
`head_dim=256`, and a few are global with `global_head_dim=512`. FlashAttention
2/3 caps at head dimension 256 on A100 (SM80), so loading the model with
`attn_implementation="flash_attention_2"` makes the first global layer raise
`RuntimeError: FlashAttention forward only supports head dimension at most 256`
([flash-attn#2427](https://github.com/Dao-AILab/flash-attention/issues/2427)).

`train_qlora.py` loads with `attn_implementation="sdpa"` so PyTorch's SDPA
dispatches each layer to a compatible backend automatically: the 256-head
sliding layers still hit the fast flash/cutlass path; the 512-head global
layers fall back to the math backend (no head-dim limit, slower but correct).
No per-layer patching, robust across transformers versions. vLLM serving of
the merged checkpoint is unaffected — vLLM uses its own attention kernels and
already handles `global_head_dim=512` (as in the existing
`tripler/outputs/test9/batch_gsmarena.sh`). If you later want to preserve FA2
on the sliding layers for speed, the hybrid patch from
[prime-rl#2362](https://github.com/PrimeIntellect-ai/prime-rl/issues/2362)
(selectively overrides `_attn_implementation` to `"sdpa"` per global layer)
can be added as an opt-in flag.

---

## 4. Pipeline stages

### Stage A — `build_dataset.py`

Zips `tripler/inputs/<domain>_train.json` (raw instances, ~1000) with the
tripler output JSON by `instance_id`, renders each example via the Gemma chat
template, and writes TRL-native `train.jsonl` / `dev.jsonl` plus a `split.json`
sidecar recording the held-out `instance_id`s. Default split: 200 dev / rest
train, deterministic by `--seed`.

`--triples` accepts **two shapes**, auto-detected:

1. **`joined.json`** (the recommended target, produced by
   `scripts/join_extract_normalize.py` from an
   `app_text_pipeline.py extract` + `normalize` run). Detected via the
   `per_instance` key. The text target is `per_instance[i].reference` and the
   triples target is `per_instance[i].normalized_triples` — i.e. the
   **canonical** predicates after `normalize`, not the raw synonym-bearing
   triples. Canonical targets are the reason the `normalize` step exists: they
   give the model one consistent predicate vocabulary to emit (e.g. always
   `release_date`, never `released`/`launched`), instead of teaching it the
   inconsistent synonyms the raw extractor produced.
2. **Legacy extract-file shape** (`extracted_triples_text_predicate_catalog_stable.json`
   or `extracted_triples_text_pipeline.json`). Detected via the
   `generated_text_by_instance` + `triples_by_instance` keys. Used as a
   fallback for the older test9/test10 outputs. Targets come from
   `generated_text_by_instance[i].text` and `triples_by_instance[i].triples`
   (raw, unnormalized — there is no canonical form in this shape).

`--input` (the raw quintd JSON) remains required in both paths: the user prompt
is rendered from it via `tripler.app.extract_instances` + `json.dumps` to stay
byte-identical to the prompt the tripler pipeline saw — reusing the
`original_data` embedded in `joined.json` would risk key-order/whitespace drift
and break prompt parity with inference time. The matching `--top-level-key`
must match what the tripler run used (`none` for bare-list inputs like
gsmarena/wikidata/owid; `forecasts` for the `{"forecasts":[...]}` openweather
shape).

Working directory: `tripler/finetune/datasets/<domain>/`.

### Stage B — `train_qlora.py`

QLoRA training (TRL + PEFT) on one A100. Defaults (tuned for ~800 train
examples):

| knob | default |
|---|---|
| epochs | 3 |
| learning rate | 1e-4, cosine, warmup 0.03 |
| per-device batch | 1 |
| grad accum | 16 (effective batch 16) |
| max length | 8192 (script default; see note below) |
| LoRA r / α / dropout | 16 / 32 / 0.05 |
| precision | bf16 compute, NF4 4-bit weights |
| optimizer | paged_adamw_8bit |
| attention | SDPA (Gemma 4 hybrid head-dim — see §3 note) |
| loss | standard NLL |

> **Per-domain `--max-len` override.** The 8192 value above is the
> `train_qlora.py` argparse default. The cluster's A100-SXM4-40GB has ~40 GB
> per GPU (half of the 80 GB the original recipe assumed), so at `seq_len≈8192`
> the attention activations plus the `[1, seq, vocab≈128k]` cross-entropy
> logits peak above the free budget — on the longest examples the first
> backward raises `CUDA out of memory`. The batch scripts therefore override
> `--max-len` per domain according to the raw instance-size distribution of
> each input (the user prompt embeds `instance_context={json.dumps(instance)}`
> verbatim, so input bytes map ~linearly to tokens):
>
> - `batch_finetune_wikidata.sh` keeps 8192 (instances are tiny, max ~640 B).
> - `batch_finetune_gsmarena.sh` uses **4096** (instances max ~6.4 KB ≈ 3–4 K
>   tokens; 4096 covers 100% of examples).
> - `batch_finetune_owid.sh` uses **4096** (median ~8.7 KB, but the small ~33%
>   of examples fit fully at 4096; the long-tail time-series instances are
>   truncated).
> - `batch_finetune_openweather.sh` uses **6144** (every forecast instance is
>   ~18 KB ≈ 6–8 K tokens rendered; 4096 would right-truncate the assistant
>   target of 100% of examples, so 6144 keeps the bulk intact while staying
>   under the activation ceiling — borderline; the very largest outliers may
>   still OOM, in which case the upstream fix is to pre-aggregate the forecast
>   time series in `build_dataset.py` rather than dump the raw blob).
>
> All batch scripts also export
> `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` to reduce fragmentation.

Adapter + tokenizer + `training_metadata.json`
(git SHA, base id, seed, final dev loss) are saved to
`tripler/finetune/runs/gsmarena/adapter`.

### Hyperparameter experiments

The shared `experiments.sh` defines these reproducible variants:

| experiment | epochs | learning rate | LoRA r/alpha | dropout | weight decay |
|---|---:|---:|---:|---:|---:|
| `baseline` | 3 | `1e-4` | 16/32 | 0.05 | 0.0 |
| `low_lr` | 5 | `3e-5` | 16/32 | 0.05 | 0.01 |
| `higher_capacity` | 3 | `5e-5` | 32/64 | 0.05 | 0.01 |
| `regularized_capacity` | 5 | `3e-5` | 32/64 | 0.10 | 0.01 |

Non-baseline runs are isolated under
`tripler/finetune/runs/<domain>/<experiment>/` and use experiment-specific
merged model names under `$SCRATCH/ft_models/`. Checkpoints are saved at epoch
boundaries; with 800 training examples and effective batch 16, checkpoints 100
and 150 are available for all listed variants.

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

Standalone evaluation. For each model (base, final adapter, checkpoint 100,
and checkpoint 150) it:

1. starts `vllm serve <model>` on a port and waits for the `/v1/models`
   health endpoint,
2. sends the train and dev prompts with the **exact same** user content used at training
   (zero-shot, no few-shot, `enable_thinking:false` via the chat template),
3. parses each response as `{"text","triples"}`,
4. scores against the corresponding train or dev references.

Metrics (matching `problems/triples_to_text/final_test.py` for comparability
with the thesis results):

- **Text** — BLEU (`evaluate`/sacrebleu) and METEOR (`evaluate`), per-example
  mean over each split.
- **Triples** — set precision / recall / F1 over
  `(subject, predicate, object)` tuples against the reference triples
  (micro-averaged TP/FP/FN across each split).
- **Predicate catalog adherence** (optional, `--catalog <tripler output>`) —
  the fraction of produced predicates that belong to the domain's canonical
  catalog. When the catalog file is a `joined.json` (with
  `unique_predicates_after`) the canonical post-normalization vocabulary is
  used; otherwise the legacy `unique_predicates` list is read. Measures whether
  the fine-tuned model stays on the learned predicate vocabulary.

Output: `tripler/finetune/runs/<domain>/eval_report.json` with one metric block
per model and split, written incrementally as each model finishes.

---

## 5. Running on the cluster

Two SLURM jobs (matching the existing batch style). Both require `HF_TOKEN` to
be exported in the SLURM environment (Gemma weights are gated on Hugging Face).
The training and evaluation drivers use `finetune-env`; evaluation launches
vLLM through the separate `vllm-env` environment.

### One-shot: build dataset + train + merge

```bash
sbatch tripler/finetune/scripts/batch_finetune_gsmarena.sh
```

To run all three new variants for all four domains, submit:

```bash
bash tripler/finetune/run_hyperparameter_experiments.sh
```

Override knobs via SLURM env when submitting:

```bash
EXPERIMENT=low_lr INPUT_FILE=$D2TPATH/tripler/inputs/gsmarena_train.json \
TRIPLES_FILE=$D2TPATH/tripler/outputs/<run>/mobile_phone_specification/extracted_triples_text_predicate_catalog_stable.json \
MERGED_DIR=$SCRATCH/ft_models/gsmarena_gemma4_31b_low_lr_merged \
sbatch tripler/finetune/scripts/batch_finetune_gsmarena.sh
```

### Evaluation (separate, re-runnable)

```bash
EXPERIMENT=low_lr sbatch tripler/finetune/scripts/batch_eval_gsmarena.sh
```

Eval starts vLLM once per model (base, final, checkpoint 100, and checkpoint
150), evaluates both train and dev, and writes the combined report. It does not
retrain, so it can be re-run after model changes without touching training.

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
- **No renames/renumbers** of existing configs/scripts; experiment support is
  additive and existing baseline paths remain supported.
- **Prompt parity** between training and inference is enforced by reusing
  `tripler.app.extract_instances` and the tripler user-prompt wording at
  dataset-build time, and by using the base tokenizer's `chat_template` (the
  same one vLLM applies at serve time).
