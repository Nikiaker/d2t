#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c4
#SBATCH --gres=gpu:1
#SBATCH -n1
#SBATCH --time=48:00:00
SERVER_LOG1="$HOME/vllm-server11.log"
SERVER_PID1=""
trap 'kill $SERVER_PID1 2>/dev/null' EXIT

TRIPLE_DOMAIN="mobile_phone_specification"
TRIPLE_INPUT_FILE="$D2TPATH/tripler/inputs/seed_2993/gsmarena_dev_2993.json"

source /home/inf151915/miniconda3/bin/activate vllm-env
export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"
CUDA_VISIBLE_DEVICES=0 vllm serve \
	google/gemma-4-31B-it \
    --port 3005 \
    --max-model-len 30K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

source /home/inf151915/miniconda3/bin/activate openevolve-env
python $D2TPATH/.conda/test-response.py --port 3005 --timeout 300
if [ $? -ne 0 ]; then
    echo "ERROR: vLLM server 1 (gemma) did not start within 5 minutes. Canceling." >&2
    exit 1
fi

python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:3005 \
    --port 3004 \
    --storage-dir $HOME/.batch_wrapper_data12 \
	2>&1 &

cd $D2TPATH/tripler/
mkdir -p outputs/test11/${TRIPLE_DOMAIN}

python app_text_pipeline.py extract \
  --input "$TRIPLE_INPUT_FILE" \
  --output outputs/test11/${TRIPLE_DOMAIN}/extracted_triples_text_pipeline.json \
  --model google/gemma-4-31B-it \
  --base-url http://localhost:3004/v1 \
  --api-key none \
  --top-level-key none

python app_text_pipeline.py normalize \
  --input  outputs/test11/${TRIPLE_DOMAIN}/extracted_triples_text_pipeline.json \
  --output outputs/test11/${TRIPLE_DOMAIN}/normalized_triples.json \
  --model google/gemma-4-31B-it \
  --base-url http://localhost:3004/v1 \
  --api-key none \
  --batch-timeout-seconds 21600

python $D2TPATH/scripts/join_extract_normalize.py \
  --extract   outputs/test11/${TRIPLE_DOMAIN}/extracted_triples_text_pipeline.json \
  --normalize outputs/test11/${TRIPLE_DOMAIN}/normalized_triples.json \
  --output    outputs/test11/${TRIPLE_DOMAIN}/joined.json \
  --input "$TRIPLE_INPUT_FILE" \
  --top-level-key none