#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:2
#SBATCH --time=48:00:00
set -eo pipefail
DOMAIN="openweather"
DOMAIN_SEED="2993"
TRIPLE_DOMAIN="weather_forecast"
EXPERIMENT="${EXPERIMENT:-baseline}"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"
conda activate finetune-env
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
source "$D2TPATH/tripler/finetune/experiments.sh"
configure_experiment "$EXPERIMENT"

BASE_ID="google/gemma-4-31B-it"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
INPUT_FILE="${INPUT_FILE:-$D2TPATH/tripler/inputs/seed_${DOMAIN_SEED}/${DOMAIN}_dev_${DOMAIN_SEED}.json}"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
if [ "$EXPERIMENT" = "baseline" ]; then
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}"
    EXPERIMENT_SUFFIX=""
else
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}/${EXPERIMENT}"
    EXPERIMENT_SUFFIX="_${EXPERIMENT}"
fi
ADAPTER_DIR="$RUN_DIR/adapter"
MERGED_DIR="${MERGED_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_merged}"
CHECKPOINT_100_DIR="$RUN_DIR/checkpoint-100"
CHECKPOINT_150_DIR="$RUN_DIR/checkpoint-150"
MERGED_CHECKPOINT_100_DIR="${MERGED_CHECKPOINT_100_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_checkpoint_100_merged}"
MERGED_CHECKPOINT_150_DIR="${MERGED_CHECKPOINT_150_DIR:-$SCRATCH/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_checkpoint_150_merged}"

mkdir -p "$DATA_DIR" "$RUN_DIR"

python "$D2TPATH/tripler/finetune/build_dataset.py" \
    --input "$INPUT_FILE" \
    --triples "$TRIPLES_FILE" \
    --out-dir "$DATA_DIR" \
    --base-id "$BASE_ID" \
    --top-level-key forecasts \
    --holdout 200 --seed 13

python "$D2TPATH/tripler/finetune/train_qlora.py" \
    --base-id "$BASE_ID" \
    --train "$DATA_DIR/train.jsonl" \
    --dev "$DATA_DIR/dev.jsonl" \
    --out "$ADAPTER_DIR" \
    --epochs "$TRAIN_EPOCHS" --lr "$TRAIN_LR" --warmup-ratio "$TRAIN_WARMUP_RATIO" \
    --max-len 6144 --lora-r "$TRAIN_LORA_R" --lora-alpha "$TRAIN_LORA_ALPHA" \
    --lora-dropout "$TRAIN_LORA_DROPOUT" --weight-decay "$TRAIN_WEIGHT_DECAY" \
    --bs 1 --grad-accum 16 --seed 13

python "$D2TPATH/tripler/finetune/merge_adapter.py" \
    --base-id "$BASE_ID" \
    --adapter "$ADAPTER_DIR" \
    --out "$MERGED_DIR" \
    --dtype bfloat16

merge_checkpoint() {
    local checkpoint_dir="$1"
    local merged_dir="$2"
    test -f "$checkpoint_dir/adapter_config.json" || {
        echo "ERROR: missing adapter checkpoint: $checkpoint_dir" >&2
        exit 1
    }
    python "$D2TPATH/tripler/finetune/merge_adapter.py" \
        --base-id "$BASE_ID" \
        --adapter "$checkpoint_dir" \
        --out "$merged_dir" \
        --dtype bfloat16
}

merge_checkpoint "$CHECKPOINT_100_DIR" "$MERGED_CHECKPOINT_100_DIR"
merge_checkpoint "$CHECKPOINT_150_DIR" "$MERGED_CHECKPOINT_150_DIR"

echo "FINETUNE DONE experiment=$EXPERIMENT merged=$MERGED_DIR checkpoint100=$MERGED_CHECKPOINT_100_DIR checkpoint150=$MERGED_CHECKPOINT_150_DIR"
