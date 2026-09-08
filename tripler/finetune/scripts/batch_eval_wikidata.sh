#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
#SBATCH --time=48:00:00
set -eo pipefail
DOMAIN="wikidata"
TRIPLE_DOMAIN="wikidata"
EXPERIMENT="${EXPERIMENT:-baseline}"

export CUDA_HOME=/usr/local/cuda
export PATH="$CUDA_HOME/bin:$PATH"
export CPATH="$CUDA_HOME/include:$CPATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"
source "$D2TPATH/tripler/finetune/experiments_old.sh"
configure_experiment "$EXPERIMENT"

DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
if [ "$EXPERIMENT" = "baseline" ]; then
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}"
    EXPERIMENT_SUFFIX=""
else
    RUN_DIR="$D2TPATH/tripler/finetune/runs/${DOMAIN}/${EXPERIMENT}"
    EXPERIMENT_SUFFIX="_${EXPERIMENT}"
fi
REPORT="${REPORT:-$RUN_DIR/eval_report_ft.json}"
MERGED_DIR="${MERGED_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b${EXPERIMENT_SUFFIX}_merged}"
PORT="${PORT:-3000}"
SERVER_LOG="${SERVER_LOG:-$RUN_DIR/vllm-ft.log}"

mkdir -p "$RUN_DIR"

VLLM_USE_FLASHINFER_SAMPLER=0 \
conda run --no-capture-output -n vllm-env vllm serve "$MERGED_DIR" \
    --port "$PORT" \
    --api-key none \
    --tensor-parallel-size 1 \
    --max-model-len 8192 \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

cleanup() {
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

if ! conda run -n openevolve-env python "$D2TPATH/.conda/test-response.py" --port "$PORT" --timeout 600; then
    echo "ERROR: vLLM server did not start within 10 minutes; see $SERVER_LOG" >&2
    exit 1
fi

conda run -n openevolve-env python "$D2TPATH/tripler/finetune/eval.py" \
    --train "$DATA_DIR/train.jsonl" \
    --dev "$DATA_DIR/dev.jsonl" \
    --report "$REPORT" \
    --port "$PORT" \
    --api-key none \
    --max-tokens 2048 \
    --model ft "$MERGED_DIR" \
    --catalog "$TRIPLES_FILE"

echo "EVAL DONE report=$REPORT"
