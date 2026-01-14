#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH --gres=gpu:1
#SBATCH -n1
conda run -n vllm-env vllm serve \
	google/gemma-3-27b-it \
    --port 2993 \
    --api-key AiIsMyLife25 \
    --gpu-memory-utilization 0.99 \