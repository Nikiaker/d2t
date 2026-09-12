#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -n1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --array=0-7

set -euo pipefail

: "${D2TPATH:?D2TPATH must point to the repository root}"

source "$D2TPATH/tripler/finetune/scripts/put_eval_runtime.sh"
put_eval_setup
put_eval_check_conda

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:${PYTHONPATH:-}"
export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export VLLM_USE_FLASHINFER_SAMPLER=0

DOMAINS=(gsmarena gsmarena openweather openweather owid owid wikidata wikidata)
SPLITS=(dev test dev test dev test dev test)
TOP_LEVEL_KEYS=(none none forecasts forecasts none none none none)
CATEGORIES=(Gsmarena Gsmarena Openweather Openweather Owid Owid Wikidata Wikidata)

TASK_ID="${SLURM_ARRAY_TASK_ID:-0}"
DOMAIN="${DOMAINS[$TASK_ID]}"
SPLIT="${SPLITS[$TASK_ID]}"
TOP_LEVEL_KEY="${TOP_LEVEL_KEYS[$TASK_ID]}"
CATEGORY="${CATEGORIES[$TASK_ID]}"

OUTPUT_ROOT="${OUTPUT_ROOT:-$D2TPATH/tripler/outputs/webnlg_seed_2994}"
WEBNLG_ROOT="${WEBNLG_ROOT:-$OUTPUT_ROOT/webnlg/release_v3.0/en}"
INPUT_FILE="${INPUT_FILE:-$D2TPATH/tripler/inputs/seed_2994/${DOMAIN}_${SPLIT}_2994.json}"
OUTPUT_FILE="${OUTPUT_FILE:-$OUTPUT_ROOT/json/${DOMAIN}_${SPLIT}_2994.json}"
MODEL_DIR="${MODEL_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b_regularized_capacity_merged}"

# Array tasks can share a node, so every task gets a deterministic port pair.
UPSTREAM_PORT="${UPSTREAM_PORT:-$((3100 + TASK_ID * 2))}"
WRAPPER_PORT="${WRAPPER_PORT:-$((UPSTREAM_PORT + 1))}"
SERVER_LOG_DEST="${SERVER_LOG:-$OUTPUT_ROOT/logs/${DOMAIN}_${SPLIT}_vllm.log}"
mkdir -p "$(dirname "$SERVER_LOG_DEST")" "$(dirname "$OUTPUT_FILE")"
SERVER_LOG="$(put_eval_log_path vllm-${DOMAIN}-${SPLIT})"
export PUT_EVAL_LOG_SOURCE="$SERVER_LOG" PUT_EVAL_LOG_DEST="$SERVER_LOG_DEST"

LOCAL_MODEL_DIR="$(put_stage_model "$MODEL_DIR")"

VLLM_USE_FLASHINFER_SAMPLER=0 \
put_vllm_run serve "$LOCAL_MODEL_DIR" \
    --port "$UPSTREAM_PORT" \
    --api-key none \
    --tensor-parallel-size 1 \
    --max-model-len "${MAX_MODEL_LEN:-16384}" \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens "${MAX_NUM_BATCHED_TOKENS:-4096}" \
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION:-0.95}" \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

WRAPPER_LOG="$(put_eval_log_path batch-wrapper-${DOMAIN}-${SPLIT})"
put_openevolve_run "$D2TPATH/tripler/batch_wrapper_server.py" \
    --upstream-base-url "http://localhost:$UPSTREAM_PORT" \
    --port "$WRAPPER_PORT" \
    --storage-dir "$PUT_EVAL_ROOT/batch_wrapper_data" \
    > "$WRAPPER_LOG" 2>&1 &
WRAPPER_PID=$!

cleanup() {
    if kill -0 "${WRAPPER_PID:-}" 2>/dev/null; then
        kill "$WRAPPER_PID" 2>/dev/null || true
        wait "$WRAPPER_PID" 2>/dev/null || true
    fi
    if kill -0 "${SERVER_PID:-}" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    put_eval_cleanup
}
trap cleanup EXIT

if ! put_openevolve_run "$D2TPATH/.conda/test-response.py" \
    --port "$UPSTREAM_PORT" --timeout 600; then
    echo "ERROR: vLLM server did not start; see $SERVER_LOG" >&2
    exit 1
fi

wrapper_ready=0
for _ in $(seq 1 60); do
    if put_openevolve_run -c \
        "import urllib.request; urllib.request.urlopen('http://localhost:$WRAPPER_PORT/health', timeout=2).read()" \
        >/dev/null 2>&1; then
        wrapper_ready=1
        break
    fi
    sleep 1
done
if [ "$wrapper_ready" -ne 1 ]; then
    echo "ERROR: batch wrapper did not start; see $WRAPPER_LOG" >&2
    exit 1
fi

put_openevolve_run "$D2TPATH/tripler/finetune/generate_webnlg.py" \
    --input "$INPUT_FILE" \
    --output "$OUTPUT_FILE" \
    --model "$LOCAL_MODEL_DIR" \
    --base-url "http://localhost:$WRAPPER_PORT/v1" \
    --api-key none \
    --top-level-key "$TOP_LEVEL_KEY" \
    --max-tokens "${MAX_TOKENS:-2048}" \
    --batch-size "${BATCH_SIZE:-0}" \
    --batch-timeout-seconds "${BATCH_TIMEOUT_SECONDS:-21600}"

put_openevolve_run "$D2TPATH/tripler/prepare_webnlg_xml.py" \
    --input "$OUTPUT_FILE" \
    --output-root "$WEBNLG_ROOT" \
    --category "$CATEGORY" \
    --split "$SPLIT"

echo "WEBNLG GENERATION DONE domain=$DOMAIN split=$SPLIT json=$OUTPUT_FILE webnlg=$WEBNLG_ROOT"
