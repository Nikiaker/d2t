#!/bin/bash
#SBATCH -w hgx1
#SBATCH -p hgx
#SBATCH -c16
#SBATCH --gres=gpu:3
#SBATCH -n1
SERVER_LOG1="/home/inf151915/vllm-server1.log"
SERVER_LOG2="/home/inf151915/vllm-server2.log"
SERVER_LOG3="/home/inf151915/vllm-server3.log"

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

CUDA_VISIBLE_DEVICES=0 \
conda run -n vllm-env vllm serve \
	google/gemma-4-31B-it \
    --port 2993 \
    --max-model-len 32K \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2993

CUDA_VISIBLE_DEVICES=1 \
conda run -n vllm-env vllm serve \
	openai/gpt-oss-120b \
    --port 2994 \
    --max-model-len 32K \
    > "$SERVER_LOG2" 2>&1 &
SERVER_PID2=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2994

CUDA_VISIBLE_DEVICES=2 \
conda run -n vllm-env vllm serve \
	PKU-ONELab/Themis \
    --chat-template ~/d2t/jinja/llama.jinja \
    --port 2995 \
    > "$SERVER_LOG3" 2>&1 &
SERVER_PID3=$!

conda run -n openevolve-env python ~/d2t/.conda/test-response.py --port 2995

conda run -n openevolve-env python ~/d2t/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2993 \
    --port 2996 \
    --storage-dir ~/.batch_wrapper_data1 \
	2>&1 &

conda run -n openevolve-env python ~/d2t/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2994 \
    --port 2997 \
    --storage-dir ~/.batch_wrapper_data2 \
	2>&1 &

conda run -n openevolve-env python ~/d2t/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2995 \
    --port 2998 \
    --storage-dir ~/.batch_wrapper_data3 \
	2>&1 &

export WEBNLG_BASE_PATH="/home/inf151915/d2t/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export LLM_JUDGES="[{\"name\": \"google/gemma-4-31B-it\", \"structured\": true, \"base_url\": \"http://localhost:2996/v1\", \"api_key\": \"AiIsMyLife25\"},{\"name\": \"openai/gpt-oss-120b\", \"structured\": true, \"base_url\": \"http://localhost:2997/v1\", \"api_key\": \"AiIsMyLife25\"},{\"name\": \"PKU-ONELab/Themis\", \"structured\": false, \"base_url\": \"http://localhost:2998/v1\", \"api_key\": \"AiIsMyLife25\"}]"

cd ~/d2t/problems/triples_to_text
conda run -n openevolve-env python run_final_test_for_configs.py results/slurm32/outputs/ 2
conda run -n openevolve-env python collect_scores_to_csv.py results/slurm32/outputs/ 2