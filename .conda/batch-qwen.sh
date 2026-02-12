#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG="/home/inf151915/vllm-server.log"
conda run -n vllm-env vllm serve \
	Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 \
    --port 2993 \
    --api-key AiIsMyLife25 \
    --gpu-memory-utilization 0.99 \
    --kv-cache-memory=926329180 \
    --max-model-len 16000 \
    --enforce-eager \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!