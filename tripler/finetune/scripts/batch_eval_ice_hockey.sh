#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
DOMAIN="ice_hockey"
TRIPLE_DOMAIN="ice_hockey_match"
SERVER_LOG1="$HOME/vllm-server_${DOMAIN}.log"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

export PYTHONPATH="$D2TPATH/tripler:$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH"

BASE_ID="${BASE_ID:-google/gemma-4-31B-it}"
DATA_DIR="$D2TPATH/tripler/finetune/datasets/${DOMAIN}"
TRIPLES_FILE="${TRIPLES_FILE:-$D2TPATH/tripler/outputs/test10/${TRIPLE_DOMAIN}/extracted_triples_text_predicate_catalog_stable.json}"
REPORT="$D2TPATH/tripler/finetune/runs/${DOMAIN}/eval_report.json"
MERGED_DIR="${MERGED_DIR:-$HOME/ft_models/${DOMAIN}_gemma4_31b_merged}"
PORT="${PORT:-2997}"

CUDA_VISIBLE_DEVICES=0 \
VLLM_USE_FLASHINFER_SAMPLER=0 \
conda run -n vllm-env vllm serve \
	$MERGED_DIR \
    --port $PORT \
    --max-model-len 30K \
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

conda run -n finetune-env python "$D2TPATH/tripler/finetune/eval.py" \
    --dev "$DATA_DIR/dev.jsonl" \
    --report "$REPORT" \
    --port "$PORT" \
    --api-key none \
    --max-tokens 2048 \
    --model base "$BASE_ID" \
    --model ft "$MERGED_DIR" \
    --catalog "$TRIPLES_FILE"

echo "EVAL DONE report=$REPORT"