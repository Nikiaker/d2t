#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG="/home/inf151915/vllm-server.log"
conda run -n vllm-env vllm serve \
	google/gemma-3-27b-it \
    --port 2993 \
    --api-key AiIsMyLife25 \
    --kv-cache-memory=24778935644 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py

cd ~/d2t/problems/circle_packing_with_artifacts
conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config config_remote.yaml