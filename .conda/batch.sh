#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG="/home/inf151915/vllm-server.log"
conda run -n vllm-env vllm serve \
	RedHatAI/Meta-Llama-3.1-70B-Instruct-FP8 \
    --port 2993 \
    --api-key AiIsMyLife25 \
    --gpu-memory-utilization 0.99 \
    --max-model-len 30000 \
    --enforce-eager \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py

kill "$SERVER_PID" 2>/dev/null