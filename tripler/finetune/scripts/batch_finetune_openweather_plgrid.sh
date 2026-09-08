#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -n1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:2
#SBATCH --time=48:00:00
set -eo pipefail
source "$D2TPATH/tripler/finetune/scripts/put_eval_runtime.sh"
put_finetune_setup
trap put_finetune_cleanup EXIT
put_finetune_check_conda

export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
DOMAIN="openweather"
DOMAIN_SEED="2993"
TRIPLE_DOMAIN="weather_forecast"
EXPERIMENT="${EXPERIMENT:-baseline}"

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
source "$D2TPATH/tripler/finetune/experiments.sh"
configure_experiment "$EXPERIMENT"

BASE_ID="google/gemma-4-31B-it"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
INPUT_FILE="${INPUT_FILE:-$D2TPATH/tripler/inputs/seed_${DOMAIN_SEED}/${DOMAIN}_dev_${DOMAIN_SEED}.json}"
if [ "$EXPERIMENT" = "baseline" ]; then
    PERSISTENT_RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}"
    LOCAL_RUN_DIR="$PUT_FINETUNE_ROOT/runs/${DOMAIN}"
    EXPERIMENT_SUFFIX=""
else
    PERSISTENT_RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}/${EXPERIMENT}"
    LOCAL_RUN_DIR="$PUT_FINETUNE_ROOT/runs/${DOMAIN}/${EXPERIMENT}"
    EXPERIMENT_SUFFIX="_${EXPERIMENT}"
fi
PERSISTENT_DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
DATA_DIR="$PUT_FINETUNE_ROOT/datasets/${DOMAIN}"
RUN_DIR="$LOCAL_RUN_DIR"
ADAPTER_DIR="$RUN_DIR/adapter"
MERGED_DIR="${MERGED_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_merged}"
LOCAL_MERGED_DIR="$PUT_FINETUNE_ROOT/models/$(basename "$MERGED_DIR")"
CHECKPOINT_100_DIR="$RUN_DIR/checkpoint-100"
CHECKPOINT_150_DIR="$RUN_DIR/checkpoint-150"
MERGED_CHECKPOINT_100_DIR="${MERGED_CHECKPOINT_100_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_checkpoint_100_merged}"
MERGED_CHECKPOINT_150_DIR="${MERGED_CHECKPOINT_150_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_checkpoint_150_merged}"
LOCAL_MERGED_CHECKPOINT_100_DIR="$PUT_FINETUNE_ROOT/models/$(basename "$MERGED_CHECKPOINT_100_DIR")"
LOCAL_MERGED_CHECKPOINT_150_DIR="$PUT_FINETUNE_ROOT/models/$(basename "$MERGED_CHECKPOINT_150_DIR")"

mkdir -p "$DATA_DIR" "$RUN_DIR"

put_finetune_run python "$D2TPATH/tripler/finetune/build_dataset.py" \
    --input "$INPUT_FILE" \
    --triples "$TRIPLES_FILE" \
    --out-dir "$DATA_DIR" \
    --base-id "$BASE_ID" \
    --top-level-key forecasts \
    --holdout 200 --seed 13

put_finetune_run python "$D2TPATH/tripler/finetune/train_qlora.py" \
    --base-id "$BASE_ID" \
    --train "$DATA_DIR/train.jsonl" \
    --dev "$DATA_DIR/dev.jsonl" \
    --out "$ADAPTER_DIR" \
    --epochs "$TRAIN_EPOCHS" --lr "$TRAIN_LR" --warmup-ratio "$TRAIN_WARMUP_RATIO" \
    --max-len 6144 --lora-r "$TRAIN_LORA_R" --lora-alpha "$TRAIN_LORA_ALPHA" \
    --lora-dropout "$TRAIN_LORA_DROPOUT" --weight-decay "$TRAIN_WEIGHT_DECAY" \
    --bs 1 --grad-accum 16 --seed 13

put_finetune_run python "$D2TPATH/tripler/finetune/merge_adapter.py" \
    --base-id "$BASE_ID" \
    --adapter "$ADAPTER_DIR" \
    --out "$LOCAL_MERGED_DIR" \
    --dtype bfloat16

merge_checkpoint() {
    local checkpoint_dir="$1"
    local merged_dir="$2"
    test -f "$checkpoint_dir/adapter_config.json" || {
        echo "ERROR: missing adapter checkpoint: $checkpoint_dir" >&2
        exit 1
    }
    put_finetune_run python "$D2TPATH/tripler/finetune/merge_adapter.py" \
        --base-id "$BASE_ID" \
        --adapter "$checkpoint_dir" \
        --out "$merged_dir" \
        --dtype bfloat16
}

merge_checkpoint "$CHECKPOINT_100_DIR" "$LOCAL_MERGED_CHECKPOINT_100_DIR"
merge_checkpoint "$CHECKPOINT_150_DIR" "$LOCAL_MERGED_CHECKPOINT_150_DIR"

put_publish_dir "$DATA_DIR" "$PERSISTENT_DATA_DIR"
put_publish_dir "$ADAPTER_DIR" "$PERSISTENT_RUN_DIR/adapter"
put_publish_dir "$CHECKPOINT_100_DIR" "$PERSISTENT_RUN_DIR/checkpoint-100"
put_publish_dir "$CHECKPOINT_150_DIR" "$PERSISTENT_RUN_DIR/checkpoint-150"
put_publish_dir "$LOCAL_MERGED_DIR" "$MERGED_DIR"
put_publish_dir "$LOCAL_MERGED_CHECKPOINT_100_DIR" "$MERGED_CHECKPOINT_100_DIR"
put_publish_dir "$LOCAL_MERGED_CHECKPOINT_150_DIR" "$MERGED_CHECKPOINT_150_DIR"

echo "FINETUNE DONE experiment=$EXPERIMENT merged=$MERGED_DIR checkpoint100=$MERGED_CHECKPOINT_100_DIR checkpoint150=$MERGED_CHECKPOINT_150_DIR"
