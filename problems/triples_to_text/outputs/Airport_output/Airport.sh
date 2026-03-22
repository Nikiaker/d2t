#!/bin/bash
#SBATCH -w hgx2
#SBATCH -p hgx
#SBATCH -c4
#SBATCH --gres=gpu:4
#SBATCH -n1
SERVER_LOG1="/home/inf151915/vllm-server1.log"
SERVER_LOG2="/home/inf151915/vllm-server2.log"
SERVER_LOG3="/home/inf151915/vllm-server3.log"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	openai/gpt-oss-120b \
    --port 2993 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2993

CUDA_VISIBLE_DEVICES=1,2 \
conda run -n vllm-env vllm serve \
	Qwen/Qwen3.5-122B-A10B-FP8 \
    --port 2994 \
    --reasoning-parser qwen3 \
    --language-model-only \
    --tensor-parallel-size 2 \
    > "$SERVER_LOG2" 2>&1 &
SERVER_PID2=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2994

CUDA_VISIBLE_DEVICES=3 \
conda run -n vllm-env vllm serve \
	PKU-ONELab/Themis \
    --port 2995 \
    --chat-template ~/d2t/jinja/llama.jinja \
    > "$SERVER_LOG3" 2>&1 &
SERVER_PID3=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2995

cd ~/d2t/problems/triples_to_text
export WEBNLG_BASE_PATH="/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export WEBNLG_DOMAIN=Airport
export CONFIG_PATH="./outputs/${WEBNLG_DOMAIN}_output/config_remote.yaml"
conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config ${CONFIG_PATH} --output ./outputs/${WEBNLG_DOMAIN}_output/openevolve_output

cd ./outputs/${WEBNLG_DOMAIN}_output
conda run -n openevolve-env python ../../plot_results.py
export BEST_PROGRAM_PATH="./openevolve_output/best/best_program.py"
conda run -n openevolve-env python ../../final_test.py