#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
#SBATCH --time=48:00:00
set -eo pipefail

source "$D2TPATH/tripler/finetune/scripts/put_eval_runtime.sh"
put_eval_setup
put_eval_check_conda

test -d "$D2TPATH/problems/triples_to_text" || {
    echo "ERROR: D2TPATH is not accessible: $D2TPATH" >&2
    exit 1
}

SERVER_LOG_DEST="${SERVER_LOG_DEST:-$HOME/vllm-server1.log}"
SERVER_LOG1="$(put_eval_log_path vllm-server1)"
export PUT_EVAL_LOG_SOURCE="$SERVER_LOG1" PUT_EVAL_LOG_DEST="$SERVER_LOG_DEST"
WRAPPER_LOG="$PUT_EVAL_ROOT/logs/batch-wrapper.log"

export CUDA_HOME=/usr/local/cuda
export PATH="$CUDA_HOME/bin:$PATH"
export CPATH="$CUDA_HOME/include:$CPATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
export VLLM_USE_FLASHINFER_SAMPLER=0
export PYTHONPATH="$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"

VLLM_USE_FLASHINFER_SAMPLER=0 put_vllm_run vllm serve \
	RedHatAI/gemma-4-31B-it-NVFP4 \
    --port {port_1} \
    --max-model-len 60K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

cleanup() {
    for pid in "${WRAPPER_PID:-}" "${SERVER_PID1:-}"; do
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            wait "$pid" 2>/dev/null || true
        fi
    done
}
trap 'cleanup; put_eval_cleanup' EXIT

if ! put_openevolve_run "$D2TPATH/.conda/test-response.py" --port {port_1} --timeout 600; then
    echo "ERROR: vLLM server did not become ready; see $SERVER_LOG_DEST" >&2
    exit 1
fi

put_openevolve_run "$D2TPATH/tripler/batch_wrapper_server.py" \
    --upstream-base-url http://localhost:{port_1} \
    --port {port_0} \
    --storage-dir "$PUT_EVAL_ROOT/batch_wrapper_data" \
    > "$WRAPPER_LOG" 2>&1 &
WRAPPER_PID=$!

if ! put_openevolve_run "$D2TPATH/.conda/test-response.py" --port {port_0} --timeout 300; then
    echo "ERROR: batch wrapper did not become ready; see $WRAPPER_LOG" >&2
    exit 1
fi

cd "$D2TPATH/problems/triples_to_text"
export WEBNLG_BASE_PATH="$D2TPATH/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export WEBNLG_DOMAIN={domain}
export CONFIG_PATH="$(pwd)/outputs/{evolution_config}/${WEBNLG_DOMAIN}_output/config_remote.yaml"
CHECKPOINT_ROOT="./outputs/{evolution_config}/${WEBNLG_DOMAIN}_output/openevolve_output/checkpoints"
LATEST_CHECKPOINT=""

if [ -d "${CHECKPOINT_ROOT}" ]; then
	LATEST_CHECKPOINT=$(find "${CHECKPOINT_ROOT}" -maxdepth 1 -mindepth 1 -type d -name "checkpoint_*" | sort -V | tail -n 1)
fi

CHECKPOINT_ARG=()
if [ -n "${LATEST_CHECKPOINT}" ]; then
	CHECKPOINT_ARG=(--checkpoint "${LATEST_CHECKPOINT}")
fi

put_openevolve_run ../../openevolve/openevolve-run.py initial_program.py evaluator.py \
    --config "$CONFIG_PATH" "${CHECKPOINT_ARG[@]}" \
    --output ./outputs/{evolution_config}/${WEBNLG_DOMAIN}_output/openevolve_output

cd "./outputs/{evolution_config}/${WEBNLG_DOMAIN}_output"
put_openevolve_run ../../../plot_results.py
export BEST_PROGRAM_PATH="./openevolve_output/best/best_program.py"
export LLM_JUDGES="[{\"name\": \"themis\", \"structured\": true, \"base_url\": \"http://localhost:{port_0}/v1\", \"api_key\": \"AiIsMyLife25\"}]"
put_openevolve_run ../../../final_test.py
