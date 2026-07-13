#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
#SBATCH --job-name=nlgfs-gemma4

# Trains nlg-from-scratch (Lango & Dusek, EMNLP 2025) rule-based NLG systems
# on the full WebNLG train split using a vLLM-served RedHatAI/gemma-4-31B-it-NVFP4.
# Produces per-category .dill program checkpoints under outputs/ for later
# apples-to-apples scoring against the openevolve systems.
#
# Prereqs (run once on a login/interactive node):
#   conda env create -f $D2TPATH/.conda/nlgfs-env.yml
#   export HF_HOME=$HOME/.cache/huggingface
#   python -c "from datasets import load_dataset; load_dataset('gem','web_nlg_en')"
#
# Then:  sbatch nlg-from-scratch/batch_train_gemma4.sh

set -euo pipefail

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"

# Repo root (script lives in nlg-from-scratch/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
D2TPATH="${D2TPATH:-$(dirname "$SCRIPT_DIR")}"
export D2TPATH

# --- HuggingFace offline cache (pre-populated on a login node) ---
export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

# --- Paths ---
mkdir -p "$SCRIPT_DIR/outputs"
SERVER_LOG="$SCRIPT_DIR/outputs/vllm-gemma4-server.log"
TRAIN_LOG="$SCRIPT_DIR/outputs/gemma4-31b.log"
OUT_PREFIX="$SCRIPT_DIR/outputs/gemma4-31b-refl"
VLLM_PORT=8881
MODEL="RedHatAI/gemma-4-31B-it-NVFP4"
API_KEY="AiIsMyLife25"

export LD_LIBRARY_PATH="${CONDA_PREFIX}/lib:${LD_LIBRARY_PATH:-}"

# --- Start vLLM server (single GPU) ---
CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
    "$MODEL" \
    --port "$VLLM_PORT" \
    --api-key "$API_KEY" \
    --max-model-len 60K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 8192 \
    --guided-decoding-backend xgrammar \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

cleanup() {
    if kill -0 "$SERVER_PID" 2>/dev/null; then
        echo "Stopping vLLM server (pid $SERVER_PID)..."
        kill "$SERVER_PID" || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# Wait until the server is ready (reuses the repo's health checker).
conda run -n nlgfs-env python "$D2TPATH/.conda/test-response.py" --port "$VLLM_PORT"

# --- Train per-category NLG systems on WebNLG train split ---
cd "$SCRIPT_DIR"
conda run -n nlgfs-env python src/idea_trainer.py \
    --backend vllm \
    --model "$MODEL" \
    --base-url "http://localhost:${VLLM_PORT}/v1" \
    --base-url-eval "http://localhost:${VLLM_PORT}/v1" \
    --api-key "$API_KEY" \
    --full \
    --config 1 \
    --maxiter 25 \
    --out-file "$OUT_PREFIX" \
    --log-file "$TRAIN_LOG"

echo "Training finished. Per-category checkpoints in $SCRIPT_DIR/outputs/gemma4-31b-refl-*"
echo "Aggregate checkpoint: $SCRIPT_DIR/outputs/gemma4-31b-refl-full"