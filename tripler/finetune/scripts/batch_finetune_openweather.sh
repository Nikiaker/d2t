#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:2
#SBATCH --time=48:00:00
DOMAIN="openweather"
DOMAIN_SEED="2993"
TRIPLE_DOMAIN="weather_forecast"
SERVER_LOG1="$HOME/vllm-server_${DOMAIN}.log"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"

BASE_ID="google/gemma-4-31B-it"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
INPUT_FILE="${INPUT_FILE:-$D2TPATH/tripler/inputs/seed_${DOMAIN_SEED}/${DOMAIN}_dev_${DOMAIN_SEED}.json}"
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
    --top-level-key forecasts \
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