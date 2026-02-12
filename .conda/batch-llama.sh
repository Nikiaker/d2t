#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH --gres=gpu:1
#SBATCH -n1
SERVER_LOG="/home/inf151915/vllm-server.log"
conda run -n vllm-env vllm serve \
	RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic \
    --port 2993 \
    --api-key AiIsMyLife25 \
    --gpu-memory-utilization 0.99 \
    --kv-cache-memory=8000000000 \
    --max-model-len 16000 \
    > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py

cd ~/d2t/problems/triples_to_text
export WEBNLG_BASE_PATH="/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config config_remote.yaml