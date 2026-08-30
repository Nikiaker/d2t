#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
#SBATCH --time=48:00:00
#SBATCH --array=0-4

set -euo pipefail

: "${D2TPATH:?D2TPATH must point to the repository root}"

# module load CUDA/12.8.0
# module load Miniconda3
# eval "$(conda shell.bash hook)"

export CUDA_HOME=/usr/local/cuda
export PATH="$CUDA_HOME/bin:$PATH"
export CPATH="$CUDA_HOME/include:$CPATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0

DOMAINS=(
    "ice_hockey_match"
    "mobile_phone_specification"
    "owid"
    "weather_forecast"
    "wikidata"
)

TASK_ID="${SLURM_ARRAY_TASK_ID:-0}"
if (( TASK_ID < 0 || TASK_ID >= ${#DOMAINS[@]} )); then
    echo "Invalid SLURM_ARRAY_TASK_ID: $TASK_ID" >&2
    exit 1
fi

TRIPLE_DOMAIN="${DOMAINS[$TASK_ID]}"
EXTRACTION_FILE="$D2TPATH/tripler/outputs/test10/$TRIPLE_DOMAIN/extracted_triples_text_pipeline.json"
NORMALIZATION_FILE="$D2TPATH/tripler/outputs/test10/$TRIPLE_DOMAIN/normalized_triples.json"
MODEL="google/gemma-4-31B-it"

if [[ ! -f "$EXTRACTION_FILE" ]]; then
    echo "Extraction output not found: $EXTRACTION_FILE" >&2
    exit 1
fi

JOB_ID="${SLURM_ARRAY_JOB_ID:-manual}"
SERVER_PORT=$((3020 + TASK_ID * 2))
WRAPPER_PORT=$((SERVER_PORT + 1))
SERVER_LOG="$HOME/vllm-test10-normalize-${JOB_ID}-${TASK_ID}.log"
WRAPPER_LOG="$HOME/batch-wrapper-test10-normalize-${JOB_ID}-${TASK_ID}.log"
STORAGE_DIR="$HOME/.batch_wrapper_data_test10_normalize_${JOB_ID}_${TASK_ID}"
SERVER_PID=""
WRAPPER_PID=""

cleanup() {
    if [[ -n "$WRAPPER_PID" ]]; then
        kill "$WRAPPER_PID" 2>/dev/null || true
    fi
    if [[ -n "$SERVER_PID" ]]; then
        kill "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

export LD_LIBRARY_PATH="${CONDA_PREFIX:-}/lib:${LD_LIBRARY_PATH:-}"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve "$MODEL" \
    --port "$SERVER_PORT" \
    --max-model-len 60K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python "$D2TPATH/.conda/test-response.py" \
    --port "$SERVER_PORT" --timeout 300

conda run -n openevolve-env python "$D2TPATH/tripler/batch_wrapper_server.py" \
    --upstream-base-url "http://localhost:$SERVER_PORT" \
    --port "$WRAPPER_PORT" \
    --storage-dir "$STORAGE_DIR" \
    > "$WRAPPER_LOG" 2>&1 &
WRAPPER_PID=$!

cd "$D2TPATH/tripler"
mkdir -p "$(dirname "$NORMALIZATION_FILE")"

conda run -n openevolve-env python app_text_pipeline.py normalize \
    --input "$EXTRACTION_FILE" \
    --output "$NORMALIZATION_FILE" \
    --model "$MODEL" \
    --base-url "http://localhost:$WRAPPER_PORT/v1" \
    --api-key none \
    --batch-timeout-seconds 21600

echo "Normalization complete: $NORMALIZATION_FILE"
