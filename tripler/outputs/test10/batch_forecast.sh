#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG1="$HOME/vllm-server10.log"
SERVER_PID1=""
trap 'kill $SERVER_PID1 2>/dev/null' EXIT

TRIPLE_DOMAIN="weather_forecast"
TRIPLE_INPUT_FILE="$D2TPATH/tripler/inputs/openweather_dev.json"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	google/gemma-4-31B-it \
    --port 3009 \
    --max-model-len 30K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port 3009 --timeout 300
if [ $? -ne 0 ]; then
    echo "ERROR: vLLM server 1 (gemma) did not start within 5 minutes. Canceling." >&2
    exit 1
fi

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:3009 \
    --port 3008 \
    --storage-dir $SCRATCH/.batch_wrapper_data10 \
	2>&1 &

cd $D2TPATH/tripler/
mkdir -p outputs/test10/${TRIPLE_DOMAIN}

conda run -n openevolve-env python app_text_pipeline.py extract \
  --input "$TRIPLE_INPUT_FILE" \
  --output outputs/test10/${TRIPLE_DOMAIN}/extracted_triples_text_pipeline.json \
  --model google/gemma-4-31B-it \
  --base-url http://localhost:3008/v1 \
  --api-key none \
  --top-level-key forecasts

conda run -n openevolve-env python app_rules_text_pipeline.py \
  --input "$TRIPLE_INPUT_FILE" \
  --output outputs/test10/${TRIPLE_DOMAIN}/extracted_triples_rules_text_pipeline.json \
  --domain ${TRIPLE_DOMAIN} \
  --model google/gemma-4-31B-it \
  --base-url http://localhost:3008/v1 \
  --api-key none \
  --top-level-key forecasts

conda run -n openevolve-env python app_text_predicate_catalog_stable.py \
  --input "$TRIPLE_INPUT_FILE" \
  --output outputs/test10/${TRIPLE_DOMAIN}/extracted_triples_text_predicate_catalog_stable.json \
  --model google/gemma-4-31B-it \
  --base-url http://localhost:3008/v1 \
  --api-key none \
  --top-level-key forecasts \
  --stable-window 20