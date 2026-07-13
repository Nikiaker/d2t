#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:1
#SBATCH --time=10:00:00

set -euo pipefail

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"

export D2TPATH="${D2TPATH:-$HOME/d2t}"
export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"
export HF_TOKEN="${HF_TOKEN:?HF_TOKEN must be exported}"

BASE_ID="RedHatAI/gemma-4-31B-it"
DOMAIN="gsmarena"
TRIPLE_DOMAIN="mobile_phone_specification"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test9/${TRIPLE_DOMAIN}/extracted_triples_text_predicate_catalog_stable.json}"
INPUT_FILE="${INPUT_FILE:-$D2TPATH/tripler/inputs/gsmarena_train.json}"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}"
ADAPTER_DIR="$RUN_DIR/adapter"
MERGED_DIR="${MERGED_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b_merged}"

mkdir -p "$DATA_DIR" "$RUN_DIR"

conda run -n finetune-env python "$D2TPATH/tripler/finetune/build_dataset.py" \
    --input "$INPUT_FILE" \
    --triples "$TRIPLES_FILE" \
    --out-dir "$DATA_DIR" \
    --base-id "$BASE_ID" \
    --top-level-key none \
    --holdout 200 --seed 13

conda run -n finetune-env python "$D2TPATH/tripler/finetune/train_qlora.py" \
    --base-id "$BASE_ID" \
    --train "$DATA_DIR/train.jsonl" \
    --dev "$DATA_DIR/dev.jsonl" \
    --out "$ADAPTER_DIR" \
    --epochs 3 --lr 1e-4 --max-len 8192 --lora-r 16 --lora-alpha 32 \
    --bs 1 --grad-accum 16 --seed 13

conda run -n finetune-env python "$D2TPATH/tripler/finetune/merge_adapter.py" \
    --base-id "$BASE_ID" \
    --adapter "$ADAPTER_DIR" \
    --out "$MERGED_DIR" \
    --dtype bfloat16

echo "FINETUNE DONE merged=$MERGED_DIR"