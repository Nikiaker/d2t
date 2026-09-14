#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1

set -euo pipefail

SERVER_LOG="$HOME/vllm-server-sequential.log"
WRAPPER_LOG="$HOME/batch-wrapper-sequential.log"
SERVER_PID=""
WRAPPER_PID=""
JUDGE_API_KEY="${LLM_JUDGE_API_KEY:-local}"

cleanup() {
    for pid in "${WRAPPER_PID:-}" "${SERVER_PID:-}"; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
        fi
    done

    for pid in "${WRAPPER_PID:-}" "${SERVER_PID:-}"; do
        if [ -n "$pid" ]; then
            wait "$pid" 2>/dev/null || true
        fi
    done

    SERVER_PID=""
    WRAPPER_PID=""
}

trap cleanup EXIT

run_evaluation() {
    local judge_config="$1"
    local storage_dir="$2"
    local reset_scores="${3:-}"

    conda run -n openevolve-env python "$D2TPATH/tripler/batch_wrapper_server.py" \
        --upstream-base-url http://localhost:2993 \
        --port 2996 \
        --storage-dir "$storage_dir" \
        > "$WRAPPER_LOG" 2>&1 &
    WRAPPER_PID=$!

    export LLM_JUDGES="$judge_config"
    if [ "$reset_scores" = "reset" ]; then
        export FINAL_TEST_MERGE_RESET=1
    else
        unset FINAL_TEST_MERGE_RESET
    fi
    conda run -n openevolve-env python run_final_test_for_configs.py outputs/ 2 \
        --final-test final_test_merge.py

    cleanup
}

export CUDA_HOME=/usr/local/cuda
export PATH="$CUDA_HOME/bin:$PATH"
export CPATH="$CUDA_HOME/include:${CPATH:-}"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export LD_LIBRARY_PATH="${CONDA_PREFIX:-}/lib:$LD_LIBRARY_PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0
export WEBNLG_BASE_PATH="$D2TPATH/problems/triples_to_text/tests/webnlg/release_v3.0/en/"

cd "$D2TPATH/problems/triples_to_text"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
    google/gemma-4-31B-it \
    --port 2993 \
    --max-model-len 100K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python "$D2TPATH/.conda/test-response.py" --port 2993
run_evaluation \
    "[{\"name\": \"google/gemma-4-31B-it\", \"structured\": true, \"base_url\": \"http://localhost:2996/v1\", \"api_key\": \"$JUDGE_API_KEY\"}]" \
    "$HOME/.batch_wrapper_data_gemma" \
    reset

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
    Qwen/Qwen3.6-35B-A3B-FP8 \
    --port 2993 \
    --max-model-len 100K \
    --reasoning-parser qwen3 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --language-model-only \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python "$D2TPATH/.conda/test-response.py" --port 2993
run_evaluation \
    "[{\"name\": \"Qwen/Qwen3.6-35B-A3B-FP8\", \"structured\": true, \"base_url\": \"http://localhost:2996/v1\", \"api_key\": \"$JUDGE_API_KEY\"}]" \
    "$HOME/.batch_wrapper_data_qwen"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
    PKU-ONELab/Themis \
    --chat-template "$D2TPATH/jinja/llama.jinja" \
    --port 2993 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python "$D2TPATH/.conda/test-response.py" --port 2993
run_evaluation \
    "[{\"name\": \"PKU-ONELab/Themis\", \"structured\": false, \"base_url\": \"http://localhost:2996/v1\", \"api_key\": \"$JUDGE_API_KEY\"}]" \
    "$HOME/.batch_wrapper_data_themis"

conda run -n openevolve-env python collect_scores_to_csv.py outputs/ 2
