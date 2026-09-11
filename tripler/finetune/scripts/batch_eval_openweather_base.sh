#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -n1
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
set -eo pipefail
source "$D2TPATH/tripler/finetune/scripts/put_eval_runtime.sh"
put_eval_setup
put_eval_check_conda
DOMAIN="openweather"
TRIPLE_DOMAIN="weather_forecast"
EXPERIMENT="${EXPERIMENT:-baseline}"

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"
source "$D2TPATH/tripler/finetune/experiments_old.sh"
configure_experiment "$EXPERIMENT"

BASE_ID="${BASE_ID:-google/gemma-4-31B-it}"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
if [ "$EXPERIMENT" = "baseline" ]; then
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}"
else
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}/${EXPERIMENT}"
fi
REPORT="${REPORT:-$RUN_DIR/eval_report_base.json}"
PORT="${PORT:-2998}"
SERVER_LOG_DEST="${SERVER_LOG:-$RUN_DIR/vllm-base.log}"
SERVER_LOG="$(put_eval_log_path vllm-base)"
export PUT_EVAL_LOG_SOURCE="$SERVER_LOG" PUT_EVAL_LOG_DEST="$SERVER_LOG_DEST"

mkdir -p "$RUN_DIR"
VLLM_USE_FLASHINFER_SAMPLER=0 \
put_vllm_run serve "$BASE_ID" \
    --port "$PORT" --api-key none --tensor-parallel-size 1 \
    --max-model-len 16K --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

cleanup() {
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap 'cleanup; put_eval_cleanup' EXIT

if ! put_openevolve_run "$D2TPATH/.conda/test-response.py" --port "$PORT" --timeout 600; then
    echo "ERROR: vLLM server did not start within 10 minutes; see $SERVER_LOG" >&2
    exit 1
fi

put_openevolve_run "$D2TPATH/tripler/finetune/eval.py" \
    --train "$DATA_DIR/train.jsonl" --dev "$DATA_DIR/dev.jsonl" \
    --report "$REPORT" --port "$PORT" --api-key none --max-tokens 2048 \
    --model base "$BASE_ID" --catalog "$TRIPLES_FILE"

echo "EVAL DONE report=$REPORT"
