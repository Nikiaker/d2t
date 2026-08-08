#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=128G
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
SERVER_LOG1="$HOME/vllm-server1.log"
SERVER_LOG2="$HOME/vllm-server2.log"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"
export PYTHONPATH=$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH

TRIPLE_DOMAIN="mobile_phone_specification"
TRIPLE_INPUT_FILE="$D2TPATH/tripler/inputs/seed_2993/gsmarena_dev_2993.json"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	RedHatAI/gemma-4-31B-it-NVFP4 \
    --port 3005 \
    --max-model-len 60K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port 3005 --timeout 300
if [ $? -ne 0 ]; then
    echo "ERROR: vLLM server 1 (gemma) did not start within 5 minutes. Canceling." >&2
    exit 1
fi

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:3005 \
    --port 3004 \
    --storage-dir $HOME/.batch_wrapper_data12 \
	2>&1 &

cd $D2TPATH/tripler/
mkdir -p outputs/test11/${TRIPLE_DOMAIN}

conda run -n openevolve-env python app_text_pipeline.py extract \
  --input "$TRIPLE_INPUT_FILE" \
  --output outputs/test11/${TRIPLE_DOMAIN}/extracted_triples_text_pipeline.json \
  --model RedHatAI/gemma-4-31B-it-NVFP4 \
  --base-url http://localhost:3004/v1 \
  --api-key none \
  --top-level-key none

conda run -n openevolve-env python app_text_pipeline.py normalize \
  --input  outputs/test11/${TRIPLE_DOMAIN}/extracted_triples_text_pipeline.json \
  --output outputs/test11/${TRIPLE_DOMAIN}/normalized_triples.json \
  --model RedHatAI/gemma-4-31B-it-NVFP4 \
  --base-url http://localhost:3004/v1 \
  --api-key none \
  --batch-timeout-seconds 21600

conda run -n openevolve-env python $D2TPATH/scripts/join_extract_normalize.py \
  --extract   outputs/test11/${TRIPLE_DOMAIN}/extracted_triples_text_pipeline.json \
  --normalize outputs/test11/${TRIPLE_DOMAIN}/normalized_triples.json \
  --output    outputs/test11/${TRIPLE_DOMAIN}/joined.json \
  --input "$TRIPLE_INPUT_FILE" \
  --top-level-key none