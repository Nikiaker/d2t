#!/bin/bash
#SBATCH -p plgrid-gpu-a100
#SBATCH -A plgnarnlg-gpu-a100
#SBATCH -n 1
#SBATCH -N 1
#SBATCH -c16
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --time=48:00:00
SERVER_LOG1="$HOME/vllm-server1.log"

module load CUDA/12.8.0
module load Miniconda3
eval "$(conda shell.bash hook)"
export PYTHONPATH=$D2TPATH/openevolve/:$D2TPATH/problems/triples_to_text/tests/benchmark_reader/:$D2TPATH/problems/triples_to_text/:$PYTHONPATH

#export CUDA_HOME=/usr/local/cuda
#export PATH="$CUDA_HOME/bin:$PATH"
#export CPATH="$CUDA_HOME/include:$CPATH"
#export LD_LIBRARY_PATH="$CUDA_HOME/lib64:$LD_LIBRARY_PATH"
#export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:$LD_LIBRARY_PATH"

conda run -n vllm-env vllm serve \
	RedHatAI/gemma-4-31B-it-NVFP4 \
    --port {port_1} \
    --max-model-len 60K \
    --reasoning-parser gemma4 \
    --default-chat-template-kwargs '{"enable_thinking": false}' \
    --max-num-batched-tokens 4096 \
    --gpu-memory-utilization 0.95 \
    > "$SERVER_LOG1" 2>&1 &
SERVER_PID1=$!

conda run -n openevolve-env python $D2TPATH/.conda/test-response.py --port {port_1}

conda run -n openevolve-env python $D2TPATH/tripler/batch_wrapper_server.py \
    --upstream-base-url http://localhost:{port_1} \
    --port {port_0} \
    --storage-dir ~/.batch_wrapper_data \
	2>&1 &

cd $D2TPATH/problems/triples_to_text
export WEBNLG_BASE_PATH="$D2TPATH/problems/triples_to_text/tests/webnlg/release_v3.0/en/"
export WEBNLG_DOMAIN={domain}
export CONFIG_PATH="$(pwd)/outputs/{evolution_config}/${WEBNLG_DOMAIN}_output/config_remote.yaml"
CHECKPOINT_ROOT="./outputs/{evolution_config}/${WEBNLG_DOMAIN}_output/openevolve_output/checkpoints"
LATEST_CHECKPOINT=""

if [ -d "${CHECKPOINT_ROOT}" ]; then
	LATEST_CHECKPOINT=$(find "${CHECKPOINT_ROOT}" -maxdepth 1 -mindepth 1 -type d -name "checkpoint_*" | sort -V | tail -n 1)
fi

CHECKPOINT_ARG=()
if [ -n "${LATEST_CHECKPOINT}" ]; then
	CHECKPOINT_ARG=(--checkpoint "${LATEST_CHECKPOINT}")
fi

conda run -n openevolve-env python ../../openevolve/openevolve-run.py initial_program.py evaluator.py --config ${CONFIG_PATH} "${CHECKPOINT_ARG[@]}" --output ./outputs/{evolution_config}/${WEBNLG_DOMAIN}_output/openevolve_output

cd ./outputs/{evolution_config}/${WEBNLG_DOMAIN}_output
conda run -n openevolve-env python ../../../plot_results.py
export BEST_PROGRAM_PATH="./openevolve_output/best/best_program.py"
export LLM_JUDGES="[{\"name\": \"themis\", \"structured\": true, \"base_url\": \"http://localhost:{port_0}/v1\", \"api_key\": \"AiIsMyLife25\"}]"
conda run -n openevolve-env python ../../../final_test.py