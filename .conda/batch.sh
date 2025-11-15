#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG="~/vllm-server.log"
conda run -n openevolve-env vllm serve \
	--model meta-llama/Llama-3.1-70B-Instruct \
    --port 2993 \
    --api-key AiIsMyLife25 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py

kill "$SERVER_PID" 2>/dev/null