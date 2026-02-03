#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH --gres=gpu:2
#SBATCH -n1
SERVER_LOG1="/home/inf151915/vllm-server1.log"
SERVER_LOG2="/home/inf151915/vllm-server2.log"
SERVER_LOG3="/home/inf151915/vllm-server3.log"
SERVER_LOG4="/home/inf151915/vllm-server4.log"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	RedHatAI/gemma-3-27b-it-FP8-dynamic \
    --port 2993 \
    --api-key AiIsMyLife25 \
    --max_model_len 16000 \
    --kv-cache-memory=11000000000 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2993

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	google/codegemma-7b-it \
    --port 2994 \
    --api-key AiIsMyLife25 \
    --kv-cache-memory=11000000000 \
    --gpu-memory-utilization=0.45 \
    > "$SERVER_LOG2" 2>&1 &
SERVER_PID2=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2994

CUDA_VISIBLE_DEVICES=1 \
conda run -n vllm-env vllm serve \
	Qwen/Qwen3-30B-A3B-Instruct-2507-FP8 \
    --port 2995 \
    --api-key AiIsMyLife25 \
    --max_model_len 16000 \
    --kv-cache-memory=5000000000 \
    > "$SERVER_LOG3" 2>&1 &
SERVER_PID3=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2995

CUDA_VISIBLE_DEVICES=1 \
conda run -n vllm-env vllm serve \
	Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8 \
    --port 2996 \
    --api-key AiIsMyLife25 \
    --max_model_len 16000 \
    --kv-cache-memory=5000000000 \
    --gpu-memory-utilization=0.51 \
    > "$SERVER_LOG4" 2>&1 &
SERVER_PID4=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2996

cd ~/d2t/problems/triples_to_text
export WEBNLG_BASE_PATH="/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export WEBNLG_DOMAIN={domain}
conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config ./outputs/${WEBNLG_DOMAIN}_output/config_remote.yaml --output ./outputs/${WEBNLG_DOMAIN}_output/openevolve_output

cd ./outputs/${WEBNLG_DOMAIN}_output
conda run -n openevolve-env python ../../plot_results.py
export BEST_PROGRAM_PATH="./openevolve_output/best/best_program.py"
conda run -n openevolve-env python ../../final_test.py