#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=32G
#SBATCH --gres=gpu:5
#SBATCH --time=2:00:00
SERVER_LOG1="$HOME/vllm-server1.log"
SERVER_LOG2="$HOME/vllm-server2.log"
SERVER_LOG3="$HOME/vllm-server3.log"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"
export PYTHONPATH=$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH

#export CUDA_HOME=/usr/local/cuda
#export PATH="$CUDA_HOME/bin:$PATH"
#export CPATH="$CUDA_HOME/include:$CPATH"
#export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
#export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

CUDA_VISIBLE_DEVICES=0,1 \
conda run -n vllm-env vllm serve \
	google/gemma-4-31B-it \
    --port 2993 \
    --max-model-len 6K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port 2993

CUDA_VISIBLE_DEVICES=2,3 \
conda run -n vllm-env vllm serve \
	Qwen/Qwen3.6-35B-A3B-FP8 \
    --port 2994 \
    --max-model-len 6K \
    --reasoning-parser qwen3 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --language-model-only \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG2" 2>&1 &
SERVER_PID2=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port 2994

CUDA_VISIBLE_DEVICES=4 \
conda run -n vllm-env vllm serve \
	PKU-ONELab/Themis \
    --chat-template $D2TPATH/jinja/llama.jinja \
    --port 2995 \
    > "$SERVER_LOG3" 2>&1 &
SERVER_PID3=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port 2995

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2993 \
    --port 2996 \
    --storage-dir $HOME/.batch_wrapper_data1 \
	2>&1 &

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2994 \
    --port 2997 \
    --storage-dir $HOME/.batch_wrapper_data2 \
	2>&1 &

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:2995 \
    --port 2998 \
    --storage-dir $HOME/.batch_wrapper_data3 \
	2>&1 &

export WEBNLG_BASE_PATH="$D2TPATH/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export LLM_JUDGES="[{\"name\": \"google/gemma-4-31B-it\", \"structured\": true, \"base_url\": \"http://localhost:2996/v1\", \"api_key\": \"AiIsMyLife25\"},{\"name\": \"Qwen/Qwen3.6-35B-A3B-FP8\", \"structured\": true, \"base_url\": \"http://localhost:2997/v1\", \"api_key\": \"AiIsMyLife25\"},{\"name\": \"PKU-ONELab/Themis\", \"structured\": false, \"base_url\": \"http://localhost:2998/v1\", \"api_key\": \"AiIsMyLife25\"}]"

cd $D2TPATH/problems/triples_to_text
conda run -n openevolve-env python run_final_test_for_configs.py results/plgrid/ 2
conda run -n openevolve-env python collect_scores_to_csv.py results/plgrid/ 2