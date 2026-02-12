#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH --gres=gpu:2
#SBATCH -n1
SERVER_LOG1="/home/inf151915/vllm-server1.log"
SERVER_LOG2="/home/inf151915/vllm-server2.log"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic \
    --port 2993 \
    --api-key AiIsMyLife25 \
    --gpu-memory-utilization 0.99 \
    --kv-cache-memory=8000000000 \
    --max-model-len 16000 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2993

CUDA_VISIBLE_DEVICES=1 \
SERVER_LOG="/home/inf151915/vllm-server.log"
conda run -n vllm-env vllm serve \
	Qwen/Qwen3-Next-80B-A3B-Instruct-FP8 \
    --port 2994 \
    --api-key AiIsMyLife25 \
    --gpu-memory-utilization 0.99 \
    --kv-cache-memory=926329180 \
    --max-model-len 16000 \
    --enforce-eager \
    > "$SERVER_LOG2" 2>&1 &
SERVER_PID2=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2994

cd ~/d2t/problems/triples_to_text
export WEBNLG_BASE_PATH="/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export WEBNLG_DOMAIN=Airport
conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config ./outputs/${WEBNLG_DOMAIN}_output/config_remote.yaml --output ./outputs/${WEBNLG_DOMAIN}_output/openevolve_output

cd ./outputs/${WEBNLG_DOMAIN}_output
conda run -n openevolve-env python ../../plot_results.py
export BEST_PROGRAM_PATH="./openevolve_output/best/best_program.py"
conda run -n openevolve-env python ../../final_test.py