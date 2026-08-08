#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:2
#SBATCH --time=48:00:00
DOMAIN="owid"
TRIPLE_DOMAIN="owid"
SERVER_LOG1="$HOME/vllm-server_${DOMAIN}.log"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"
conda activate finetune-env

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"

BASE_ID="${BASE_ID:-google/gemma-4-31B-it}"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test11/${TRIPLE_DOMAIN}/joined.json}"
REPORT="$D2TPATH/tripler/finetune/runs/${DOMAIN}/eval_report.json"
MERGED_DIR="${MERGED_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b_merged}"
PORT="${PORT:-2999}"

VLLM_USE_FLASHINFER_SAMPLER=0 \
conda run -n vllm-env vllm serve \
	$MERGED_DIR \
    --port $PORT \
    --tensor-parallel-size 2 \
    --max-model-len 8192 \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port $PORT --timeout 300
if [ $? -ne 0 ]; then
    echo "ERROR: vLLM server 1 (gemma) did not start within 5 minutes. Canceling." >&2
    exit 1
fi

python "$D2TPATH/tripler/finetune/eval.py" \
    --dev "$DATA_DIR/dev.jsonl" \
    --report "$REPORT" \
    --port "$PORT" \
    --api-key none \
    --max-tokens 2048 \
    --tp 2 \
    --model base "$BASE_ID" \
    --model ft "$MERGED_DIR" \
    --catalog "$TRIPLES_FILE"

echo "EVAL DONE report=$REPORT"