#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
DOMAIN="gsmarena"
TRIPLE_DOMAIN="mobile_phone_specification"
SERVER_LOG1="$HOME/vllm-server_${DOMAIN}.log"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"

BASE_ID="google/gemma-4-31B-it"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
INPUT_FILE="${INPUT_FILE:-$D2TPATH/tripler/inputs/${DOMAIN}_train.json}"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}"
ADAPTER_DIR="$RUN_DIR/adapter"
MERGED_DIR="${MERGED_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b_merged}"

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