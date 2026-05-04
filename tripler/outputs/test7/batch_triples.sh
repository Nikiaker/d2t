#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG1="/home/inf151915/vllm-server1.log"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	openai/gpt-oss-120b \
    --port 2993 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2993

conda run -n openevolve-env python ~/d2t/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2993 \
    --port 2992 \
    --storage-dir ~/.batch_wrapper_data \
	2>&1 &

cd ~/d2t/tripler/
conda run -n openevolve-env python app_rules_text_pipeline.py --input inputs/input_data_weather_dev_full.json --output outputs/test7/extracted_triples_1.json --domain "weather forecast" --model google/gemma-4-31B-it --base-url http://localhost:2993/v1 --api-key none