#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
SERVER_LOG1="$HOME/vllm-server10.log"
SERVER_PID1=""
trap 'kill $SERVER_PID1 2>/dev/null' EXIT

TRIPLE_DOMAIN="mobile_phone_specification"
TRIPLE_INPUT_FILE="$D2TPATH/tripler/inputs/gsmarena_dev.json"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"
export PYTHONPATH=$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	RedHatAI/gemma-4-31B-it-NVFP4 \
    --port 2999 \
    --max-model-len 30K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port 2999 --timeout 300
if [ $? -ne 0 ]; then
    echo "ERROR: vLLM server 1 (gemma) did not start within 5 minutes. Canceling." >&2
    exit 1
fi

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2999 \
    --port 2998 \
    --storage-dir $SCRATCH/.batch_wrapper_data10 \
	2>&1 &

cd $D2TPATH/tripler/
mkdir -p outputs/test9/${TRIPLE_DOMAIN}

conda run -n openevolve-env python app_text_predicate_catalog_stable.py \
  --input "$TRIPLE_INPUT_FILE" \
  --output outputs/test9/${TRIPLE_DOMAIN}/extracted_triples_text_predicate_catalog_stable.json \
  --model RedHatAI/gemma-4-31B-it-NVFP4 \
  --base-url http://localhost:2998/v1 \
  --api-key none \
  --top-level-key none \
  --stable-window 20